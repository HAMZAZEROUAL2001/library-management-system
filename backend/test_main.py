from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, Base
from database import get_db, BookModel

# Configuration de la base de données de test
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer les tables de test
Base.metadata.create_all(bind=engine)

# Remplacer la dépendance de base de données par une session de test
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Créer un client de test
client = TestClient(app)

def test_create_book():
    """Test de création d'un nouveau livre"""
    # Supprimer tous les livres existants avant le test
    with TestingSessionLocal() as db:
        db.query(BookModel).delete()
        db.commit()

    # Données de test pour un nouveau livre
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "1234567890",
        "quantity": 5
    }

    # Tester la création du livre
    response = client.post("/books", json=book_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == book_data["title"]
    assert data["author"] == book_data["author"]
    assert data["isbn"] == book_data["isbn"]
    assert data["quantity"] == book_data["quantity"]

def test_create_duplicate_book():
    """Test de création d'un livre avec un ISBN existant"""
    # Supprimer tous les livres existants avant le test
    with TestingSessionLocal() as db:
        db.query(BookModel).delete()
        db.commit()

    # Données de test pour un nouveau livre
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "1234567890",
        "quantity": 5
    }

    # Créer un premier livre
    response = client.post("/books", json=book_data)
    assert response.status_code == 200

    # Essayer de créer un livre avec le même ISBN
    response = client.post("/books", json=book_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_get_books():
    """Test de récupération de la liste des livres"""
    # Supprimer tous les livres existants avant le test
    with TestingSessionLocal() as db:
        db.query(BookModel).delete()
        db.commit()

    # Créer quelques livres de test
    books_data = [
        {
            "title": "Book 1",
            "author": "Author 1",
            "isbn": "1111111111",
            "quantity": 3
        },
        {
            "title": "Book 2",
            "author": "Author 2",
            "isbn": "2222222222",
            "quantity": 5
        }
    ]

    # Ajouter les livres
    for book_data in books_data:
        response = client.post("/books", json=book_data)
        assert response.status_code == 200

    # Récupérer la liste des livres
    response = client.get("/books")
    assert response.status_code == 200
    books = response.json()
    assert len(books) >= 2

def test_update_book():
    """Test de mise à jour d'un livre"""
    # Supprimer tous les livres existants avant le test
    with TestingSessionLocal() as db:
        db.query(BookModel).delete()
        db.commit()

    # Créer un livre initial
    initial_book = {
        "title": "Original Book",
        "author": "Original Author",
        "isbn": "1234567890",
        "quantity": 5
    }
    response = client.post("/books", json=initial_book)
    assert response.status_code == 200

    # Données de mise à jour
    updated_book = {
        "title": "Updated Book",
        "author": "Updated Author",
        "isbn": "1234567890",
        "quantity": 10
    }

    # Mettre à jour le livre
    response = client.put("/books/1234567890", json=updated_book)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == updated_book["title"]
    assert data["author"] == updated_book["author"]
    assert data["quantity"] == updated_book["quantity"]

def test_delete_book():
    """Test de suppression d'un livre"""
    # Supprimer tous les livres existants avant le test
    with TestingSessionLocal() as db:
        db.query(BookModel).delete()
        db.commit()

    # Créer un livre à supprimer
    book_data = {
        "title": "Book to Delete",
        "author": "Delete Author",
        "isbn": "9876543210",
        "quantity": 3
    }
    response = client.post("/books", json=book_data)
    assert response.status_code == 200

    # Supprimer le livre
    response = client.delete("/books/9876543210")
    assert response.status_code == 200
    assert response.json()["message"] == "Book deleted successfully"

    # Vérifier que le livre n'existe plus
    response = client.get("/books/9876543210")
    assert response.status_code == 404
