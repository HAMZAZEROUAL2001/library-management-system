# Guide de Troubleshooting - Library Management System

Ce guide de dépannage vous aide à diagnostiquer et résoudre les problèmes courants du système de gestion de bibliothèque.

## 🔍 Méthodologie de diagnostic

### Approche structurée
1. **Identifier**: Reproduire et caractériser le problème
2. **Localiser**: Déterminer la couche affectée (frontend, backend, base de données, infrastructure)
3. **Analyser**: Examiner les logs, métriques et état du système
4. **Résoudre**: Appliquer la solution appropriée
5. **Vérifier**: Confirmer la résolution et documenter

### Outils de diagnostic essentiels
```bash
# Kubernetes
kubectl get pods,svc,ingress -n <namespace>
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --tail=100 -f

# Docker
docker ps
docker logs <container-id> --tail=100 -f
docker exec -it <container-id> /bin/bash

# Réseau
curl -v https://library.example.com/health
nslookup library.example.com
telnet <host> <port>

# Système
top, htop
free -h
df -h
netstat -tlnp
```

## 🚨 Problèmes courants et solutions

### 1. Application ne démarre pas

#### Symptômes
- Pods en état `CrashLoopBackOff`
- Erreurs dans les logs au démarrage
- Health checks échouent

#### Diagnostic
```bash
# Vérifier l'état des pods
kubectl get pods -n library-management-prod

# Examiner les logs de démarrage
kubectl logs <pod-name> -n library-management-prod --previous

# Vérifier la configuration
kubectl describe pod <pod-name> -n library-management-prod
```

#### Solutions courantes

**Configuration manquante**
```bash
# Vérifier les ConfigMaps et Secrets
kubectl get configmaps,secrets -n library-management-prod

# Vérifier le contenu
kubectl describe configmap app-config -n library-management-prod
kubectl get secret app-secrets -n library-management-prod -o yaml
```

**Problème de base de données**
```bash
# Tester la connectivité DB
kubectl run test-db --rm -it --image=postgres:13 -- psql -h <db-host> -U <username> -d <database>

# Vérifier les migrations
kubectl exec -it <pod-name> -n library-management-prod -- python -c "
from backend.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    print(result.fetchone())
"
```

**Ressources insuffisantes**
```bash
# Vérifier les ressources du nœud
kubectl describe node <node-name>

# Augmenter les ressources temporairement
kubectl patch deployment library-management-prod -p '{"spec":{"template":{"spec":{"containers":[{"name":"library-app","resources":{"limits":{"memory":"1Gi","cpu":"1000m"}}}]}}}}'
```

### 2. Problèmes de performance

#### Symptômes
- Temps de réponse élevés (> 2s)
- Timeouts fréquents
- Utilisation CPU/mémoire élevée

#### Diagnostic
```bash
# Métriques en temps réel
kubectl top pods -n library-management-prod

# Profiling de l'application
kubectl port-forward <pod-name> 8080:8000 -n library-management-prod
curl http://localhost:8080/debug/profiler

# Analyse des requêtes lentes
kubectl logs <pod-name> -n library-management-prod | grep "slow query"
```

#### Solutions

**Optimisation base de données**
```sql
-- Identifier les requêtes lentes
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Ajouter des index manquants
CREATE INDEX CONCURRENTLY idx_books_title ON books(title);
CREATE INDEX CONCURRENTLY idx_loans_status ON loans(status);

-- Analyser les statistiques
ANALYZE books, loans, users;
```

**Mise à jour des ressources**
```yaml
# environments/prod.tfvars
resource_limits = {
  prod = {
    cpu_request    = "1000m"
    memory_request = "1Gi"
    cpu_limit      = "2000m"
    memory_limit   = "2Gi"
  }
}
```

