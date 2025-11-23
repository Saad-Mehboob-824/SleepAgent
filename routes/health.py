"""
Health check routes for Worker Agent.
"""
from flask import Blueprint, jsonify
import psutil
import time
from datetime import datetime
from config import Config
from memory.storage import storage

health_bp = Blueprint('health', __name__)

# Track start time
START_TIME = time.time()

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        uptime = time.time() - START_TIME
        
        # Get system stats
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Check storage
        try:
            storage_healthy = True
            user_count = len(storage.list_users())
        except Exception as e:
            storage_healthy = False
            user_count = 0
        
        return jsonify({
            'status': 'healthy',
            'agent': Config.AGENT_NAME,
            'agent_id': Config.AGENT_ID,
            'version': Config.AGENT_VERSION,
            'uptime_seconds': round(uptime, 2),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'storage_healthy': storage_healthy,
            'user_count': user_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503
