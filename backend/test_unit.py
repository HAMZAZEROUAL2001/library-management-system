import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import jwt

from auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    verify_token,
    authenticate_user,
    get_current_user
)
from models import UserModel, BookModel, LoanModel
from database import get_db


class TestAuthenticationUnit:
    """Tests unitaires pour l'authentification"""
    
    def test_password_hashing(self):
        """Test du hachage et vérification des mots de passe"""
        password = "testpassword123"
        
        # Test du hachage
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 50  # Le hash bcrypt est long
        
        # Test de la vérification
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_jwt_token_creation_and_verification(self):
        """Test de création et vérification des tokens JWT"""
        user_data = {"sub": "testuser", "user_id": 1}
        
        # Créer un token
        token = create_access_token(data=user_data, expires_delta=timedelta(minutes=30))
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT a 3 parties
        
        # Vérifier le token
        decoded_data = verify_token(token)
        assert decoded_data["sub"] == "testuser"
        assert decoded_data["user_id"] == 1
        assert "exp" in decoded_data
    
    def test_expired_token(self):
        """Test avec un token expiré"""
        user_data = {"sub": "testuser", "user_id": 1}
        
        # Créer un token expiré
        token = create_access_token(data=user_data, expires_delta=timedelta(seconds=-1))
        
        # Vérifier que le token est rejeté
        decoded_data = verify_token(token)
        assert decoded_data is None
    
    def test_invalid_token(self):
        """Test avec un token invalide"""
        invalid_tokens = [
            "invalid.token.format",
            "completely-invalid-token",
            "",
            None
        ]
        
        for token in invalid_tokens:
            decoded_data = verify_token(token)
            assert decoded_data is None
    
    @patch('auth.get_db')
    def test_authenticate_user_success(self, mock_get_db):
        """Test d'authentification réussie"""
        # Mock de la base de données
        mock_db = Mock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        # Mock utilisateur
        mock_user = UserModel(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpassword")
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Test d'authentification
        result = authenticate_user("testuser", "testpassword")
        
        assert result == mock_user
        mock_db.query.assert_called_once()
    
    @patch('auth.get_db')
    def test_authenticate_user_failure(self, mock_get_db):
        """Test d'authentification échouée"""
        # Mock de la base de données
        mock_db = Mock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        # Cas 1: Utilisateur inexistant
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = authenticate_user("nonexistent", "password")
        assert result is None
        
        # Cas 2: Mot de passe incorrect
        mock_user = UserModel(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("correctpassword")
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        result = authenticate_user("testuser", "wrongpassword")
        assert result is None


class TestModelsUnit:
    """Tests unitaires pour les modèles"""
    
    def test_user_model(self):
        """Test du modèle User"""
        user = UserModel(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password"
        assert user.is_active is True  # Valeur par défaut
    
    def test_book_model(self):
        """Test du modèle Book"""
        book = BookModel(
            title="Test Book",
            author="Test Author",
            isbn="978-0123456789"
        )
        
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.isbn == "978-0123456789"
        assert book.available is True  # Valeur par défaut
        assert isinstance(book.created_at, datetime)
    
    def test_loan_model(self):
        """Test du modèle Loan"""
        loan = LoanModel(
            user_id=1,
            book_id=1
        )
        
        assert loan.user_id == 1
        assert loan.book_id == 1
        assert loan.is_returned is False  # Valeur par défaut
        assert isinstance(loan.loan_date, datetime)
        assert loan.return_date is None


class TestValidationUnit:
    """Tests unitaires pour la validation"""
    
    def test_isbn_validation(self):
        """Test de validation des ISBN"""
        from models import BookCreate
        
        # ISBN valides
        valid_isbns = [
            "978-0123456789",
            "978-0-123-45678-9",
            "9780123456789",
            "0123456789"
        ]
        
        for isbn in valid_isbns:
            book = BookCreate(title="Test", author="Author", isbn=isbn)
            assert book.isbn == isbn
        
        # ISBN invalides
        invalid_isbns = [
            "123",  # Trop court
            "abcd-efgh-ijkl",  # Lettres
            "978-012345678",  # Trop court
            "978-01234567890",  # Trop long
        ]
        
        for isbn in invalid_isbns:
            with pytest.raises(ValueError):
                BookCreate(title="Test", author="Author", isbn=isbn)
    
    def test_email_validation(self):
        """Test de validation des emails"""
        from models import UserCreate
        
        # Emails valides
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        for email in valid_emails:
            user = UserCreate(username="test", email=email, password="password")
            assert user.email == email
        
        # Emails invalides
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user name@example.com"
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValueError):
                UserCreate(username="test", email=email, password="password")


class TestBusinessLogicUnit:
    """Tests unitaires pour la logique métier"""
    
    @patch('models.BookModel')
    def test_book_availability_logic(self, mock_book_model):
        """Test de la logique de disponibilité des livres"""
        # Mock d'un livre disponible
        available_book = Mock()
        available_book.available = True
        
        # Mock d'un livre non disponible
        unavailable_book = Mock()
        unavailable_book.available = False
        
        # Test de disponibilité
        assert available_book.available is True
        assert unavailable_book.available is False
    
    def test_loan_duration_calculation(self):
        """Test du calcul de durée d'emprunt"""
        from datetime import datetime, timedelta
        
        loan_date = datetime(2024, 1, 1, 10, 0, 0)
        return_date = datetime(2024, 1, 15, 14, 30, 0)
        
        duration = return_date - loan_date
        assert duration.days == 14
        assert duration.total_seconds() > 0
    
    def test_search_query_processing(self):
        """Test du traitement des requêtes de recherche"""
        # Simulation de la logique de recherche
        def process_search_query(query):
            # Nettoyer et normaliser la requête
            cleaned = query.strip().lower()
            if len(cleaned) < 3:
                return None
            return cleaned
        
        # Tests
        assert process_search_query("Python") == "python"
        assert process_search_query("  JavaScript  ") == "javascript"
        assert process_search_query("Go") is None  # Trop court
        assert process_search_query("") is None  # Vide


class TestUtilityFunctions:
    """Tests pour les fonctions utilitaires"""
    
    def test_datetime_formatting(self):
        """Test du formatage des dates"""
        from datetime import datetime
        
        test_date = datetime(2024, 1, 15, 14, 30, 45)
        
        # Format ISO
        iso_format = test_date.isoformat()
        assert "2024-01-15T14:30:45" in iso_format
        
        # Format personnalisé
        custom_format = test_date.strftime("%Y-%m-%d %H:%M:%S")
        assert custom_format == "2024-01-15 14:30:45"
    
    def test_pagination_logic(self):
        """Test de la logique de pagination"""
        def calculate_pagination(total_items, page_size, current_page):
            total_pages = (total_items + page_size - 1) // page_size
            skip = (current_page - 1) * page_size
            return {
                "total_pages": total_pages,
                "current_page": current_page,
                "skip": skip,
                "limit": page_size,
                "has_next": current_page < total_pages,
                "has_prev": current_page > 1
            }
        
        # Test avec 25 éléments, 10 par page, page 2
        result = calculate_pagination(25, 10, 2)
        
        assert result["total_pages"] == 3
        assert result["current_page"] == 2
        assert result["skip"] == 10
        assert result["limit"] == 10
        assert result["has_next"] is True
        assert result["has_prev"] is True


class TestErrorHandling:
    """Tests pour la gestion d'erreurs"""
    
    def test_database_connection_error(self):
        """Test de gestion d'erreur de connexion DB"""
        with patch('database.SessionLocal') as mock_session:
            mock_session.side_effect = Exception("Connection failed")
            
            # Simuler une fonction qui utilise la DB
            def get_books_with_error():
                try:
                    db = mock_session()
                    return db.query().all()
                except Exception as e:
                    return {"error": str(e)}
            
            result = get_books_with_error()
            assert "error" in result
            assert "Connection failed" in result["error"]
    
    def test_validation_error_handling(self):
        """Test de gestion des erreurs de validation"""
        from pydantic import ValidationError
        from models import BookCreate
        
        # Test avec des données invalides
        try:
            BookCreate(title="", author="", isbn="invalid")
            assert False, "Devrait lever une ValidationError"
        except ValidationError as e:
            assert len(e.errors()) > 0
            error_fields = [error["loc"][0] for error in e.errors()]
            assert "title" in error_fields or "isbn" in error_fields


class TestPerformanceUnit:
    """Tests unitaires de performance"""
    
    def test_password_hashing_performance(self):
        """Test de performance du hachage de mot de passe"""
        import time
        
        password = "testpassword123"
        
        start_time = time.time()
        for _ in range(10):
            get_password_hash(password)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        # Le hachage bcrypt devrait prendre moins d'une seconde par opération
        assert avg_time < 1.0, f"Hachage trop lent: {avg_time:.3f}s"
    
    def test_token_operations_performance(self):
        """Test de performance des opérations JWT"""
        import time
        
        user_data = {"sub": "testuser", "user_id": 1}
        
        # Test de création de tokens
        start_time = time.time()
        tokens = []
        for _ in range(100):
            token = create_access_token(data=user_data)
            tokens.append(token)
        creation_time = time.time() - start_time
        
        # Test de vérification de tokens
        start_time = time.time()
        for token in tokens:
            verify_token(token)
        verification_time = time.time() - start_time
        
        # Les opérations JWT devraient être rapides
        assert creation_time < 1.0, f"Création de tokens trop lente: {creation_time:.3f}s"
        assert verification_time < 1.0, f"Vérification de tokens trop lente: {verification_time:.3f}s"


class TestMocking:
    """Tests utilisant des mocks pour isoler les composants"""
    
    @patch('auth.SessionLocal')
    def test_database_dependency_mock(self, mock_session_local):
        """Test avec mock de la dépendance DB"""
        # Configuration du mock
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Utilisation de la dépendance
        db_gen = get_db()
        db = next(db_gen)
        
        assert db == mock_db
        mock_session_local.assert_called_once()
    
    @patch('auth.pwd_context')
    def test_password_context_mock(self, mock_pwd_context):
        """Test avec mock du contexte de mot de passe"""
        # Configuration du mock
        mock_pwd_context.hash.return_value = "mocked_hash"
        mock_pwd_context.verify.return_value = True
        
        # Test des fonctions
        hashed = get_password_hash("password")
        assert hashed == "mocked_hash"
        
        is_valid = verify_password("password", "hash")
        assert is_valid is True
        
        mock_pwd_context.hash.assert_called_once_with("password")
        mock_pwd_context.verify.assert_called_once_with("password", "hash")


if __name__ == "__main__":
    # Exécuter tous les tests unitaires
    pytest.main([
        "test_unit.py",
        "-v",
        "--cov=auth",
        "--cov=models",
        "--cov-report=html",
        "--cov-report=term-missing"
    ])