# Bonnes Pratiques de Sécurité - Library Management System

Ce document présente les bonnes pratiques de sécurité appliquées au système de gestion de bibliothèque et les recommandations pour maintenir un niveau de sécurité élevé.

## 🛡️ Principes de sécurité fondamentaux

### Defense in Depth (Défense en profondeur)
- **Sécurité multicouche**: Application des contrôles à tous les niveaux
- **Principle of Least Privilege**: Permissions minimales nécessaires
- **Zero Trust**: Vérification continue de l'identité et des autorisations
- **Fail Secure**: En cas d'échec, le système doit être sécurisé par défaut

## 🔐 Sécurité de l'application

### Authentification et autorisation

#### JWT (JSON Web Tokens)
```python
# Configuration sécurisée des JWT
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME = timedelta(hours=1)  # Courte durée de vie
JWT_REFRESH_TOKEN_EXPIRATION = timedelta(days=7)

# Génération sécurisée des tokens
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + JWT_EXPIRATION_TIME
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
```

#### Hachage des mots de passe
```python
# Utilisation de bcrypt avec un coût adapté
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

#### Politique de mots de passe
```python
import re

def validate_password_strength(password: str) -> bool:
    """
    Politique de mot de passe:
    - Au moins 8 caractères
    - Au moins 1 majuscule
    - Au moins 1 minuscule
    - Au moins 1 chiffre
    - Au moins 1 caractère spécial
    """
    if len(password) < 8:
        return False
    
    patterns = [
        r'[A-Z]',  # Majuscule
        r'[a-z]',  # Minuscule
        r'\d',     # Chiffre
        r'[!@#$%^&*(),.?":{}|<>]'  # Caractère spécial
    ]
    
    return all(re.search(pattern, password) for pattern in patterns)
```

### Protection contre les attaques communes

#### Injection SQL
```python
# ✅ Utilisation d'ORM (SQLAlchemy) - Protection automatique
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# ❌ Éviter les requêtes brutes non sécurisées
# cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

#### XSS (Cross-Site Scripting)
```python
from fastapi.responses import HTMLResponse
from markupsafe import escape

# Échappement automatique des données utilisateur
def render_user_data(user_input: str):
    return escape(user_input)

# Configuration des headers de sécurité
from fastapi.middleware.security import SecurityHeadersMiddleware

app.add_middleware(
    SecurityHeadersMiddleware,
    content_security_policy="default-src 'self'; script-src 'self' 'unsafe-inline'",
    x_frame_options="DENY",
    x_content_type_options="nosniff"
)
```

#### CSRF (Cross-Site Request Forgery)
```python
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/books/")
async def create_book(
    book: BookCreate,
    csrf_protect: CsrfProtect = Depends(),
    current_user: User = Depends(get_current_user)
):
    csrf_protect.validate_csrf_token(request)
    # Logique de création du livre
```

### Validation et sanitisation des données

#### Validation d'entrée stricte
```python
from pydantic import BaseModel, validator, constr
from typing import Optional

class BookCreate(BaseModel):
    title: constr(min_length=1, max_length=200, regex=r'^[a-zA-Z0-9\s\-_.,!?]+$')
    author: constr(min_length=1, max_length=100, regex=r'^[a-zA-Z\s\-.,]+$')
    isbn: Optional[constr(regex=r'^\d{10}(\d{3})?$')] = None
    
    @validator('title', 'author')
    def validate_not_empty_or_whitespace(cls, v):
        if not v or v.isspace():
            raise ValueError('Field cannot be empty or contain only whitespace')
        return v.strip()
```

#### Limitation du taux de requêtes
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/auth/login")
@limiter.limit("5/minute")  # 5 tentatives par minute
async def login(request: Request, credentials: UserLogin):
    # Logique d'authentification
```

## 🔒 Sécurité de l'infrastructure

### Configuration Kubernetes sécurisée

#### Pod Security Standards
```yaml
# pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: library-management-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
```

#### Network Policies
```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: library-management-netpol
  namespace: library-management-prod
spec:
  podSelector:
    matchLabels:
      app: library-management
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
  - to: []  # DNS
    ports:
    - protocol: UDP
      port: 53
