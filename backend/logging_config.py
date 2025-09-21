import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configuration du système de logging"""
    # Créer le répertoire de logs s'il n'existe pas
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Chemin du fichier de log
    log_file = os.path.join(log_dir, 'library_management.log')
    
    # Configuration du logger racine
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Affichage dans la console
            logging.StreamHandler(),
            # Écriture dans un fichier avec rotation
            RotatingFileHandler(
                log_file, 
                maxBytes=10*1024*1024,  # 10 Mo
                backupCount=5
            )
        ]
    )
    
    # Logger spécifique pour l'application
    logger = logging.getLogger('library_management')
    return logger

# Créer le logger global
logger = setup_logging()
