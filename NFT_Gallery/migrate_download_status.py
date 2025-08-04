#!/usr/bin/env python3
"""
Migration script to add download status fields to existing Firestore documents.
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.firestore_manager import FirestoreManager


def setup_logging():
    """Setup logging for the migration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def migrate_download_status():
    """Migrate existing Firestore documents to include download status fields."""
    logger = setup_logging()
    
    try:
        logger.info("Starting download status migration...")
        
        # Initialize Firestore manager
        firestore_manager = FirestoreManager()
        
        # Get all documents
        logger.info("Fetching all documents from Firestore...")
        docs = list(firestore_manager.collection.stream())
        
        if not docs:
            logger.info("No documents found to migrate")
            return
        
        logger.info(f"Found {len(docs)} documents to migrate")
        
        # Prepare migration data
        migration_data = {
            "download_status": "pending",
            "download_attempts": 0,
            "download_error": None,
            "local_file_path": None,
            "file_size": None,
            "download_completed_at": None,
            "last_download_attempt": None,
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Process documents in batches
        batch_size = 500  # Firestore batch limit
        total_updated = 0
        
        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i:i + batch_size]
            batch = firestore_manager.db.batch()
            batch_count = 0
            
            for doc in batch_docs:
                doc_data = doc.to_dict()
                
                # Check if document already has download status fields
                if "download_status" not in doc_data:
                    batch.update(doc.reference, migration_data)
                    batch_count += 1
            
            if batch_count > 0:
                # Commit batch
                batch.commit()
                total_updated += batch_count
                logger.info(f"Updated batch {i//batch_size + 1}: {batch_count} documents")
            else:
                logger.info(f"Batch {i//batch_size + 1}: No documents needed updating")
        
        logger.info(f"Migration completed! Updated {total_updated} documents")
        
        # Verify migration
        logger.info("Verifying migration...")
        verify_migration(firestore_manager, logger)
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    return True


def verify_migration(firestore_manager, logger):
    """Verify that the migration was successful."""
    try:
        # Get download statistics
        stats = firestore_manager.get_download_statistics()
        
        logger.info("=== Migration Verification ===")
        logger.info(f"Total Documents: {stats.get('total_documents', 0)}")
        logger.info(f"Pending Downloads: {stats.get('pending_downloads', 0)}")
        logger.info(f"Downloading: {stats.get('downloading', 0)}")
        logger.info(f"Completed Downloads: {stats.get('completed_downloads', 0)}")
        logger.info(f"Failed Downloads: {stats.get('failed_downloads', 0)}")
        
        # Check if all documents have download status
        total_docs = stats.get('total_documents', 0)
        pending_docs = stats.get('pending_downloads', 0)
        
        if total_docs > 0 and pending_docs == total_docs:
            logger.info("✅ Migration successful: All documents have download status fields")
        else:
            logger.warning("⚠️  Migration may be incomplete: Some documents may not have download status fields")
        
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")


def reset_download_status():
    """Reset download status for all documents (useful for testing)."""
    logger = setup_logging()
    
    try:
        logger.info("Starting download status reset...")
        
        # Initialize Firestore manager
        firestore_manager = FirestoreManager()
        
        # Reset all documents
        updated_count = firestore_manager.reset_download_status()
        
        logger.info(f"Reset completed! Updated {updated_count} documents")
        
        # Verify reset
        verify_migration(firestore_manager, logger)
        
    except Exception as e:
        logger.error(f"Reset failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate Firestore documents for download status")
    parser.add_argument("--reset", action="store_true", help="Reset download status for all documents")
    
    args = parser.parse_args()
    
    if args.reset:
        print("=== Download Status Reset ===")
        if reset_download_status():
            print("✅ Reset completed successfully")
        else:
            print("❌ Reset failed")
            sys.exit(1)
    else:
        print("=== Download Status Migration ===")
        if migrate_download_status():
            print("✅ Migration completed successfully")
        else:
            print("❌ Migration failed")
            sys.exit(1) 