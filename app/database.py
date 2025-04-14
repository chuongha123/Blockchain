import os

import pymysql
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

load_dotenv()

# Get database connection parameters
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "farmdb")

print(f"Connecting to MySQL at {DB_HOST}:{DB_PORT} with user {DB_USER}")

# Create the database if it doesn't exist
try:
    # Connect without specifying a database
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=int(DB_PORT)
    )
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    connection.close()
    print(f"Database '{DB_NAME}' created or already exists")
except Exception as e:
    print(f"Warning: Could not create database: {e}")
    print("Using SQLAlchemy with existing database configuration")

# Use the pre-defined DATABASE_URL from .env which has proper URL encoding
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine with a pool of connections
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using it
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False  # Don't log SQL queries
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        # Test the connection
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        print(f"Database connection error: {e}")
        raise
    finally:
        db.close()
