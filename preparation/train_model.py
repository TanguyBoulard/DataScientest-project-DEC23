import pandas as pd
from pathlib import Path
import os

from dotenv import load_dotenv
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
import joblib
import warnings

from database.postgresql_functools import PostgresManager

warnings.filterwarnings('ignore')

if __name__ == '__main__':
    load_dotenv()
    root_path = os.getenv('ROOT_PATH')

    # Database connection
    postgres = PostgresManager()

    # Load data
    df = (pd.read_sql_table('australian_meteorology_weather', postgres.engine)
          .drop(columns=['id']))

    # Explicitly convert all column names to strings and remove any quotes
    df.columns = [str(col).strip("'\"") for col in df.columns]

    # Create target variable
    df['rain_today'] = df['rainfall'].apply(lambda x: 'yes' if x >= 1 else 'no')
    df['rain_tomorrow'] = df['rain_today'].shift(-1).apply(lambda x: 'yes' if x == 'yes' else 'no')

    # Drop rows with missing target values
    df.dropna(subset=['rain_today', 'rain_tomorrow'], inplace=True)

    # Define features and target
    X = df.drop(['rain_tomorrow', 'date'], axis=1)
    y = df['rain_tomorrow']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define columns
    numerical_columns = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_columns = X_train.select_dtypes(include=['object', 'category']).columns.tolist()

    # Preprocessing pipelines
    numerical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
    ])

    # Combine preprocessing steps
    preprocessor = ColumnTransformer([
        ('numerical', numerical_pipeline, numerical_columns),
        ('categorical', categorical_pipeline, categorical_columns)
    ])

    # Define the model
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=42))
    ])

    # Hyperparameter tuning
    param_grid = {
        'classifier__n_estimators': [100],
        'classifier__max_depth': [2],
        'classifier__min_samples_split': [2],
        'classifier__min_samples_leaf': [1]
    }

    grid_search = GridSearchCV(pipeline, param_grid, cv=5, n_jobs=-1, scoring='accuracy')

    try:
        grid_search.fit(X_train, y_train)

        # Save the best model
        best_model_pipeline = os.path.join(root_path, 'model', 'random_forest_model.joblib')
        joblib.dump(grid_search.best_estimator_, best_model_pipeline)
    except Exception as e:
        raise Exception(f"An error occurred during model training: {str(e)}")
