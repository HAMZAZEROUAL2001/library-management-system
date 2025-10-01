import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db, Base
from models import UserModel, BookModel
import auth


# Base de données en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
async def async_client():
    """Client HTTP asynchrone pour les tests"""
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    # Override de la dépendance DB
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Nettoyer
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def test_db():
    """Session de base de données pour les tests"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_data():
    """Données de test pour un utilisateur"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def test_book_data():
    """Données de test pour un livre"""
    return {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "978-0123456789"
    }


@pytest.fixture
async def authenticated_user(async_client: AsyncClient, test_user_data):
    """Utilisateur authentifié avec token"""
    # Créer un utilisateur
    response = await async_client.post("/register", json=test_user_data)
    assert response.status_code == 201
    
    # Se connecter
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = await async_client.post("/token", data=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    token = token_data["access_token"]
    
    return {
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "user_data": test_user_data
    }


class TestAuthentication:
    """Tests pour l'authentification"""
    
    async def test_register_user(self, async_client: AsyncClient, test_user_data):
        """Test d'inscription d'un nouvel utilisateur"""
        response = await async_client.post("/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "password" not in data
        assert data["is_active"] is True
    
    async def test_register_duplicate_user(self, async_client: AsyncClient, test_user_data):
        """Test d'inscription avec un utilisateur déjà existant"""
        # Première inscription
        response = await async_client.post("/register", json=test_user_data)
        assert response.status_code == 201
        
        # Deuxième inscription avec le même nom d'utilisateur
        response = await async_client.post("/register", json=test_user_data)
        assert response.status_code == 400
    
    async def test_login_valid_user(self, async_client: AsyncClient, test_user_data):
        """Test de connexion avec des identifiants valides"""
        # Créer un utilisateur
        await async_client.post("/register", json=test_user_data)
        
        # Se connecter
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = await async_client.post("/token", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_user(self, async_client: AsyncClient):
        """Test de connexion avec des identifiants invalides"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        response = await async_client.post("/token", data=login_data)
        
        assert response.status_code == 401
    
    async def test_get_current_user(self, async_client: AsyncClient, authenticated_user):
        """Test de récupération des informations utilisateur"""
        response = await async_client.get("/users/me", headers=authenticated_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == authenticated_user["user_data"]["username"]
        assert data["email"] == authenticated_user["user_data"]["email"]
    
    async def test_get_current_user_without_token(self, async_client: AsyncClient):
        """Test d'accès aux informations utilisateur sans token"""
        response = await async_client.get("/users/me")
        
        assert response.status_code == 401


class TestBooks:
    """Tests pour la gestion des livres"""
    
    async def test_create_book(self, async_client: AsyncClient, authenticated_user, test_book_data):
        """Test de création d'un livre"""
        response = await async_client.post(
            "/books", 
            json=test_book_data, 
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == test_book_data["title"]
        assert data["author"] == test_book_data["author"]
        assert data["isbn"] == test_book_data["isbn"]
        assert data["available"] is True
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_book_without_auth(self, async_client: AsyncClient, test_book_data):
        """Test de création d'un livre sans authentification"""
        response = await async_client.post("/books", json=test_book_data)
        
        assert response.status_code == 401
    
    async def test_get_books(self, async_client: AsyncClient, authenticated_user, test_book_data):
        """Test de récupération de la liste des livres"""
        # Créer quelques livres
        await async_client.post("/books", json=test_book_data, headers=authenticated_user["headers"])
        
        book_data_2 = {
            "title": "Another Book",
            "author": "Another Author",
            "isbn": "978-0987654321"
        }
        await async_client.post("/books", json=book_data_2, headers=authenticated_user["headers"])
        
        # Récupérer la liste
        response = await async_client.get("/books")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == test_book_data["title"]
        assert data[1]["title"] == book_data_2["title"]
    
    async def test_get_book_by_id(self, async_client: AsyncClient, authenticated_user, test_book_data):
        """Test de récupération d'un livre par ID"""
        # Créer un livre
        create_response = await async_client.post(
            "/books", 
            json=test_book_data, 
            headers=authenticated_user["headers"]
        )
        book_id = create_response.json()["id"]
        
        # Récupérer le livre par ID
        response = await async_client.get(f"/books/{book_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == book_id
        assert data["title"] == test_book_data["title"]
    
    async def test_get_nonexistent_book(self, async_client: AsyncClient):
        """Test de récupération d'un livre inexistant"""
        response = await async_client.get("/books/999")
        
        assert response.status_code == 404
    
    async def test_update_book(self, async_client: AsyncClient, authenticated_user, test_book_data):
        """Test de mise à jour d'un livre"""
        # Créer un livre
        create_response = await async_client.post(
            "/books", 
            json=test_book_data, 
            headers=authenticated_user["headers"]
        )
        book_id = create_response.json()["id"]
        
        # Mettre à jour le livre
        update_data = {
            "title": "Updated Title",
            "author": test_book_data["author"],
            "isbn": test_book_data["isbn"],
            "available": False
        }
        response = await async_client.put(
            f"/books/{book_id}", 
            json=update_data, 
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["available"] is False
    
    async def test_delete_book(self, async_client: AsyncClient, authenticated_user, test_book_data):
        """Test de suppression d'un livre"""
        # Créer un livre
        create_response = await async_client.post(
            "/books", 
            json=test_book_data, 
            headers=authenticated_user["headers"]
        )
        book_id = create_response.json()["id"]
        
        # Supprimer le livre
        response = await async_client.delete(
            f"/books/{book_id}", 
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 204
        
        # Vérifier que le livre n'existe plus
        get_response = await async_client.get(f"/books/{book_id}")
        assert get_response.status_code == 404
    
    async def test_search_books(self, async_client: AsyncClient, authenticated_user):
        """Test de recherche de livres"""
        # Créer quelques livres
        books = [
            {"title": "Python Programming", "author": "John Doe", "isbn": "978-0111111111"},
            {"title": "JavaScript Guide", "author": "Jane Smith", "isbn": "978-0222222222"},
            {"title": "Python Advanced", "author": "Bob Johnson", "isbn": "978-0333333333"},
        ]
        
        for book in books:
            await async_client.post("/books", json=book, headers=authenticated_user["headers"])
        
        # Rechercher "Python"
        response = await async_client.get("/books/search?q=Python")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("Python" in book["title"] for book in data)


class TestLoans:
    """Tests pour le système d'emprunts"""
    
    async def test_create_loan(self, async_client: AsyncClient, authenticated_user, test_book_data):
        """Test de création d'un emprunt"""
        # Créer un livre
        book_response = await async_client.post(
            "/books", 
            json=test_book_data, 
            headers=authenticated_user["headers"]
        )
        book_id = book_response.json()["id"]
        
        # Emprunter le livre
        loan_data = {"book_id": book_id}
        response = await async_client.post(
            "/loans", 
            json=loan_data, 
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["book_id"] == book_id
        assert data["is_returned"] is False
        assert "loan_date" in data
        assert data["return_date"] is None
    
    async def test_create_loan_unavailable_book(self, async_client: AsyncClient, authenticated_user, test_book_data):
        """Test d'emprunt d'un livre non disponible"""
        # Créer un livre et le rendre indisponible
        book_response = await async_client.post(
            "/books", 
            json=test_book_data, 
            headers=authenticated_user["headers"]
        )
        book_id = book_response.json()["id"]
        
        # Premier emprunt
        loan_data = {"book_id": book_id}
        await async_client.post("/loans", json=loan_data, headers=authenticated_user["headers"])
        
        # Deuxième emprunt (devrait échouer)
        response = await async_client.post(
            "/loans", 
            json=loan_data, 
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 400
    
    async def test_get_user_loans(self, async_client: AsyncClient, authenticated_user, test_book_data):
        """Test de récupération des emprunts d'un utilisateur"""
        # Créer et emprunter un livre
        book_response = await async_client.post(
            "/books", 
            json=test_book_data, 
            headers=authenticated_user["headers"]
        )
        book_id = book_response.json()["id"]
        
        loan_data = {"book_id": book_id}
        await async_client.post("/loans", json=loan_data, headers=authenticated_user["headers"])
        
        # Récupérer les emprunts
        response = await async_client.get("/loans/my-loans", headers=authenticated_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["book_id"] == book_id
    
    async def test_return_book(self, async_client: AsyncClient, authenticated_user, test_book_data):
        """Test de retour d'un livre"""
        # Créer et emprunter un livre
        book_response = await async_client.post(
            "/books", 
            json=test_book_data, 
            headers=authenticated_user["headers"]
        )
        book_id = book_response.json()["id"]
        
        loan_data = {"book_id": book_id}
        loan_response = await async_client.post(
            "/loans", 
            json=loan_data, 
            headers=authenticated_user["headers"]
        )
        loan_id = loan_response.json()["id"]
        
        # Retourner le livre
        response = await async_client.patch(
            f"/loans/{loan_id}/return", 
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_returned"] is True
        assert data["return_date"] is not None
        
        # Vérifier que le livre est redevenu disponible
        book_response = await async_client.get(f"/books/{book_id}")
        assert book_response.json()["available"] is True


class TestStats:
    """Tests pour les statistiques"""
    
    async def test_get_stats(self, async_client: AsyncClient, authenticated_user, test_book_data):
        """Test de récupération des statistiques"""
        # Créer quelques livres
        for i in range(3):
            book_data = {
                "title": f"Book {i}",
                "author": "Author",
                "isbn": f"978-{i:010d}"
            }
            await async_client.post("/books", json=book_data, headers=authenticated_user["headers"])
        
        # Emprunter un livre
        loan_data = {"book_id": 1}
        await async_client.post("/loans", json=loan_data, headers=authenticated_user["headers"])
        
        # Récupérer les statistiques
        response = await async_client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_books"] == 3
        assert data["available_books"] == 2
        assert data["total_loans"] == 1
        assert data["active_loans"] == 1


class TestValidation:
    """Tests pour la validation des données"""
    
    async def test_invalid_email_registration(self, async_client: AsyncClient):
        """Test d'inscription avec un email invalide"""
        invalid_data = {
            "username": "testuser",
            "email": "not-an-email",
            "password": "password123"
        }
        response = await async_client.post("/register", json=invalid_data)
        
        assert response.status_code == 422
    
    async def test_invalid_isbn_book(self, async_client: AsyncClient, authenticated_user):
        """Test de création de livre avec ISBN invalide"""
        invalid_book = {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "invalid-isbn"
        }
        response = await async_client.post(
            "/books", 
            json=invalid_book, 
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422
    
    async def test_missing_required_fields(self, async_client: AsyncClient, authenticated_user):
        """Test de création de livre avec des champs manquants"""
        incomplete_book = {
            "title": "Test Book"
            # author et isbn manquants
        }
        response = await async_client.post(
            "/books", 
            json=incomplete_book, 
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422


class TestSecurity:
    """Tests de sécurité"""
    
    async def test_access_protected_endpoint_without_token(self, async_client: AsyncClient):
        """Test d'accès à un endpoint protégé sans token"""
        response = await async_client.post("/books", json={"title": "Test"})
        assert response.status_code == 401
    
    async def test_access_with_invalid_token(self, async_client: AsyncClient):
        """Test d'accès avec un token invalide"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = await async_client.get("/users/me", headers=headers)
        assert response.status_code == 401
    
    async def test_sql_injection_protection(self, async_client: AsyncClient):
        """Test de protection contre l'injection SQL"""
        malicious_query = "'; DROP TABLE books; --"
        response = await async_client.get(f"/books/search?q={malicious_query}")
        
        # L'endpoint devrait gérer la requête sans erreur
        assert response.status_code == 200


# Tests de performance et de charge (utilisent pytest-benchmark si installé)
class TestPerformance:
    """Tests de performance de base"""
    
    async def test_concurrent_book_creation(self, async_client: AsyncClient, authenticated_user):
        """Test de création concurrente de livres"""
        tasks = []
        for i in range(10):
            book_data = {
                "title": f"Concurrent Book {i}",
                "author": "Concurrent Author",
                "isbn": f"978-{i:010d}"
            }
            task = async_client.post("/books", json=book_data, headers=authenticated_user["headers"])
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # Tous les livres devraient être créés avec succès
        for response in responses:
            assert response.status_code == 201
        
        # Vérifier que tous les livres sont présents
        books_response = await async_client.get("/books")
        assert len(books_response.json()) == 10


# Configuration pour les tests de couverture
if __name__ == "__main__":
    pytest.main([
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v"
    ])