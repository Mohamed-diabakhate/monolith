"""
Celery worker for background task processing.
"""

import structlog
from app.tasks import celery_app
from app.config import settings

logger = structlog.get_logger()

if __name__ == "__main__":
    logger.info("Starting EstFor Asset Collection Worker")
    logger.info("Worker configuration", 
               broker_url=settings.CELERY_BROKER_URL,
               result_backend=settings.CELERY_RESULT_BACKEND)
    
    # Start the Celery worker
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=2",
        "--hostname=estfor-worker@%h"
    ]) 