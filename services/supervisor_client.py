"""
Client for interacting with the Supervisor Agent API.
"""
import requests
from config import Config
from utils.logger import logger

class SupervisorClient:
    """Client for Supervisor Agent API."""
    
    def __init__(self):
        self.base_url = Config.SUPERVISOR_URL
        
    def verify_user(self, user_id):
        """Verify if a user exists."""
        try:
            response = requests.get(f"{self.base_url}/internal/api/verify_user/{user_id}")
            if response.status_code == 200:
                return response.json().get('valid', False)
            return False
        except Exception as e:
            logger.error(f"Error verifying user {user_id}: {str(e)}")
            return False

supervisor_client = SupervisorClient()
