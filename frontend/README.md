# Frontend - React avec TypeScript

Une interface utilisateur moderne pour le système de gestion de bibliothèque.

## Fonctionnalités

- **Authentification** : Connexion et inscription des utilisateurs
- **Tableau de bord** : Vue d'ensemble avec statistiques
- **Gestion des livres** : Ajout, modification, suppression et recherche
- **Emprunts** : Consultation et retour des livres empruntés
- **Interface responsive** : Compatible mobile et desktop

## Technologies

- React 18 avec TypeScript
- Material-UI (MUI) pour l'interface
- React Router pour la navigation
- Axios pour les appels API
- Context API pour la gestion d'état

## Installation

```bash
cd frontend
npm install
```

## Configuration

1. Copier le fichier `.env.example` vers `.env` :
```bash
cp .env.example .env
```

2. Modifier les variables d'environnement si nécessaire dans `.env`

## Démarrage

### Mode développement
```bash
npm start
```
L'application sera accessible sur http://localhost:3000

### Build pour production
```bash
npm run build
```

## Structure

```
src/
├── components/          # Composants React
│   ├── Dashboard.tsx    # Tableau de bord
│   ├── BooksPage.tsx    # Gestion des livres
│   ├── LoansPage.tsx    # Gestion des emprunts
│   ├── LoginPage.tsx    # Authentification
│   ├── Navbar.tsx       # Barre de navigation
│   └── ProtectedRoute.tsx # Route protégée
├── contexts/           # Contextes React
│   └── AuthContext.tsx # Gestion authentification
├── services/          # Services API
│   └── api.ts         # Client API
├── types/            # Types TypeScript
│   └── index.ts      # Définitions des types
├── App.tsx           # Composant principal
└── index.tsx         # Point d'entrée
```

## API

Le frontend communique avec l'API FastAPI via Axios. Toutes les requêtes sont interceptées pour ajouter automatiquement le token JWT.

### Endpoints utilisés

- `POST /token` - Authentification
- `POST /register` - Inscription
- `GET /users/me` - Utilisateur actuel
- `GET /books` - Liste des livres
- `POST /books` - Créer un livre
- `PUT /books/{id}` - Modifier un livre
- `DELETE /books/{id}` - Supprimer un livre
- `GET /books/search` - Rechercher des livres
- `GET /loans/my-loans` - Emprunts de l'utilisateur
- `POST /loans` - Créer un emprunt
- `PATCH /loans/{id}/return` - Retourner un livre
- `GET /stats` - Statistiques de la bibliothèque

## Authentification

L'authentification utilise JWT avec les fonctionnalités suivantes :
- Auto-login au chargement si token valide
- Redirection automatique si token expiré
- Stockage sécurisé du token dans localStorage
- Protection des routes avec ProtectedRoute

## Responsive Design

L'interface est entièrement responsive grâce à Material-UI :
- Grille adaptative pour les cartes
- Navigation mobile avec menu hamburger
- Composants optimisés pour tous écrans