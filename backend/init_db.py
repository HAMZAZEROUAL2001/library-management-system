#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
Crée les tables et insère des données de test
"""

from database import engine
from models import Base, UserModel, BookModel, LoanModel
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
import hashlib

def hash_password(password: str) -> str:
    # Simple hash pour les tests (à remplacer par bcrypt en production)
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Initialise la base de données avec les tables et données de test"""
    
    print("🔧 Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès")
    
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Vérifier si des données existent déjà
        if db.query(UserModel).first():
            print("ℹ️  Des données existent déjà dans la base")
            return
        
        print("📚 Insertion des données de test...")
        
        # Créer des utilisateurs de test
        users_data = [
            {"username": "admin", "email": "admin@library.com", "password": "admin123", "is_admin": True},
            {"username": "john_doe", "email": "john@example.com", "password": "user123", "is_admin": False},
            {"username": "jane_smith", "email": "jane@example.com", "password": "user123", "is_admin": False},
            {"username": "bob_wilson", "email": "bob@example.com", "password": "user123", "is_admin": False},
        ]
        
        users = []
        for user_data in users_data:
            user = UserModel(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                is_admin=user_data["is_admin"],
                is_active=True
            )
            db.add(user)
            users.append(user)
        
        # Créer des livres de test
        books_data = [
            {"title": "Clean Code", "author": "Robert C. Martin", "isbn": "978-0132350884", "quantity": 3},
            {"title": "Design Patterns", "author": "Gang of Four", "isbn": "978-0201633612", "quantity": 2},
            {"title": "Refactoring", "author": "Martin Fowler", "isbn": "978-0134757599", "quantity": 4},
            {"title": "Effective Python", "author": "Brett Slatkin", "isbn": "978-0134853987", "quantity": 2},
            {"title": "Python Tricks", "author": "Dan Bader", "isbn": "978-1775093305", "quantity": 3},
            {"title": "Architecture Patterns", "author": "Mark Richards", "isbn": "978-1492075752", "quantity": 2},
            {"title": "Microservices Patterns", "author": "Chris Richardson", "isbn": "978-1617294549", "quantity": 1},
            {"title": "Docker Deep Dive", "author": "Nigel Poulton", "isbn": "978-1521822807", "quantity": 2},
        ]
        
        books = []
        for book_data in books_data:
            book = BookModel(
                title=book_data["title"],
                author=book_data["author"],
                isbn=book_data["isbn"],
                quantity=book_data["quantity"]
            )
            db.add(book)
            books.append(book)
        
        # Commit pour obtenir les IDs
        db.commit()
        
        # Créer quelques emprunts de test
        loans_data = [
            {"user_idx": 1, "book_idx": 0, "days_ago": 5, "returned": False},
            {"user_idx": 2, "book_idx": 1, "days_ago": 10, "returned": True},
            {"user_idx": 3, "book_idx": 2, "days_ago": 3, "returned": False},
            {"user_idx": 1, "book_idx": 4, "days_ago": 15, "returned": True},
        ]
        
        for loan_data in loans_data:
            loan_date = datetime.now() - timedelta(days=loan_data["days_ago"])
            due_date = loan_date + timedelta(days=14)  # 2 semaines d'emprunt
            
            loan = LoanModel(
                user_id=users[loan_data["user_idx"]].id,
                book_id=books[loan_data["book_idx"]].id,
                loan_date=loan_date,
                due_date=due_date,
                is_returned=loan_data["returned"]
            )
            
            if loan_data["returned"]:
                loan.return_date = loan_date + timedelta(days=random.randint(1, 13))
            else:
                # Réduire la quantité disponible
                books[loan_data["book_idx"]].quantity -= 1
            
            db.add(loan)
        
        db.commit()
        
        print("✅ Données de test insérées avec succès!")
        print(f"👥 Utilisateurs créés: {len(users_data)}")
        print(f"📖 Livres ajoutés: {len(books_data)}")
        print(f"📋 Emprunts créés: {len(loans_data)}")
        
        # Afficher un résumé
        print("\n📊 Résumé de la base de données:")
        print(f"   - Utilisateurs: {db.query(UserModel).count()}")
        print(f"   - Livres: {db.query(BookModel).count()}")
        print(f"   - Emprunts: {db.query(LoanModel).count()}")
        print(f"   - Emprunts en cours: {db.query(LoanModel).filter(LoanModel.is_returned == False).count()}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()