**Configuration du cache**
```python
# backend/cache.py
from functools import lru_cache
import redis

redis_client = redis.Redis(host='redis-service', port=6379, db=0)

@lru_cache(maxsize=128)
def get_popular_books():
    # Mise en cache des requêtes fréquentes
    return popular_books_query()
```

### 3. Problèmes d'authentification

#### Symptômes
- Erreurs 401 Unauthorized
- Tokens JWT invalides
- Sessions expirées prématurément

#### Diagnostic
```bash
# Tester l'endpoint d'authentification
curl -X POST https://library.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  -v

# Vérifier la configuration JWT
kubectl exec -it <pod-name> -n library-management-prod -- python -c "
import os
print('SECRET_KEY:', 'SET' if os.getenv('SECRET_KEY') else 'NOT SET')
print('JWT_SECRET_KEY:', 'SET' if os.getenv('JWT_SECRET_KEY') else 'NOT SET')
"
```

#### Solutions

**Secrets corrompus ou manquants**
```bash
# Regenerer les secrets
kubectl delete secret app-secrets -n library-management-prod
kubectl create secret generic app-secrets \
  --from-literal=secret_key="$(openssl rand -base64 32)" \
  --from-literal=jwt_secret="$(openssl rand -base64 32)" \
  -n library-management-prod

# Redémarrer l'application
kubectl rollout restart deployment/library-management-prod -n library-management-prod
```

**Synchronisation des horloges**
```bash
# Vérifier la synchronisation NTP
kubectl exec -it <pod-name> -n library-management-prod -- date
timedatectl status

# Ajuster la durée de vie des tokens si nécessaire
# Dans backend/auth.py
JWT_EXPIRATION_TIME = timedelta(hours=2)  # Augmenter temporairement
```

### 4. Problèmes réseau et connectivité

#### Symptômes
- Service inaccessible de l'extérieur
- Erreurs de DNS
- Timeouts de connexion

#### Diagnostic
```bash
# Vérifier les services
kubectl get svc -n library-management-prod

# Tester la connectivité interne
kubectl run test-pod --rm -it --image=busybox -- nslookup library-management-service.library-management-prod.svc.cluster.local

# Vérifier l'Ingress
kubectl describe ingress library-management-ingress -n library-management-prod

# Tester depuis l'extérieur
curl -v --resolve library.example.com:443:<ingress-ip> https://library.example.com/health
```

#### Solutions

**Problème de DNS**
```bash
# Vérifier CoreDNS
kubectl get pods -n kube-system | grep coredns
kubectl logs -n kube-system <coredns-pod>

# Redémarrer CoreDNS si nécessaire
kubectl rollout restart deployment/coredns -n kube-system
```

**Configuration Ingress incorrecte**
```yaml
# Vérifier les annotations Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/rewrite-target: "/"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
```

**Problème de certificats**
```bash
# Vérifier les certificats
kubectl get certificates -n library-management-prod
kubectl describe certificate library-management-tls -n library-management-prod

# Forcer le renouvellement
kubectl delete certificate library-management-tls -n library-management-prod
```

### 5. Problèmes de base de données

#### Symptômes
- Erreurs de connexion DB
- Données corrompues
- Migrations échouées

#### Diagnostic
```bash
# Vérifier l'état de PostgreSQL
kubectl get pods -n database
kubectl logs postgresql-0 -n database

# Tester la connectivité
kubectl exec -it postgresql-0 -n database -- psql -U postgres -l

# Vérifier l'espace disque
kubectl exec -it postgresql-0 -n database -- df -h
```

#### Solutions

**Connexions DB épuisées**
```sql
-- Vérifier les connexions actives
SELECT count(*) FROM pg_stat_activity;

-- Augmenter max_connections si nécessaire
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();
```

**Migration échouée**
```bash
# Rollback de la migration
kubectl exec -it <pod-name> -n library-management-prod -- alembic downgrade -1

# Corriger manuellement si nécessaire
kubectl exec -it postgresql-0 -n database -- psql -U postgres -d library_prod -c "
-- Commandes SQL pour corriger l'état
"

# Re-exécuter la migration
kubectl exec -it <pod-name> -n library-management-prod -- alembic upgrade head
```

