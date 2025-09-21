from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr, Field

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
        orm_mode = True

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
