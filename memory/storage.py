"""
Memory storage layer using MongoDB.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from config import Config
from utils.logger import logger

class MongoMemoryStorage:
    """MongoDB-based memory storage."""
    
    def __init__(self):
        try:
            self.client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[Config.MONGODB_DB_NAME]
            self.collection = self.db['memory']
            
            # Create indexes
            self.collection.create_index([('user_id', 1), ('memory_type', 1)], unique=True)
            self.collection.create_index('updated_at')
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"MongoDB memory storage initialized: {Config.MONGODB_DB_NAME}")
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"MongoDB initialization error: {str(e)}")
            raise
    
    def save_memory(self, user_id: str, memory_type: str, data: Dict[str, Any]) -> bool:
        """Save memory data to MongoDB."""
        try:
            memory_doc = {
                'user_id': user_id,
                'memory_type': memory_type,
                'data': data,
                'timestamp': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Upsert: update if exists, insert if not
            result = self.collection.update_one(
                {'user_id': user_id, 'memory_type': memory_type},
                {'$set': memory_doc},
                upsert=True
            )
            
            logger.info(f"Saved {memory_type} memory for user {user_id}")
            return True
            
        except OperationFailure as e:
            logger.error(f"MongoDB operation failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error saving memory: {str(e)}")
            return False
    
    def get_memory(self, user_id: str, memory_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve memory data from MongoDB."""
        try:
            doc = self.collection.find_one(
                {'user_id': user_id, 'memory_type': memory_type}
            )
            
            if doc:
                return doc.get('data')
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {str(e)}")
            return None
    
    def delete_memory(self, user_id: str, memory_type: str) -> bool:
        """Delete memory data from MongoDB."""
        try:
            result = self.collection.delete_one(
                {'user_id': user_id, 'memory_type': memory_type}
            )
            
            if result.deleted_count > 0:
                logger.info(f"Deleted {memory_type} memory for user {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting memory: {str(e)}")
            return False
    
    def list_users(self) -> List[str]:
        """List all user IDs with stored memory."""
        try:
            user_ids = self.collection.distinct('user_id')
            return list(user_ids)
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return []
    
    def close(self):
        """Close MongoDB connection."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("MongoDB connection closed")

# Global storage instance
storage = MongoMemoryStorage()
