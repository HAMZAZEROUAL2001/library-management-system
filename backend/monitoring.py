from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse
import time
import psutil
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Métriques personnalisées
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

DATABASE_OPERATIONS = Counter(
    'database_operations_total',
    'Total database operations',
    ['operation', 'table']
)

USER_REGISTRATIONS = Counter(
    'user_registrations_total',
    'Total user registrations'
)

BOOK_OPERATIONS = Counter(
    'book_operations_total',
    'Total book operations',
    ['operation']
)

LOAN_OPERATIONS = Counter(
    'loan_operations_total',
    'Total loan operations',
    ['operation']
)

SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

APPLICATION_INFO = Gauge(
    'application_info',
    'Application information',
    ['version', 'python_version']
)


class PrometheusMetrics:
    """Gestionnaire des métriques Prometheus"""
    
    def __init__(self):
        self.start_time = time.time()
        self._setup_application_info()
    
    def _setup_application_info(self):
        """Configurer les informations de l'application"""
        import sys
        APPLICATION_INFO.labels(
            version="1.0.0",
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        ).set(1)
    
    async def middleware(self, request: Request, call_next):
        """Middleware pour collecter les métriques HTTP"""
        start_time = time.time()
        
        # Incrémenter les connexions actives
        ACTIVE_CONNECTIONS.inc()
        
        try:
            response = await call_next(request)
            
            # Calculer la durée de la requête
            duration = time.time() - start_time
            
            # Extraire les informations de la requête
            method = request.method
            endpoint = self._get_endpoint_path(request)
            status_code = str(response.status_code)
            
            # Enregistrer les métriques
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
        
        except Exception as e:
            # Enregistrer les erreurs
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=self._get_endpoint_path(request),
                status_code="500"
            ).inc()
            raise
        
        finally:
            # Décrémenter les connexions actives
            ACTIVE_CONNECTIONS.dec()
    
    def _get_endpoint_path(self, request: Request) -> str:
        """Extraire le chemin de l'endpoint"""
        if hasattr(request, 'url') and hasattr(request.url, 'path'):
            path = request.url.path
            # Normaliser les chemins avec des IDs
            if '/books/' in path and path.split('/books/')[-1].isdigit():
                return '/books/{id}'
            elif '/loans/' in path and '/return' in path:
                return '/loans/{id}/return'
            elif '/loans/' in path and path.split('/loans/')[-1].isdigit():
                return '/loans/{id}'
            return path
        return "unknown"
    
    def record_user_registration(self):
        """Enregistrer une inscription utilisateur"""
        USER_REGISTRATIONS.inc()
    
    def record_book_operation(self, operation: str):
        """Enregistrer une opération sur les livres"""
        BOOK_OPERATIONS.labels(operation=operation).inc()
    
    def record_loan_operation(self, operation: str):
        """Enregistrer une opération d'emprunt"""
        LOAN_OPERATIONS.labels(operation=operation).inc()
    
    def record_database_operation(self, operation: str, table: str):
        """Enregistrer une opération de base de données"""
        DATABASE_OPERATIONS.labels(operation=operation, table=table).inc()
    
    def update_system_metrics(self):
        """Mettre à jour les métriques système"""
        try:
            # Utilisation mémoire
            memory_info = psutil.virtual_memory()
            SYSTEM_MEMORY_USAGE.set(memory_info.used)
            
            # Utilisation CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            SYSTEM_CPU_USAGE.set(cpu_percent)
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des métriques système: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Obtenir un résumé des métriques"""
        return {
            "uptime_seconds": time.time() - self.start_time,
            "active_connections": ACTIVE_CONNECTIONS._value._value,
            "total_requests": sum(REQUEST_COUNT._metrics.values()),
            "memory_usage_mb": psutil.virtual_memory().used / (1024 * 1024),
            "cpu_usage_percent": psutil.cpu_percent(),
        }


# Instance globale
metrics = PrometheusMetrics()


def get_metrics_endpoint():
    """Endpoint pour exposer les métriques Prometheus"""
    # Mettre à jour les métriques système avant de les exposer
    metrics.update_system_metrics()
    
    # Générer les métriques au format Prometheus
    return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Décorateurs pour instrumenter les fonctions
def track_database_operation(operation: str, table: str):
    """Décorateur pour tracker les opérations de base de données"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            metrics.record_database_operation(operation, table)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def track_book_operation(operation: str):
    """Décorateur pour tracker les opérations sur les livres"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            metrics.record_book_operation(operation)
            return result
        return wrapper
    return decorator


def track_loan_operation(operation: str):
    """Décorateur pour tracker les opérations d'emprunt"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            metrics.record_loan_operation(operation)
            return result
        return wrapper
    return decorator


# Fonctions utilitaires pour l'instrumentation manuelle
def increment_user_registrations():
    """Incrémenter le compteur d'inscriptions"""
    metrics.record_user_registration()


def increment_book_created():
    """Incrémenter le compteur de livres créés"""
    metrics.record_book_operation("created")


def increment_book_updated():
    """Incrémenter le compteur de livres mis à jour"""
    metrics.record_book_operation("updated")


def increment_book_deleted():
    """Incrémenter le compteur de livres supprimés"""
    metrics.record_book_operation("deleted")


def increment_loan_created():
    """Incrémenter le compteur d'emprunts créés"""
    metrics.record_loan_operation("created")


def increment_loan_returned():
    """Incrémenter le compteur de retours"""
    metrics.record_loan_operation("returned")