**Espace disque insuffisant**
```bash
# Nettoyer les logs anciens
kubectl exec -it postgresql-0 -n database -- find /var/log -name "*.log" -mtime +7 -delete

# Augmenter la taille du volume (si supporté)
kubectl patch pvc postgres-data -p '{"spec":{"resources":{"requests":{"storage":"100Gi"}}}}'
```

## 📊 Monitoring et alertes

### Métriques clés à surveiller

**Application**
```promql
# Taux de succès des requêtes HTTP
rate(http_requests_total{status!~"5.."}[5m]) / rate(http_requests_total[5m]) * 100

# Temps de réponse 95e percentile
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Nombre d'utilisateurs connectés
active_users_total
```

**Infrastructure**
```promql
# Utilisation CPU des pods
rate(container_cpu_usage_seconds_total[5m]) * 100

# Utilisation mémoire
container_memory_usage_bytes / container_spec_memory_limit_bytes * 100

# Disponibilité du service
up{job="library-management-api"}
```

### Alertes critiques

**Configuration Alertmanager**
```yaml
groups:
- name: library_critical
  rules:
  - alert: ApplicationDown
    expr: up{job="library-management-api"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Application inaccessible"
      description: "L'application est down depuis plus d'1 minute"

  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Taux d'erreur élevé"
      description: "Taux d'erreur: {{ $value }}%"
```

## 🛠️ Scripts de diagnostic automatisé

### Script de diagnostic complet
```bash
#!/bin/bash
# diagnose.sh - Script de diagnostic automatisé

NAMESPACE=${1:-library-management-prod}
LOGFILE="diagnostic-$(date +%Y%m%d-%H%M%S).log"

echo "=== DIAGNOSTIC LIBRARY MANAGEMENT SYSTEM ===" | tee -a $LOGFILE
echo "Namespace: $NAMESPACE" | tee -a $LOGFILE
echo "Timestamp: $(date)" | tee -a $LOGFILE
echo "" | tee -a $LOGFILE

# 1. État général des ressources
echo "1. ÉTAT DES RESSOURCES" | tee -a $LOGFILE
kubectl get pods,svc,ingress,configmaps,secrets -n $NAMESPACE | tee -a $LOGFILE
echo "" | tee -a $LOGFILE

# 2. Événements récents
echo "2. ÉVÉNEMENTS RÉCENTS" | tee -a $LOGFILE
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10 | tee -a $LOGFILE
echo "" | tee -a $LOGFILE

# 3. Logs des pods en erreur
echo "3. LOGS DES PODS PROBLÉMATIQUES" | tee -a $LOGFILE
for pod in $(kubectl get pods -n $NAMESPACE -o name | grep -v Running); do
    echo "--- Logs de $pod ---" | tee -a $LOGFILE
    kubectl logs $pod -n $NAMESPACE --tail=20 | tee -a $LOGFILE
    echo "" | tee -a $LOGFILE
done

# 4. Utilisation des ressources
echo "4. UTILISATION DES RESSOURCES" | tee -a $LOGFILE
kubectl top pods -n $NAMESPACE | tee -a $LOGFILE
echo "" | tee -a $LOGFILE

# 5. Tests de connectivité
echo "5. TESTS DE CONNECTIVITÉ" | tee -a $LOGFILE
SERVICE_NAME=$(kubectl get svc -n $NAMESPACE -o name | head -1 | cut -d'/' -f2)
kubectl run connectivity-test --rm -it --image=busybox --restart=Never -- wget -qO- http://$SERVICE_NAME.$NAMESPACE.svc.cluster.local/health 2>&1 | tee -a $LOGFILE

echo "" | tee -a $LOGFILE
echo "Diagnostic terminé. Résultats sauvegardés dans $LOGFILE"
```

