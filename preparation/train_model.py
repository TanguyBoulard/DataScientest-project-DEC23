import os
from typing import Tuple, List, Any

import numpy as np
import pandas as pd
import joblib
from dotenv import load_dotenv
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import RandomOverSampler
from imblearn.pipeline import Pipeline as ImbPipeline
import warnings

from database.postgresql_functools import PostgresManager
from database.redis_functools import RedisManager

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
    df.columns = [str(col) for col in df.columns]
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the weather data by creating target variables.

    :param df: Raw weather data.
    :return: Preprocessed weather data
    """
    df['rain_today'] = df['rainfall'].apply(lambda x: 'yes' if x >= 1 else 'no')
    df['rain_tomorrow'] = df['rain_today'].shift(-1).apply(lambda x: 'yes' if x == 'yes' else 'no')
    df = df.dropna(subset=['rain_today', 'rain_tomorrow'])
    return df


def get_column_types(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """
    Identify numerical and categorical columns in the dataset.

    :param df: Input features.
    :return: Tuple of numerical and categorical column names
    """
    numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
    return numerical_columns, categorical_columns


def create_preprocessor(numerical_columns: List[str],
                        categorical_columns: List[str]) -> ColumnTransformer:
    """
    Create a preprocessor for numerical and categorical data.

    :param numerical_columns: List of numerical column names.
    :param categorical_columns: List of categorical column names.
    :return: ColumnTransformer for preprocessing.
    """
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(missing_values=np.nan, strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(missing_values=np.nan, strategy='most_frequent')),
        ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_columns),
            ('cat', categorical_transformer, categorical_columns),
        ])

    return preprocessor


def create_model_pipeline(preprocessor: ColumnTransformer) -> ImbPipeline:
    """
    Create the full model pipeline including preprocessor, oversampler, and classifier.

    :param preprocessor: Preprocessor for the data.
    :return: Full model pipeline.
    """
    return ImbPipeline([
        ('preprocessor', preprocessor),
        ('oversampler', RandomOverSampler(random_state=42)),
        ('classifier', RandomForestClassifier(
            max_depth=None,
            min_samples_leaf=4,
            min_samples_split=9,
            n_estimators=161,
            random_state=42
        ))
    ])


def save_model(ser_obj: Any, path: str, redis_manager: RedisManager, redis_key: str) -> None:
    """
    Save the model or encoder.

    :param ser_obj: Model or encoder to save.
    :param path: Path to save the model or encoder.
    :param redis_manager: RedisManager for saving to Redis.
    :param redis_key: Key to use when saving to Redis.
    :raise Exception: If an error occurs while saving.
    """
    try:
        joblib.dump(ser_obj, path)

        try:
            redis_manager.set_serializable_object(redis_key, ser_obj, expiration=86400)
        except Exception as e:
            raise Exception(f"An error occurred while saving to Redis: {str(e)}")

    except Exception as e:
        raise Exception(f"An error occurred while saving: {str(e)}")


def train_model() -> None:
    """
    Main function to orchestrate the model training process.
    """
    load_dotenv()
    root_path = os.getenv('ROOT_PATH')

    # Database connection
    postgres = PostgresManager()
    redis = RedisManager()

    # Load and preprocess data
    df = load_data(postgres)
    df = preprocess_data(df)

    # Prepare data for training
    X = df.drop(['rain_tomorrow', 'date'], axis=1)
    y = df['rain_tomorrow']

    # Get column types
    numerical_columns, categorical_columns = get_column_types(X)

    # Create preprocessor and model pipeline
    preprocessor = create_preprocessor(numerical_columns, categorical_columns)
    pipeline = create_model_pipeline(preprocessor)

    # Encode target variable
    target_le = LabelEncoder()
    y = pd.Series(target_le.fit_transform(y))

    # Train model
    pipeline.fit(X, y)

    # Save the label encoder and the model
    label_path = os.path.join(root_path, 'model', 'label_encoder.joblib')
    save_model(target_le, label_path, redis, 'weather_label_encoder')

    model_path = os.path.join(root_path, 'model', 'weather_model.joblib')
    save_model(pipeline, model_path, redis, 'weather_prediction_model')


if __name__ == '__main__':
    train_model()