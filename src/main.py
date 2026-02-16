import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from src.shared.config import Config
from src.shared.logger import setup_logger
from src.providers.csv_reader import load_users_map
from src.providers.api_client import fetch_posts_stream
from src.core.transform import stream_enrichment
from src.storage.sqlite_repo import SQLiteRepository
from src.integrations.webhook_client import WebhookClient

def run_pipeline() -> None:
    """
    Exécute le flux ETL complet : Extraction, Transformation, Chargement.
    Le traitement est effectué en streaming pour optimiser la mémoire.
    """
    logger = setup_logger(__name__)
    logger.info("Démarrage du pipeline de traitement de données.")

    try:
        # Initialisation des composants et des accès aux données
        users_map = load_users_map(Config.USER_CSV_PATH)
        repo = SQLiteRepository(Config.DB_PATH)
        webhook = WebhookClient(Config.EXTERNAL_WEBHOOK_URL)
        
        # Buffer pour isoler l'échantillon à envoyer vers l'API externe
        sample_to_notify = []

        # Extraction des données via un générateur (Non-bloquant)
        posts_generator = fetch_posts_stream(Config.POSTS_API_URL, Config.CHUNK_SIZE)
        
        # Transformation et enrichissement à la volée
        enriched_stream = stream_enrichment(posts_generator, users_map)

        logger.info("Début du stockage par paquets (chunks)...")
        for chunk in enriched_stream:
            if not chunk:
                continue
            
            # Persistance immédiate pour libérer la mémoire
            repo.save_enriched_posts(chunk)
            
            # Collecte des 10 premiers enregistrements pour la notification
            if len(sample_to_notify) < 10:
                needed = 10 - len(sample_to_notify)
                sample_to_notify.extend(chunk[:needed])

        # Action finale : Notification des premiers résultats
        if sample_to_notify:
            logger.info("Transmission de l'échantillon au webhook externe.")
            webhook.send_sample(sample_to_notify)

        logger.info("Pipeline exécuté avec succès.")

    except Exception as e:
        logger.critical(f"Échec du pipeline : {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()