### Script de récupération d'urgence
```bash
#!/bin/bash
# emergency-recovery.sh - Récupération d'urgence

NAMESPACE=${1:-library-management-prod}

echo "PROCÉDURE DE RÉCUPÉRATION D'URGENCE"
echo "Namespace: $NAMESPACE"

# 1. Redémarrer tous les pods
echo "1. Redémarrage des deployments..."
kubectl rollout restart deployment -n $NAMESPACE

# 2. Vérifier les secrets critiques
echo "2. Vérification des secrets..."
kubectl get secrets -n $NAMESPACE

# 3. Nettoyer les pods en erreur
echo "3. Nettoyage des pods en erreur..."
kubectl delete pods --field-selector=status.phase=Failed -n $NAMESPACE

# 4. Attendre la stabilisation
echo "4. Attente de la stabilisation..."
kubectl wait --for=condition=ready pod -l app=library-management -n $NAMESPACE --timeout=300s

# 5. Test de santé
echo "5. Test de santé..."
SERVICE_IP=$(kubectl get svc -n $NAMESPACE -o jsonpath='{.items[0].spec.clusterIP}')
kubectl run health-check --rm -it --image=busybox --restart=Never -- wget -qO- http://$SERVICE_IP/health

echo "Récupération terminée."
```

## 📱 Monitoring en temps réel

### Dashboard de statut
```bash
#!/bin/bash
# status-dashboard.sh - Dashboard temps réel

watch -n 5 "
echo '=== LIBRARY MANAGEMENT SYSTEM STATUS ==='
echo 'Timestamp: $(date)'
echo ''
echo 'PODS STATUS:'
kubectl get pods -n library-management-prod
echo ''
echo 'RESOURCE USAGE:'
kubectl top pods -n library-management-prod
echo ''
echo 'RECENT EVENTS:'
kubectl get events -n library-management-prod --sort-by='.lastTimestamp' | tail -5
echo ''
echo 'ENDPOINTS HEALTH:'
curl -s -o /dev/null -w 'Health endpoint: %{http_code} (%{time_total}s)' https://library.example.com/health || echo 'Health endpoint: FAILED'
"
```

## 🔧 Outils de maintenance

### Nettoyage automatisé
```bash
#!/bin/bash
# cleanup.sh - Nettoyage maintenance

NAMESPACE=${1:-library-management-prod}

echo "Nettoyage de maintenance pour $NAMESPACE"

# Nettoyer les pods terminés
kubectl delete pods --field-selector=status.phase=Succeeded -n $NAMESPACE

# Nettoyer les jobs anciens
kubectl delete jobs --field-selector=status.conditions[].type=Complete -n $NAMESPACE

# Nettoyer les événements anciens
kubectl delete events --field-selector=reason=Killing -n $NAMESPACE

# Rotation des logs si nécessaire
kubectl exec -it $(kubectl get pods -n $NAMESPACE -l app=library-management -o name | head -1) -n $NAMESPACE -- find /app/logs -name "*.log" -mtime +7 -delete

echo "Nettoyage terminé."
```

## 📞 Escalade et support

### Niveaux de support
- **Niveau 1**: Redémarrage services, vérifications basiques
- **Niveau 2**: Analyse logs, diagnostic infrastructure  
- **Niveau 3**: Modification code, architecture

### Contacts d'urgence
- **DevOps Team**: devops@example.com
- **Dev Team**: dev@example.com
- **Infrastructure**: infra@example.com

### Procédure d'escalade
1. Tentative de résolution automatisée
2. Diagnostic manuel (15 min max)
3. Escalade Niveau 2 si non résolu
4. Notification parties prenantes si impact critique

---

Ce guide de troubleshooting doit être maintenu à jour avec les nouveaux problèmes rencontrés et leurs solutions.