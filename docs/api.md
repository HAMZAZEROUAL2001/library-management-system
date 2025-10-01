# Documentation API

Cette documentation détaille toutes les endpoints de l'API REST du système de gestion de bibliothèque.

## Base URL

- **Développement** : `http://localhost:8000`
- **Production** : `https://api.yourdomain.com`

## Authentification

L'API utilise JWT (JSON Web Tokens) pour l'authentification. Tous les endpoints protégés nécessitent un header `Authorization`.

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Authentification

#### POST /register
Créer un nouveau compte utilisateur.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true
}
```

**Erreurs possibles:**
- `400` : Données invalides
- `409` : Utilisateur déjà existant

---

#### POST /token
Obtenir un token d'authentification.

**Request Body (form-data):**
```
username: john_doe
password: securepassword123
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Erreurs possibles:**
- `401` : Identifiants incorrects

---

#### GET /users/me
Obtenir les informations de l'utilisateur connecté.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true
}
```

---

### Gestion des livres

#### GET /books
Lister tous les livres avec pagination.

**Query Parameters:**
- `skip` (int, optional) : Nombre d'éléments à ignorer (défaut: 0)
- `limit` (int, optional) : Nombre maximum d'éléments (défaut: 100)

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Python Programming",
    "author": "John Smith",
    "isbn": "978-0123456789",
    "available": true,
    "created_at": "2024-01-15T10:30:00"
  },
  {
    "id": 2,
    "title": "JavaScript Essentials",
    "author": "Jane Doe",
    "isbn": "978-0987654321",
    "available": false,
    "created_at": "2024-01-16T14:20:00"
  }
]
```

---

#### GET /books/{book_id}
Obtenir un livre spécifique par son ID.

**Path Parameters:**
- `book_id` (int) : ID du livre

**Response (200):**
```json
{
  "id": 1,
  "title": "Python Programming",
  "author": "John Smith",
  "isbn": "978-0123456789",
  "available": true,
  "created_at": "2024-01-15T10:30:00"
}
```

**Erreurs possibles:**
- `404` : Livre non trouvé

---

#### POST /books
Créer un nouveau livre.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "Advanced Python",
  "author": "Bob Johnson",
  "isbn": "978-0111222333"
}
```

**Response (201):**
```json
{
  "id": 3,
  "title": "Advanced Python",
  "author": "Bob Johnson",
  "isbn": "978-0111222333",
  "available": true,
  "created_at": "2024-01-17T09:15:00"
}
```

**Erreurs possibles:**
- `400` : Données invalides
- `401` : Non authentifié
- `409` : ISBN déjà existant

---

#### PUT /books/{book_id}
Modifier un livre existant.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `book_id` (int) : ID du livre

**Request Body:**
```json
{
  "title": "Advanced Python Programming",
  "author": "Bob Johnson",
  "isbn": "978-0111222333",
  "available": false
}
```

**Response (200):**
```json
{
  "id": 3,
  "title": "Advanced Python Programming",
  "author": "Bob Johnson",
  "isbn": "978-0111222333",
  "available": false,
  "created_at": "2024-01-17T09:15:00"
}
```

**Erreurs possibles:**
- `400` : Données invalides
- `401` : Non authentifié
- `404` : Livre non trouvé

---

#### DELETE /books/{book_id}
Supprimer un livre.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `book_id` (int) : ID du livre

**Response (204):** Pas de contenu

**Erreurs possibles:**
- `401` : Non authentifié
- `404` : Livre non trouvé
- `409` : Livre actuellement emprunté

---

#### GET /books/search
Rechercher des livres par titre, auteur ou ISBN.

**Query Parameters:**
- `q` (string) : Terme de recherche
- `skip` (int, optional) : Pagination (défaut: 0)
- `limit` (int, optional) : Limite (défaut: 100)

**Exemple:** `/books/search?q=python&limit=10`

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Python Programming",
    "author": "John Smith",
    "isbn": "978-0123456789",
    "available": true,
    "created_at": "2024-01-15T10:30:00"
  }
]
```

---

### Gestion des emprunts

