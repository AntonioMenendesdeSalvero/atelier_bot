from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Підключення до бази даних
DATABASE_URL = "sqlite:///database.db"  # Замініть на вашу базу даних

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_session():
    """
    Повертає нову сесію бази даних.
    """
    return SessionLocal()


