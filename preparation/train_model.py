import os
from typing import Tuple, List

import pandas as pd
import joblib
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer, f1_score
from imblearn.over_sampling import RandomOverSampler
from imblearn.pipeline import Pipeline as ImbPipeline
import warnings

from database.postgresql_functools import PostgresManager

warnings.filterwarnings('ignore')


def load_data(postgres: PostgresManager) -> pd.DataFrame:
    """
    Load weather data from the PostgreSQL database.

    :param postgres: PostgresManager object for database connection.
    :return: Raw weather data.
    """
    df = pd.read_sql_table('australian_meteorology_weather', postgres.engine)
    df = df.drop(columns=['id'])
    df = df.drop_duplicates()
    df.columns = [str(col).strip("'\"") for col in df.columns]
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the weather data by creating target variables.

    :param df: Raw weather data.
    :return: Preprocessed weather data
    """
    df['rain_today'] = df['rainfall'].apply(lambda x: 'yes' if x >= 1 else 'no')
    df['rain_tomorrow'] = df['rain_today'].shift(-1).apply(lambda x: 'yes' if x == 'yes' else 'no')
    return df.dropna(subset=['rain_today', 'rain_tomorrow'])


def split_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split the data into features and target, then into training and testing sets.

    :param df: Preprocessed weather data.
    :return: Tuple of X_train, X_test, y_train, y_test
    """
    X = df.drop(['rain_tomorrow', 'date'], axis=1)
    y = df['rain_tomorrow']
    return train_test_split(X, y, test_size=0.2, stratify=y)


def get_column_types(X: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """
    Identify numerical and categorical columns in the dataset.

    :param X: Input features.
    :return: Tuple of numerical and categorical column names
    """
    numerical_columns = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_columns = X.select_dtypes(include=['object', 'category']).columns.tolist()
    return numerical_columns, categorical_columns


def create_preprocessor(numerical_columns: List[str], categorical_columns: List[str]) -> ColumnTransformer:
    """
    Create a preprocessor for numerical and categorical data.

    :param numerical_columns: List of numerical column names.
    :param categorical_columns: List of categorical column names.
    :return: ColumnTransformer for preprocessing.
    """
    numerical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
    ])

    return ColumnTransformer([
        ('numerical', numerical_pipeline, numerical_columns),
        ('categorical', categorical_pipeline, categorical_columns)
    ])


def create_model_pipeline(preprocessor: ColumnTransformer) -> ImbPipeline:
    """
    Create the full model pipeline including preprocessor, oversampler, and classifier.

    :param preprocessor: Preprocessor for the data.
    :return: Full model pipeline.
    """
    return ImbPipeline([
        ('preprocessor', preprocessor),
        ('oversampler', RandomOverSampler()),
        ('classifier', RandomForestClassifier())
    ])


def custom_f1_score(y_true, y_pred):
    """
    Custom F1 score that handles string labels.

    :param y_true: True labels
    :param y_pred: Predicted labels
    :return: F1 score
    """
    le = LabelEncoder()
    y_true_encoded = le.fit_transform(y_true)
    y_pred_encoded = le.transform(y_pred)
    return f1_score(y_true_encoded, y_pred_encoded, pos_label=1)


def perform_grid_search(pipeline: ImbPipeline, X_train: pd.DataFrame, y_train: pd.Series) -> GridSearchCV:
    """
    Perform grid search for hyperparameter tuning.

    :param pipeline: Model pipeline.
    :param X_train: Training features.
    :param y_train: Training target.
    :return: Fitted grid search object
    """
    param_grid = {
        'classifier__n_estimators': [100, 200],
        'classifier__max_depth': [None, 10, 20],
        'classifier__min_samples_split': [2, 5],
        'classifier__min_samples_leaf': [1, 2]
    }

    custom_scorer = make_scorer(custom_f1_score)
    grid_search = GridSearchCV(pipeline, param_grid, cv=5, n_jobs=-1, scoring=custom_scorer)
    grid_search.fit(X_train, y_train)
    return grid_search


def save_model(model: GridSearchCV, path: str) -> None:
    """
    Save the best model from grid search.

    :param model: Fitted grid search object.
    :param path: Path to save the model.
    :raise Exception: If an error occurs while saving the model.
    """
    try:
        joblib.dump(model.best_estimator_, path)
    except Exception as e:
        raise Exception(f"An error occurred while saving the model: {str(e)}")


def train_model() -> None:
    """
    Main function to orchestrate the model training process.
    """
    load_dotenv()
    root_path = os.getenv('ROOT_PATH')

    # Database connection
    postgres = PostgresManager()

    # Load and preprocess data
    df = load_data(postgres)
    df = preprocess_data(df)

    # Split data
    X_train, X_test, y_train, y_test = split_data(df)

    # Get column types
    numerical_columns, categorical_columns = get_column_types(X_train)

    # Create preprocessor and model pipeline
    preprocessor = create_preprocessor(numerical_columns, categorical_columns)
    pipeline = create_model_pipeline(preprocessor)

    # Perform grid search
    grid_search = perform_grid_search(pipeline, X_train, y_train)

    # Save the best model
    best_model_path = os.path.join(root_path, 'model', 'random_forest_model.joblib')
    save_model(grid_search, best_model_path)


if __name__ == '__main__':
    train_model()
