# Monitoring Setup - Library Management System

Ce dossier contient la configuration complète pour le monitoring de l'application Library Management System avec Prometheus, Grafana, et Alertmanager.

## 🚀 Démarrage rapide

### 1. Démarrer l'infrastructure de monitoring

```bash
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. Accéder aux interfaces

- **Grafana**: http://localhost:3001
  - Utilisateur: `admin`
  - Mot de passe: `admin123`
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

### 3. Démarrer l'application avec métriques

```bash
cd ../backend
# Assurez-vous que l'application tourne sur le port 8000
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📊 Dashboards Grafana

### Dashboard principal: Library Management System
- **URL**: http://localhost:3001/d/library-management-dashboard
- **Métriques surveillées**:
  - Taux de requêtes HTTP
  - Temps de réponse (percentiles)
  - Statistiques métier (utilisateurs, livres, emprunts)
  - Utilisation des ressources système
  - Opérations base de données

## 🔔 Alertes configurées

### Alertes critiques
- **ApplicationDown**: Application indisponible > 1 minute
- **HighErrorRate**: Taux d'erreur > 10% pendant 2 minutes
- **DatabaseConnectionFailure**: Échec connexion DB > 5% pendant 1 minute

### Alertes d'avertissement
- **HighResponseTime**: Temps de réponse 95e percentile > 2s pendant 3 minutes
- **HighCPUUsage**: Utilisation CPU > 80% pendant 5 minutes
- **HighMemoryUsage**: Utilisation mémoire > 85% pendant 5 minutes

## 🔧 Configuration

### Structure des fichiers

```
monitoring/
├── docker-compose.monitoring.yml    # Configuration Docker Compose
├── prometheus.yml                   # Configuration Prometheus
├── alert_rules.yml                  # Règles d'alertes
├── alertmanager.yml                 # Configuration Alertmanager
└── grafana/
    ├── provisioning/
    │   ├── datasources/
    │   │   └── prometheus.yml       # Source de données Prometheus
    │   └── dashboards/
    │       └── dashboard.yml        # Configuration des dashboards
    └── dashboards/
        └── library-management-dashboard.json  # Dashboard principal
```

### Métriques personnalisées

L'application expose les métriques suivantes sur `/metrics`:

#### Métriques HTTP
- `http_requests_total`: Nombre total de requêtes HTTP
- `http_request_duration_seconds`: Durée des requêtes HTTP

#### Métriques métier
- `user_registrations_total`: Nombre d'inscriptions d'utilisateurs
- `book_operations_total`: Opérations sur les livres (ajout, suppression, etc.)
- `loan_operations_total`: Opérations d'emprunt
- `total_users`: Nombre total d'utilisateurs
- `total_books`: Nombre total de livres
- `active_loans`: Nombre d'emprunts actifs

#### Métriques système
- `cpu_usage_percent`: Utilisation CPU en pourcentage
- `memory_usage_percent`: Utilisation mémoire en pourcentage
- `disk_usage_percent`: Utilisation disque en pourcentage

#### Métriques base de données
- `database_operations_total`: Opérations sur la base de données

## 🔍 Requêtes Prometheus utiles

### Performance
```promql
# Taux de requêtes par seconde
rate(http_requests_total[5m])

# Temps de réponse médian
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))

# Taux d'erreur
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100
```

### Métriques métier
```promql
# Nouveaux utilisateurs par heure
increase(user_registrations_total[1h])

# Emprunts actifs
active_loans

# Taux d'utilisation des livres
active_loans / total_books * 100
```

## 🚨 Configuration des alertes

### Modification des seuils
Éditez `alert_rules.yml` pour ajuster les seuils d'alerte:

```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1  # 10%
  for: 2m
```

### Notifications
Configurez `alertmanager.yml` pour les notifications:

```yaml
- name: 'email-notifications'
  email_configs:
  - to: 'votre-email@example.com'
    subject: '[ALERT] {{ .GroupLabels.alertname }}'
```

## 🛠️ Maintenance

### Mise à jour des dashboards
1. Modifiez le fichier JSON dans `grafana/dashboards/`
2. Redémarrez Grafana: `docker-compose restart grafana`

### Sauvegarde des métriques
Les données Prometheus sont persistées dans le volume `prometheus_data`.

### Nettoyage
```bash
# Arrêter tous les services
docker-compose -f docker-compose.monitoring.yml down

# Supprimer les volumes (attention: perte de données)
docker-compose -f docker-compose.monitoring.yml down -v
```

## 📈 Bonnes pratiques

1. **Surveillance proactive**: Configurez des alertes avant que les problèmes n'impactent les utilisateurs
2. **Rétention des données**: Ajustez la rétention Prometheus selon vos besoins
3. **Sécurité**: Changez les mots de passe par défaut en production
4. **Monitoring des métriques**: Surveillez également Prometheus et Grafana
5. **Documentation**: Maintenez cette documentation à jour avec vos modifications

## 🔗 Liens utiles

- [Documentation Prometheus](https://prometheus.io/docs/)
- [Documentation Grafana](https://grafana.com/docs/)
- [Alertmanager Guide](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)