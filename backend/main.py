from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from database import get_db
from logging_config import logger
import re

# Importer les modèles et fonctions d'authentification
from models import Book, UserCreate, UserResponse, Token
from auth import (
    authenticate_user, 
    create_access_token, 
    get_current_user, 
    create_user, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models import UserModel, BookModel, Base, engine

# Recreate tables (for development, remove in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System",
    description="Une API de gestion de bibliothèque avec authentification",
    version="0.2.0"
)

@app.post("/users/", response_model=UserResponse, tags=["Users"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Enregistrer un nouvel utilisateur"""
    logger.info(f"Tentative d'enregistrement d'un nouvel utilisateur : {user.username}")
    return create_user(db, user)

@app.post("/token", response_model=Token, tags=["Authentication"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """Obtenir un token d'accès JWT"""
    logger.info(f"Tentative de connexion : {form_data.username}")
    
    # Authentifier l'utilisateur
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        logger.warning(f"Échec de connexion pour {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer le token d'accès
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    logger.info(f"Connexion réussie pour {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get('/')
def read_root():
    logger.info("Root endpoint accessed")
    return {'message': 'Bienvenue dans le système de gestion de bibliothèque'}

@app.post('/books')
def create_book(
    book: Book, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """Créer un nouveau livre (nécessite authentification)"""
    logger.info(f"Attempting to create book: {book.title} by {book.author}")

    # Check if book with same ISBN already exists
    existing_book = db.query(BookModel).filter(BookModel.isbn == book.isbn).first()
    if existing_book:
        logger.warning(f"Attempt to create duplicate book with ISBN: {book.isbn}")
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    
    # Create new book
    db_book = BookModel(
        title=book.title, 
        author=book.author, 
        isbn=book.isbn, 
        quantity=book.quantity
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    logger.info(f"Book created successfully: {book.title}")
    return book

@app.get('/books')
def list_books(
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """Lister tous les livres (nécessite authentification)"""
    logger.info("Retrieving list of books")
    books = db.query(BookModel).all()
    logger.info(f"Retrieved {len(books)} books")
    return books

@app.get('/books/{isbn}')
def get_book(
    isbn: str, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """Obtenir un livre par son ISBN (nécessite authentification)"""
    logger.info(f"Attempting to retrieve book with ISBN: {isbn}")
    book = db.query(BookModel).filter(BookModel.isbn == isbn).first()
    if not book:
        logger.warning(f"Book not found with ISBN: {isbn}")
        raise HTTPException(status_code=404, detail="Book not found")
    
    logger.info(f"Book retrieved successfully: {book.title}")
    return book

@app.put('/books/{isbn}')
def update_book(
    isbn: str, 
    book: Book, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """Mettre à jour un livre (nécessite authentification)"""
    # Validate that the ISBN in the path matches the book's ISBN
    if isbn != book.isbn:
        logger.warning(f"ISBN mismatch: path {isbn}, book {book.isbn}")
        raise HTTPException(status_code=400, detail="ISBN in path must match book's ISBN")
    
    logger.info(f"Attempting to update book with ISBN: {isbn}")
    
    db_book = db.query(BookModel).filter(BookModel.isbn == isbn).first()
    if not db_book:
        logger.warning(f"Book not found for update with ISBN: {isbn}")
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Update book details
    db_book.title = book.title
    db_book.author = book.author
    db_book.quantity = book.quantity
    
    db.commit()
    db.refresh(db_book)
    
    logger.info(f"Book updated successfully: {book.title}")
    return book

@app.delete('/books/{isbn}')
def delete_book(
    isbn: str, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """Supprimer un livre (nécessite authentification)"""
    logger.info(f"Attempting to delete book with ISBN: {isbn}")
    
    db_book = db.query(BookModel).filter(BookModel.isbn == isbn).first()
    if not db_book:
        logger.warning(f"Book not found for deletion with ISBN: {isbn}")
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)
    db.commit()
    
    logger.info(f"Book deleted successfully: {isbn}")
    return {"message": "Book deleted successfully"}
