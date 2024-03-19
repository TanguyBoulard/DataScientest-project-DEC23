from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Determine the environment context
environment = os.getenv("ENVIRONMENT", "development")

if environment == "development":
    # Load environment variables for development
    SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
elif environment == "testing":
    # Load environment variables for testing
    SQLALCHEMY_DATABASE_URL = os.getenv("TEST_SQLALCHEMY_DATABASE_URL")
else:
    raise ValueError("Invalid environment. Please set ENVIRONMENT to 'development' or 'testing'.")

# Database connection
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
