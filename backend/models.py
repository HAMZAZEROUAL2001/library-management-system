from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timedelta

# Base pour les modèles SQLAlchemy
Base = declarative_base()

class UserModel(Base):
    """Modèle de base de données pour les utilisateurs"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relations
    loans = relationship("LoanModel", back_populates="user")

class BookModel(Base):
    """Modèle de base de données pour les livres"""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    isbn = Column(String, unique=True, index=True)
    quantity = Column(Integer, default=0)

# Modèles Pydantic pour la validation
class UserCreate(BaseModel):
    """Modèle pour la création d'un utilisateur"""
    username: str = Field(..., min_length=3, max_length=50, description="Nom d'utilisateur unique")
    email: EmailStr
    password: str = Field(..., min_length=8, description="Mot de passe")

class UserResponse(BaseModel):
    """Modèle de réponse pour les utilisateurs (sans mot de passe)"""
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Modèle pour la connexion des utilisateurs"""
    username: str
    password: str

class Token(BaseModel):
    """Modèle pour le token d'authentification"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Modèle pour les données du token"""
    username: str | None = None

# Modèle Pydantic pour les livres
class Book(BaseModel):
    """Modèle Pydantic pour les livres"""
    title: str = Field(..., min_length=1, max_length=200, description="Titre du livre")
    author: str = Field(..., min_length=2, max_length=100, description="Nom de l'auteur")
    isbn: str = Field(..., description="ISBN du livre")
    quantity: int = Field(default=0, ge=0, description="Nombre de livres en stock")

    class Config:
        from_attributes = True

# Modèle SQLAlchemy pour les emprunts
class LoanModel(Base):
    """Modèle de base de données pour les emprunts de livres"""
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    loan_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
    is_returned = Column(Boolean, default=False)

    # Relations
    book = relationship("BookModel", back_populates="loans")
    user = relationship("UserModel", back_populates="loans")

# Mettre à jour les modèles existants avec les relations
UserModel.loans = relationship("LoanModel", back_populates="user")
BookModel.loans = relationship("LoanModel", back_populates="book")

# Modèles Pydantic pour la validation
class LoanCreate(BaseModel):
    """Modèle pour la création d'un emprunt"""
    book_isbn: str
    loan_duration_days: int = Field(default=14, ge=1, le=30, description="Durée de l'emprunt en jours")

class LoanResponse(BaseModel):
    """Modèle de réponse pour un emprunt"""
    id: int
    book_id: int
    user_id: int
    loan_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    is_returned: bool

    class Config:
        from_attributes = True

class LoanReturnRequest(BaseModel):
    """Modèle pour le retour d'un livre"""
    loan_id: int
