from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# PostgreSQL database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://library_user:library_pass@localhost:5432/library_management"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import des modèles pour s'assurer qu'ils sont créés
from models import Base, UserModel, BookModel, LoanModel

# Créer les tables
Base.metadata.create_all(bind=engine)