#### GET /loans
Lister tous les emprunts (admin).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int, optional) : Pagination (défaut: 0)
- `limit` (int, optional) : Limite (défaut: 100)

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "book_id": 2,
    "loan_date": "2024-01-18T10:00:00",
    "return_date": null,
    "is_returned": false,
    "book": {
      "id": 2,
      "title": "JavaScript Essentials",
      "author": "Jane Doe",
      "isbn": "978-0987654321"
    },
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    }
  }
]
```

---

#### GET /loans/my-loans
Lister les emprunts de l'utilisateur connecté.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int, optional) : Pagination (défaut: 0)
- `limit` (int, optional) : Limite (défaut: 100)

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "book_id": 2,
    "loan_date": "2024-01-18T10:00:00",
    "return_date": null,
    "is_returned": false,
    "book": {
      "id": 2,
      "title": "JavaScript Essentials",
      "author": "Jane Doe",
      "isbn": "978-0987654321"
    }
  }
]
```

---

#### POST /loans
Emprunter un livre.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "book_id": 1
}
```

**Response (201):**
```json
{
  "id": 2,
  "user_id": 1,
  "book_id": 1,
  "loan_date": "2024-01-19T11:30:00",
  "return_date": null,
  "is_returned": false,
  "book": {
    "id": 1,
    "title": "Python Programming",
    "author": "John Smith",
    "isbn": "978-0123456789"
  }
}
```

**Erreurs possibles:**
- `400` : Livre non disponible ou déjà emprunté par cet utilisateur
- `401` : Non authentifié
- `404` : Livre non trouvé

---

#### PATCH /loans/{loan_id}/return
Retourner un livre emprunté.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `loan_id` (int) : ID de l'emprunt

**Response (200):**
```json
{
  "id": 2,
  "user_id": 1,
  "book_id": 1,
  "loan_date": "2024-01-19T11:30:00",
  "return_date": "2024-01-25T16:45:00",
  "is_returned": true,
  "book": {
    "id": 1,
    "title": "Python Programming",
    "author": "John Smith",
    "isbn": "978-0123456789"
  }
}
```

**Erreurs possibles:**
- `400` : Livre déjà retourné
- `401` : Non authentifié
- `403` : Emprunt appartenant à un autre utilisateur
- `404` : Emprunt non trouvé

---

### Statistiques

#### GET /stats
Obtenir les statistiques de la bibliothèque.

**Response (200):**
```json
{
  "total_books": 150,
  "available_books": 127,
  "total_loans": 423,
  "active_loans": 23
}
```

---

## Codes de statut HTTP

| Code | Signification | Description |
|------|---------------|-------------|
| 200 | OK | Requête réussie |
| 201 | Created | Ressource créée avec succès |
| 204 | No Content | Requête réussie, pas de contenu |
| 400 | Bad Request | Données de requête invalides |
| 401 | Unauthorized | Authentification requise |
| 403 | Forbidden | Accès interdit |
| 404 | Not Found | Ressource non trouvée |
| 409 | Conflict | Conflit avec l'état actuel |
| 422 | Unprocessable Entity | Erreur de validation |
| 500 | Internal Server Error | Erreur serveur |

## Format des erreurs

Toutes les erreurs suivent le même format :

```json
{
  "detail": "Description de l'erreur"
}
```

### Exemples d'erreurs

#### 400 - Bad Request
```json
{
  "detail": "Le livre n'est pas disponible pour l'emprunt"
}
```

#### 401 - Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### 404 - Not Found
```json
{
  "detail": "Livre non trouvé"
}
```

#### 422 - Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Exemples d'utilisation

### Authentification complète

```bash
# 1. Inscription
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "alicepassword"
  }'

# 2. Connexion
TOKEN=$(curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=alicepassword" \
  | jq -r '.access_token')

# 3. Utilisation du token
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

### Gestion des livres

```bash
# Créer un livre
curl -X POST "http://localhost:8000/books" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert Martin",
    "isbn": "978-0132350884"
  }'

# Rechercher des livres
curl -X GET "http://localhost:8000/books/search?q=clean&limit=5" \
  -H "Authorization: Bearer $TOKEN"

# Emprunter un livre
curl -X POST "http://localhost:8000/loans" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1}'
```

## Limites et quotas

- **Pagination** : Maximum 100 éléments par page
- **Recherche** : Minimum 3 caractères pour la recherche
- **Token JWT** : Expire après 30 minutes par défaut
- **Rate limiting** : Non implémenté (recommandé pour la production)

## Webhooks (Futur)

Endpoints prévus pour les notifications :
- `POST /webhooks/book-returned` : Notification de retour de livre
- `POST /webhooks/loan-overdue` : Notification d'emprunt en retard

---

*Documentation API v1.0 - Compatible avec OpenAPI 3.0*

Pour une documentation interactive, visitez `/docs` sur votre instance de l'API.