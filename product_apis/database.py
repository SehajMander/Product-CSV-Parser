from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database configuration - simple and suitable for this assessment
DATABASE_URL = "sqlite:///./products.db"

# Create database engine with SQLite-specific settings
database_engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Required for SQLite threading
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database_engine)

# Base class for all models
Base = declarative_base()
