#!/usr/bin/env python3
"""
Test de connexion à PostgreSQL
"""

try:
    from database import engine
    print(f"✅ Connexion PostgreSQL réussie: {engine.url}")
    
    # Test de connexion réelle
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ Base de données connectée: {version[:50]}...")
        
except Exception as e:
    print(f"❌ Erreur de connexion PostgreSQL: {e}")