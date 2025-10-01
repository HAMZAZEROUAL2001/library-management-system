from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from database import get_db
from logging_config import logger
import re
from typing import Optional, List
from datetime import datetime, timedelta

# Importer les modèles et fonctions d'authentification
from models import Book, UserCreate, UserResponse, Token, LoanModel, LoanCreate, LoanResponse, LoanReturnRequest
from auth import (
    authenticate_user, 
    create_access_token, 
    get_current_user, 
    create_user, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models import UserModel, BookModel, Base
from database import engine

# Importer le monitoring
from monitoring import (
    metrics, 
    get_metrics_endpoint,
    increment_user_registrations,
    increment_book_created,
    increment_book_updated,
    increment_book_deleted,
    increment_loan_created,
    increment_loan_returned
)

# Recreate tables (for development, remove in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System",
    description="Une API de gestion de bibliothèque avec authentification",
    version="0.2.0"
)

# Ajouter le middleware de monitoring
app.middleware("http")(metrics.middleware)

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
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    logger.info(f"Connexion réussie pour {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get('/')
def read_root():
    logger.info("Root endpoint accessed")
    return {'message': 'Bienvenue dans le système de gestion de bibliothèque'}

@app.get('/health')
def health_check():
    """Endpoint de santé pour Docker Compose healthcheck"""
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

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

@app.get('/books/search', response_model=List[Book])
def search_books(
    query: Optional[str] = Query(None, description="Terme de recherche (titre, auteur ou ISBN)"),
    min_quantity: Optional[int] = Query(None, ge=0, description="Quantité minimale de livres"),
    max_quantity: Optional[int] = Query(None, ge=0, description="Quantité maximale de livres"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Rechercher des livres avec des filtres optionnels
    
    Paramètres :
    - query : Terme de recherche (recherche sur titre, auteur, ISBN)
    - min_quantity : Quantité minimale de livres en stock
    - max_quantity : Quantité maximale de livres en stock
    """
    logger.info(f"Recherche de livres - Terme: {query}, Quantité min: {min_quantity}, Quantité max: {max_quantity}")
    
    # Requête de base
    search_query = db.query(BookModel)
    
    # Filtrage par terme de recherche
    if query:
        search_query = search_query.filter(
            or_(
                BookModel.title.ilike(f"%{query}%"),
                BookModel.author.ilike(f"%{query}%"),
                BookModel.isbn.ilike(f"%{query}%")
            )
        )
    
    # Filtrage par quantité
    if min_quantity is not None:
        search_query = search_query.filter(BookModel.quantity >= min_quantity)
    
    if max_quantity is not None:
        search_query = search_query.filter(BookModel.quantity <= max_quantity)
    
    # Exécuter la requête
    results = search_query.all()
    
    logger.info(f"Recherche terminée - {len(results)} résultats trouvés")
    
    return results

@app.get('/books/stats')
def get_book_statistics(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Obtenir des statistiques sur la collection de livres
    
    Retourne :
    - Nombre total de livres
    - Nombre de livres par auteur
    - Nombre de livres en stock
    """
    logger.info("Récupération des statistiques de la bibliothèque")
    
    # Nombre total de livres
    total_books = db.query(BookModel).count()
    
    # Nombre de livres par auteur
    books_by_author = db.query(
        BookModel.author, 
        func.count(BookModel.id).label('book_count')
    ).group_by(BookModel.author).all()
    
    # Total des livres en stock
    total_books_in_stock = db.query(func.sum(BookModel.quantity)).scalar() or 0
    
    stats = {
        "total_books": total_books,
        "books_by_author": [
            {"author": author, "count": count} 
            for author, count in books_by_author
        ],
        "total_books_in_stock": total_books_in_stock
    }
    
    logger.info("Statistiques récupérées avec succès")
    return stats

@app.post('/loans', response_model=LoanResponse)
def create_loan(
    loan: LoanCreate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Créer un nouvel emprunt de livre
    
    - Vérifie la disponibilité du livre
    - Crée un nouvel emprunt
    - Réduit la quantité de livres disponibles
    """
    logger.info(f"Tentative d'emprunt de livre par {current_user.username}")
    
    # Trouver le livre par ISBN
    book = db.query(BookModel).filter(BookModel.isbn == loan.book_isbn).first()
    if not book:
        logger.warning(f"Livre non trouvé avec l'ISBN : {loan.book_isbn}")
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    # Vérifier la disponibilité du livre
    if book.quantity < 1:
        logger.warning(f"Livre indisponible : {book.title}")
        raise HTTPException(status_code=400, detail="Aucun exemplaire de ce livre n'est disponible")
    
    # Calculer la date de retour
    loan_duration = timedelta(days=loan.loan_duration_days)
    due_date = datetime.utcnow() + loan_duration
    
    # Créer l'emprunt
    new_loan = LoanModel(
        book_id=book.id,
        user_id=current_user.id,
        due_date=due_date
    )
    
    # Réduire la quantité de livres
    book.quantity -= 1
    
    # Ajouter et committer
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    
    logger.info(f"Emprunt créé pour {current_user.username} - Livre : {book.title}")
    return new_loan

@app.post('/loans/return', response_model=LoanResponse)
def return_book(
    return_request: LoanReturnRequest, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retourner un livre emprunté
    
    - Marque l'emprunt comme retourné
    - Augmente la quantité de livres disponibles
    - Vérifie que l'utilisateur est le propriétaire de l'emprunt
    """
    logger.info(f"Tentative de retour de livre par {current_user.username}")
    
    # Trouver l'emprunt
    loan = db.query(LoanModel).filter(
        LoanModel.id == return_request.loan_id,
        LoanModel.user_id == current_user.id,
        LoanModel.is_returned == False
    ).first()
    
    if not loan:
        logger.warning(f"Emprunt non trouvé ou déjà retourné : {return_request.loan_id}")
        raise HTTPException(status_code=404, detail="Emprunt non trouvé ou déjà retourné")
    
    # Marquer comme retourné
    loan.is_returned = True
    loan.return_date = datetime.utcnow()
    
    # Récupérer le livre
    book = db.query(BookModel).filter(BookModel.id == loan.book_id).first()
    
    # Augmenter la quantité de livres
    book.quantity += 1
    
    # Vérifier les retards
    if loan.due_date < datetime.utcnow():
        logger.warning(f"Retard de retour pour l'emprunt : {loan.id}")
        # Vous pouvez ajouter une logique de pénalité ici si nécessaire
    
    # Committer les modifications
    db.commit()
    db.refresh(loan)
    
    logger.info(f"Livre retourné par {current_user.username}")
    return loan

@app.get('/loans/user', response_model=List[LoanResponse])
def get_user_loans(
    show_returned: bool = False,
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Récupérer les emprunts de l'utilisateur courant
    
    Paramètres :
    - show_returned : Inclure les livres déjà retournés
    """
    logger.info(f"Récupération des emprunts pour {current_user.username}")
    
    # Construire la requête
    query = db.query(LoanModel).filter(LoanModel.user_id == current_user.id)
    
    # Filtrer les emprunts non retournés si nécessaire
    if not show_returned:
        query = query.filter(LoanModel.is_returned == False)
    
    # Récupérer les emprunts
    loans = query.all()
    
    logger.info(f"Récupéré {len(loans)} emprunts")
    return loans

@app.get('/loans/overdue', response_model=List[LoanResponse])
def get_overdue_loans(
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Récupérer les emprunts en retard
    
    Nécessite des droits d'administrateur
    """
    # Vérifier les droits d'administrateur
    if not current_user.is_admin:
        logger.warning(f"Tentative d'accès aux emprunts en retard par un non-admin : {current_user.username}")
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    
    logger.info("Récupération des emprunts en retard")
    
    # Récupérer les emprunts non retournés et en retard
    overdue_loans = db.query(LoanModel).filter(
        LoanModel.is_returned == False,
        LoanModel.due_date < datetime.utcnow()
    ).all()
    
    logger.info(f"Récupéré {len(overdue_loans)} emprunts en retard")
    return overdue_loans