```

#### RBAC (Role-Based Access Control)
```yaml
# rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: library-management-prod
  name: library-management-role
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["events"]
  verbs: ["create"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: library-management-binding
  namespace: library-management-prod
subjects:
- kind: ServiceAccount
  name: library-management-sa
  namespace: library-management-prod
roleRef:
  kind: Role
  name: library-management-role
  apiGroup: rbac.authorization.k8s.io
```

### Gestion des secrets

#### HashiCorp Vault (recommandé pour production)
```yaml
# vault-secret-operator.yaml
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultStaticSecret
metadata:
  name: library-management-secrets
  namespace: library-management-prod
spec:
  type: kv-v2
  mount: secret
  path: library-management/prod
  destination:
    name: app-secrets
    create: true
  refreshAfter: 30s
```

#### Rotation automatique des secrets
```bash
#!/bin/bash
# rotate-secrets.sh - Script de rotation des secrets

NEW_SECRET=$(openssl rand -base64 32)
kubectl create secret generic app-secrets-new \
  --from-literal=secret_key="$NEW_SECRET" \
  -n library-management-prod

# Mise à jour progressive des pods
kubectl patch deployment library-management-prod \
  -p '{"spec":{"template":{"metadata":{"annotations":{"secret-rotation":"'$(date +%s)'"}}}}}'

# Attendre le rollout
kubectl rollout status deployment/library-management-prod -n library-management-prod

# Supprimer l'ancien secret
kubectl delete secret app-secrets -n library-management-prod
kubectl label secret app-secrets-new app-secrets- -n library-management-prod
```

### Chiffrement

#### TLS/SSL
```yaml
# tls-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: library-management-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - library.example.com
    secretName: library-management-tls
  rules:
  - host: library.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: library-management-service
            port:
              number: 80
```

#### Chiffrement des données au repos
```python
# Configuration PostgreSQL avec chiffrement
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require&sslcert=client-cert.pem&sslkey=client-key.pem&sslrootcert=ca-cert.pem"

# Chiffrement des données sensibles avant stockage
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

## 🔍 Surveillance et détection

### Logging de sécurité
```python
import logging
from fastapi import Request

security_logger = logging.getLogger("security")

async def log_security_event(request: Request, event_type: str, details: dict):
    security_logger.warning({
        "event_type": event_type,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "timestamp": datetime.utcnow().isoformat(),
        "details": details
    })

# Exemple d'utilisation
@app.post("/auth/login")
async def login(request: Request, credentials: UserLogin):
    try:
        # Logique d'authentification
        pass
    except AuthenticationError:
        await log_security_event(request, "FAILED_LOGIN", {
            "username": credentials.username,
            "reason": "invalid_credentials"
        })
        raise HTTPException(status_code=401, detail="Invalid credentials")
```

### Détection d'intrusion
```python
from collections import defaultdict
from datetime import datetime, timedelta

class IntrusionDetection:
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = set()
    
    def record_failed_attempt(self, ip_address: str):
        current_time = datetime.utcnow()
        self.failed_attempts[ip_address].append(current_time)
        
        # Nettoyer les tentatives anciennes (> 15 minutes)
        cutoff_time = current_time - timedelta(minutes=15)
        self.failed_attempts[ip_address] = [
            attempt for attempt in self.failed_attempts[ip_address]
            if attempt > cutoff_time
        ]
        
        # Bloquer après 5 tentatives échouées
        if len(self.failed_attempts[ip_address]) >= 5:
            self.blocked_ips.add(ip_address)
            logger.warning(f"IP {ip_address} blocked due to multiple failed attempts")
    
    def is_blocked(self, ip_address: str) -> bool:
        return ip_address in self.blocked_ips
```

### Monitoring de sécurité avec Prometheus
```python
from prometheus_client import Counter, Histogram

# Métriques de sécurité
SECURITY_EVENTS = Counter('security_events_total', 'Total security events', ['event_type'])
FAILED_LOGINS = Counter('failed_logins_total', 'Total failed login attempts', ['ip_address'])
AUTH_DURATION = Histogram('auth_duration_seconds', 'Authentication duration')

# Dans le code d'authentification
@AUTH_DURATION.time()
async def authenticate_user(username: str, password: str):
    try:
        # Logique d'authentification
        return user
    except AuthenticationError:
        FAILED_LOGINS.labels(ip_address=request.client.host).inc()
        SECURITY_EVENTS.labels(event_type='failed_login').inc()
        raise
```

## 🚨 Réponse aux incidents

### Plan de réponse aux incidents
1. **Détection**: Monitoring automatisé et alertes
2. **Analyse**: Évaluation de l'impact et de la portée
3. **Containment**: Isolation de la menace
4. **Éradication**: Suppression de la menace
5. **Récupération**: Restauration des services
6. **Lessons Learned**: Analyse post-incident

### Procédures d'urgence
```bash
# Script d'urgence - Bloquer le trafic suspect
#!/bin/bash

# Bloquer une IP suspecte
block_ip() {
    local IP=$1
    kubectl patch networkpolicy library-management-netpol \
      --type='json' \
      -p='[{"op": "add", "path": "/spec/ingress/0/from/0/ipBlock/except/-", "value": "'$IP'"}]'
}

# Activer le mode maintenance
enable_maintenance_mode() {
    kubectl scale deployment library-management-prod --replicas=0
    kubectl apply -f maintenance-page.yaml
}

# Rotation d'urgence des secrets
emergency_secret_rotation() {
    kubectl delete secret app-secrets
    kubectl create secret generic app-secrets \
      --from-literal=secret_key="$(openssl rand -base64 32)" \
      --from-literal=jwt_secret="$(openssl rand -base64 32)"
    kubectl rollout restart deployment/library-management-prod
}
```

## 🔧 Audit de sécurité

### Checklist de sécurité
- [ ] **Authentification forte** implémentée
- [ ] **Autorisation granulaire** configurée
- [ ] **Chiffrement** des données en transit et au repos
- [ ] **Validation** stricte des entrées utilisateur
- [ ] **Logging de sécurité** complet
- [ ] **Monitoring** des événements suspects
- [ ] **Secrets** gérés de manière sécurisée
- [ ] **Network policies** restrictives
- [ ] **Pod security policies** appliquées
- [ ] **RBAC** avec principe du moindre privilège
- [ ] **Certificats TLS** valides et à jour
- [ ] **Sauvegardes** chiffrées et testées

### Outils de scan de sécurité
```bash
# Scan des vulnérabilités des images Docker
trivy image library-management-system:latest

# Analyse de sécurité du code
bandit -r backend/

# Scan des secrets dans le code
truffleHog --regex --entropy=False .

# Test de pénétration automatisé
zap-full-scan.py -t https://library.example.com
```

### Tests de sécurité automatisés
```python
# tests/test_security.py
import pytest
from fastapi.testclient import TestClient

def test_sql_injection_protection():
    """Test protection contre l'injection SQL"""
    malicious_input = "'; DROP TABLE users; --"
    response = client.get(f"/users/?search={malicious_input}")
    assert response.status_code == 400  # Bad request

def test_xss_protection():
    """Test protection contre XSS"""
    malicious_script = "<script>alert('xss')</script>"
    response = client.post("/books/", json={
        "title": malicious_script,
        "author": "Test Author"
    })
    assert malicious_script not in response.text

def test_rate_limiting():
    """Test limitation du taux de requêtes"""
    for _ in range(10):  # Dépasser la limite
        response = client.post("/auth/login", json={
            "username": "test",
            "password": "test"
        })
    assert response.status_code == 429  # Too Many Requests
```

## 📚 Formation et sensibilisation

### Formation développeurs
1. **OWASP Top 10**: Vulnérabilités web les plus critiques
2. **Secure Coding**: Pratiques de développement sécurisé
3. **Cryptographie**: Utilisation correcte des algorithmes
4. **Testing de sécurité**: Tests automatisés et manuels

### Processus de développement sécurisé
1. **Threat Modeling**: Analyse des menaces dès la conception
2. **Security Reviews**: Revue de code axée sécurité
3. **Penetration Testing**: Tests d'intrusion réguliers
4. **Vulnerability Management**: Gestion des vulnérabilités

## 🔗 Références et ressources

- [OWASP Application Security Guide](https://owasp.org/www-guide/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [SANS Secure Coding Practices](https://www.sans.org/white-papers/2172/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

*Ce document doit être régulièrement mis à jour pour refléter les dernières menaces et meilleures pratiques de sécurité.*