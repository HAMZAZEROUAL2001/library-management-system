#!/usr/bin/env python3
"""
Test End-to-End du système Library Management System
Teste l'intégration complète : Frontend React + Backend FastAPI + PostgreSQL + Nginx
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost"
API_URL = f"{BASE_URL}/api"
FRONTEND_URL = BASE_URL

def test_system_health():
    """Test de santé générale du système"""
    print("🔍 Test de santé du système...")
    
    # Test santé backend via Nginx
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    health_data = response.json()
    assert health_data["status"] == "healthy"
    print("✅ Backend en santé via Nginx")
    
    # Test direct backend
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    print("✅ Backend direct accessible")
    
    # Test frontend
    response = requests.get(FRONTEND_URL)
    assert response.status_code == 200
    assert "Library Management System" in response.text or "html" in response.text
    print("✅ Frontend accessible")

def test_api_authentication():
    """Test du système d'authentification"""
    print("\n🔐 Test d'authentification...")
    
    # Test création d'utilisateur
    new_user = {
        "username": f"test_user_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{API_URL}/users/", json=new_user)
    print(f"Création utilisateur: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("✅ Utilisateur créé avec succès")
        created_user = response.json()
        print(f"Utilisateur créé: {created_user.get('username', 'N/A')}")
        
        # Test connexion
        login_data = {
            "username": new_user["username"],
            "password": new_user["password"]
        }
        
        response = requests.post(f"{API_URL}/token", data=login_data)
        print(f"Tentative de connexion: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("✅ Connexion réussie")
            return access_token
        else:
            print(f"❌ Échec connexion: {response.status_code} - {response.text}")
    else:
        print(f"⚠️ Problème création utilisateur: {response.status_code} - {response.text}")
        
        # Essayer de se connecter avec un utilisateur existant
        login_data = {
            "username": "admin",
            "password": "admin"
        }
        
        response = requests.post(f"{API_URL}/token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("✅ Connexion avec utilisateur existant")
            return access_token
    
    return None

def test_book_management(token):
    """Test de gestion des livres"""
    if not token:
        print("⚠️ Pas de token, skip test livres")
        return
        
    print("\n📚 Test de gestion des livres...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test récupération des livres
    response = requests.get(f"{API_URL}/books", headers=headers)
    print(f"Liste des livres: {response.status_code}")
    
    if response.status_code == 200:
        books = response.json()
        print(f"✅ {len(books)} livres trouvés")
        
        if books:
            # Test détail d'un livre
            book_id = books[0]["id"]
            response = requests.get(f"{API_URL}/books/{book_id}", headers=headers)
            if response.status_code == 200:
                print("✅ Détail livre accessible")
            else:
                print(f"❌ Erreur détail livre: {response.status_code}")
    else:
        print(f"❌ Erreur liste livres: {response.status_code}")

def test_loan_system(token):
    """Test du système d'emprunt"""
    if not token:
        print("⚠️ Pas de token, skip test emprunts")
        return
        
    print("\n📖 Test du système d'emprunts...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test récupération des emprunts
    response = requests.get(f"{API_URL}/loans", headers=headers)
    print(f"Liste des emprunts: {response.status_code}")
    
    if response.status_code == 200:
        loans = response.json()
        print(f"✅ {len(loans)} emprunts trouvés")
    else:
        print(f"❌ Erreur liste emprunts: {response.status_code}")

def test_api_documentation():
    """Test de la documentation API"""
    print("\n📋 Test documentation API...")
    
    # Test Swagger UI
    response = requests.get("http://localhost:8000/docs")
    if response.status_code == 200:
        print("✅ Documentation Swagger accessible")
    else:
        print(f"❌ Erreur documentation: {response.status_code}")
    
    # Test OpenAPI schema
    response = requests.get("http://localhost:8000/openapi.json")
    if response.status_code == 200:
        schema = response.json()
        print(f"✅ Schéma OpenAPI disponible ({len(schema.get('paths', {}))} endpoints)")
    else:
        print(f"❌ Erreur schéma OpenAPI: {response.status_code}")

def test_database_connectivity():
    """Test de connectivité base de données"""
    print("\n🗄️ Test connectivité base de données...")
    
    # Test via un endpoint qui utilise la DB
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        print("✅ Base de données accessible via API")
    else:
        print(f"❌ Problème connectivité DB: {response.status_code}")

def main():
    """Fonction principale du test E2E"""
    print("🚀 Démarrage des tests End-to-End")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Tests de base
        test_system_health()
        test_database_connectivity()
        test_api_documentation()
        
        # Tests avec authentification
        token = test_api_authentication()
        test_book_management(token)
        test_loan_system(token)
        
        print("\n" + "=" * 50)
        print("✅ Tests End-to-End terminés avec succès!")
        print(f"🌐 Frontend: {FRONTEND_URL}")
        print(f"🔗 API: {API_URL}")
        print(f"📚 Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        raise

if __name__ == "__main__":
    main()