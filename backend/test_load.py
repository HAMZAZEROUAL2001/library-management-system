import pytest
import asyncio
import time
from httpx import AsyncClient
from concurrent.futures import ThreadPoolExecutor
from locust import HttpUser, task, between
import statistics

from test_integration import async_client, authenticated_user, test_book_data


class TestLoad:
    """Tests de charge pour l'API"""

    @pytest.mark.asyncio
    async def test_concurrent_users_load(self, async_client: AsyncClient):
        """Test avec plusieurs utilisateurs concurrents"""
        
        async def create_user_and_books(user_id):
            """Créer un utilisateur et quelques livres"""
            user_data = {
                "username": f"loaduser{user_id}",
                "email": f"loaduser{user_id}@example.com",
                "password": "loadtest123"
            }
            
            # Inscription
            register_response = await async_client.post("/register", json=user_data)
            if register_response.status_code != 201:
                return False
            
            # Connexion
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            token_response = await async_client.post("/token", data=login_data)
            if token_response.status_code != 200:
                return False
            
            token = token_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Créer des livres
            success_count = 0
            for i in range(5):
                book_data = {
                    "title": f"Load Test Book {user_id}-{i}",
                    "author": f"Author {user_id}",
                    "isbn": f"978-{user_id:03d}{i:07d}"
                }
                book_response = await async_client.post("/books", json=book_data, headers=headers)
                if book_response.status_code == 201:
                    success_count += 1
            
            return success_count == 5
        
        # Créer 20 utilisateurs concurrents
        tasks = [create_user_and_books(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Vérifier que la plupart des opérations ont réussi
        successful = sum(1 for result in results if result is True)
        assert successful >= 15, f"Seulement {successful}/20 utilisateurs ont réussi"
    
    @pytest.mark.asyncio
    async def test_api_response_time(self, async_client: AsyncClient, authenticated_user):
        """Test des temps de réponse de l'API"""
        
        # Créer quelques livres pour les tests
        books = []
        for i in range(10):
            book_data = {
                "title": f"Response Time Book {i}",
                "author": "Speed Author",
                "isbn": f"978-{i:010d}"
            }
            response = await async_client.post("/books", json=book_data, headers=authenticated_user["headers"])
            books.append(response.json()["id"])
        
        # Test des temps de réponse pour différentes opérations
        response_times = {
            "list_books": [],
            "get_book": [],
            "search_books": [],
            "get_stats": []
        }
        
        for _ in range(50):  # 50 requêtes de chaque type
            # Liste des livres
            start_time = time.time()
            await async_client.get("/books")
            response_times["list_books"].append(time.time() - start_time)
            
            # Récupération d'un livre spécifique
            book_id = books[_ % len(books)]
            start_time = time.time()
            await async_client.get(f"/books/{book_id}")
            response_times["get_book"].append(time.time() - start_time)
            
            # Recherche
            start_time = time.time()
            await async_client.get("/books/search?q=Book")
            response_times["search_books"].append(time.time() - start_time)
            
            # Statistiques
            start_time = time.time()
            await async_client.get("/stats")
            response_times["get_stats"].append(time.time() - start_time)
        
        # Vérifier que les temps de réponse sont acceptables
        for operation, times in response_times.items():
            avg_time = statistics.mean(times)
            p95_time = statistics.quantiles(times, n=20)[18]  # 95e percentile
            
            print(f"{operation}: Avg={avg_time:.3f}s, P95={p95_time:.3f}s")
            
            # Les temps de réponse moyens devraient être < 1 seconde
            assert avg_time < 1.0, f"{operation} temps moyen trop élevé: {avg_time:.3f}s"
            
            # Le 95e percentile devrait être < 2 secondes
            assert p95_time < 2.0, f"{operation} P95 trop élevé: {p95_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_database_stress(self, async_client: AsyncClient, authenticated_user):
        """Test de stress sur la base de données"""
        
        # Créer beaucoup de livres rapidement
        async def create_books_batch(start_idx, count):
            tasks = []
            for i in range(count):
                book_data = {
                    "title": f"Stress Test Book {start_idx + i}",
                    "author": "Stress Author",
                    "isbn": f"978-{start_idx + i:010d}"
                }
                task = async_client.post("/books", json=book_data, headers=authenticated_user["headers"])
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            return responses
        
        # Créer 100 livres en 5 batches de 20
        all_responses = []
        for batch in range(5):
            batch_responses = await create_books_batch(batch * 20, 20)
            all_responses.extend(batch_responses)
        
        # Vérifier que la plupart des créations ont réussi
        successful = sum(1 for resp in all_responses 
                        if hasattr(resp, 'status_code') and resp.status_code == 201)
        
        assert successful >= 80, f"Seulement {successful}/100 créations ont réussi"
        
        # Test de lecture massive
        start_time = time.time()
        books_response = await async_client.get("/books?limit=100")
        read_time = time.time() - start_time
        
        assert books_response.status_code == 200
        assert len(books_response.json()) >= 80
        assert read_time < 2.0, f"Lecture de 100 livres trop lente: {read_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, async_client: AsyncClient, authenticated_user):
        """Test de stabilité de l'utilisation mémoire"""
        
        # Effectuer de nombreuses opérations pour détecter les fuites mémoire
        for cycle in range(10):
            # Créer des livres
            books = []
            for i in range(10):
                book_data = {
                    "title": f"Memory Test Book {cycle}-{i}",
                    "author": "Memory Author",
                    "isbn": f"978-{cycle:03d}{i:07d}"
                }
                response = await async_client.post("/books", json=book_data, headers=authenticated_user["headers"])
                if response.status_code == 201:
                    books.append(response.json()["id"])
            
            # Lire les livres
            for book_id in books:
                await async_client.get(f"/books/{book_id}")
            
            # Rechercher
            await async_client.get("/books/search?q=Memory")
            
            # Emprunter et retourner
            if books:
                loan_response = await async_client.post(
                    "/loans", 
                    json={"book_id": books[0]}, 
                    headers=authenticated_user["headers"]
                )
                if loan_response.status_code == 201:
                    loan_id = loan_response.json()["id"]
                    await async_client.patch(f"/loans/{loan_id}/return", headers=authenticated_user["headers"])
            
            # Supprimer quelques livres
            for book_id in books[:5]:
                await async_client.delete(f"/books/{book_id}", headers=authenticated_user["headers"])
        
        # Si nous arrivons ici sans erreur, c'est bon signe
        assert True


class LibraryLoadTestUser(HttpUser):
    """Utilisateur Locust pour les tests de charge"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """S'exécute au démarrage de chaque utilisateur"""
        # Créer un utilisateur unique
        import time
        timestamp = int(time.time() * 1000)
        self.username = f"loaduser_{timestamp}_{id(self)}"
        self.email = f"{self.username}@example.com"
        self.password = "loadtest123"
        
        # S'inscrire
        response = self.client.post("/register", json={
            "username": self.username,
            "email": self.email,
            "password": self.password
        })
        
        if response.status_code == 201:
            # Se connecter
            token_response = self.client.post("/token", data={
                "username": self.username,
                "password": self.password
            })
            
            if token_response.status_code == 200:
                self.token = token_response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
            else:
                self.token = None
                self.headers = {}
        else:
            self.token = None
            self.headers = {}
    
    @task(3)
    def list_books(self):
        """Lister les livres (tâche fréquente)"""
        self.client.get("/books")
    
    @task(2)
    def search_books(self):
        """Rechercher des livres"""
        search_terms = ["Python", "JavaScript", "Test", "Programming", "Guide"]
        term = search_terms[hash(self.username) % len(search_terms)]
        self.client.get(f"/books/search?q={term}")
    
    @task(1)
    def create_book(self):
        """Créer un livre (moins fréquent)"""
        if not self.headers:
            return
        
        import random
        book_id = random.randint(1000, 9999)
        book_data = {
            "title": f"Load Test Book {book_id}",
            "author": f"Load Author {self.username}",
            "isbn": f"978-{book_id:010d}"
        }
        
        self.client.post("/books", json=book_data, headers=self.headers)
    
    @task(1)
    def get_stats(self):
        """Obtenir les statistiques"""
        self.client.get("/stats")
    
    @task(1)
    def get_my_loans(self):
        """Voir mes emprunts"""
        if not self.headers:
            return
        
        self.client.get("/loans/my-loans", headers=self.headers)
    
    @task(1)
    def user_profile(self):
        """Voir le profil utilisateur"""
        if not self.headers:
            return
        
        self.client.get("/users/me", headers=self.headers)


class TestDatabasePerformance:
    """Tests de performance spécifiques à la base de données"""
    
    def test_large_dataset_queries(self, test_db, authenticated_user):
        """Test avec un grand jeu de données"""
        from models import BookModel, UserModel
        
        # Créer un utilisateur de test
        user = UserModel(
            username="perftest",
            email="perftest@example.com",
            hashed_password="hashed"
        )
        test_db.add(user)
        test_db.commit()
        
        # Créer beaucoup de livres
        books = []
        for i in range(1000):
            book = BookModel(
                title=f"Performance Book {i}",
                author=f"Author {i % 100}",  # 100 auteurs différents
                isbn=f"978-{i:010d}",
                available=i % 3 != 0  # 2/3 des livres disponibles
            )
            books.append(book)
        
        start_time = time.time()
        test_db.add_all(books)
        test_db.commit()
        insert_time = time.time() - start_time
        
        print(f"Insertion de 1000 livres: {insert_time:.2f}s")
        assert insert_time < 5.0, "Insertion trop lente"
        
        # Test de requêtes sur le grand jeu de données
        start_time = time.time()
        available_books = test_db.query(BookModel).filter(BookModel.available == True).all()
        query_time = time.time() - start_time
        
        print(f"Requête de livres disponibles: {query_time:.3f}s")
        assert query_time < 1.0, "Requête trop lente"
        assert len(available_books) > 600
        
        # Test de recherche textuelle
        start_time = time.time()
        search_results = test_db.query(BookModel).filter(
            BookModel.title.contains("Book 1")
        ).all()
        search_time = time.time() - start_time
        
        print(f"Recherche textuelle: {search_time:.3f}s")
        assert search_time < 1.0, "Recherche trop lente"
        assert len(search_results) >= 100  # Book 1, Book 10, Book 100, etc.


# Script pour lancer les tests de charge avec Locust
locust_script = '''
# Pour lancer un test de charge avec Locust:
# 1. Installer locust: pip install locust
# 2. Sauvegarder ce fichier comme locustfile.py
# 3. Lancer: locust -f test_load.py --host=http://localhost:8000
# 4. Ouvrir http://localhost:8089 pour l'interface web

from test_load import LibraryLoadTestUser

if __name__ == "__main__":
    import os
    os.system("locust -f test_load.py --host=http://localhost:8000")
'''

if __name__ == "__main__":
    # Exécuter les tests de charge
    pytest.main([
        "test_load.py::TestLoad",
        "-v",
        "-s",
        "--tb=short"
    ])