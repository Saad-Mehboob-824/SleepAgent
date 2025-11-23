"""
Configuration settings for the Sleep Optimizer Worker Agent.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the Flask application"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8000))
    
    # CORS configuration
    CORS_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://localhost:3002',
        'http://127.0.0.1:3002',
        '*'  # Allow all for development
    ]
    
    # MongoDB configuration
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'worker_db')
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Memory configuration
    MEMORY_STORAGE_PATH = os.environ.get('MEMORY_STORAGE_PATH') or os.path.join(BASE_DIR, 'instance', 'memory')
    STM_RETENTION_DAYS = int(os.environ.get('STM_RETENTION_DAYS', 7))
    LTM_RETENTION_DAYS = int(os.environ.get('LTM_RETENTION_DAYS', 365))
    
    # Gemini API configuration (optional)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    USE_GEMINI = os.environ.get('USE_GEMINI', 'False').lower() == 'true' and bool(GEMINI_API_KEY)
    
    # Agent configuration
    AGENT_ID = os.environ.get('AGENT_ID') or 'sleep-optimizer-agent-001'
    AGENT_VERSION = os.environ.get('AGENT_VERSION') or '1.0.0'
    AGENT_NAME = 'Sleep Optimizer Agent'
    AGENT_NAME = 'Sleep Optimizer Agent'
    AGENT_DESCRIPTION = 'AI-powered sleep analysis and recommendation agent'
    
    # Supervisor configuration
    SUPERVISOR_URL = os.environ.get('SUPERVISOR_URL') or 'http://localhost:5000'
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', os.path.join(BASE_DIR, 'instance', 'logs', 'agent.log'))
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # API configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Task processing configuration
    MAX_TASK_TIMEOUT = int(os.environ.get('MAX_TASK_TIMEOUT', 300))  # 5 minutes
    MAX_SLEEP_SESSIONS_PER_TASK = int(os.environ.get('MAX_SLEEP_SESSIONS_PER_TASK', 1000))
    
    # Sleep analysis thresholds
    OPTIMAL_SLEEP_DURATION_MIN = 7.0
    OPTIMAL_SLEEP_DURATION_MAX = 9.0
    MIN_SLEEP_DURATION = 0.5  # Allow short naps (30 minutes minimum)
    MAX_SLEEP_DURATION = 16.0
    
    # Recommendation thresholds
    CAFFEINE_CUTOFF_HOURS = 8  # Hours before bedtime
    SCREEN_TIME_WARNING_HOURS = 2  # Hours before bedtime
    EXERCISE_CUTOFF_HOURS = 3  # Hours before bedtime

