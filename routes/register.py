"""
Agent registration endpoint - Returns agent capabilities and info.
"""
from flask import Blueprint, jsonify
from config import Config
from utils.logger import logger

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['POST'])
def register_agent():
    """
    Register the agent with the Supervisor.
    
    Returns:
        JSON response with agent information and capabilities
    """
    try:
        agent_info = {
            'agent_id': Config.AGENT_ID,
            'agent_name': Config.AGENT_NAME,
            'agent_description': Config.AGENT_DESCRIPTION,
            'version': Config.AGENT_VERSION,
            'capabilities': [
                'sleep_analysis',
                'sleep_scoring',
                'recommendation_generation',
                'memory_management',
                'trend_analysis',
                'personalized_planning'
            ],
            'endpoints': {
                'task': '/task',
                'health': '/health',
                'memory': '/memory',
                'logs': '/logs'
            },
            'supported_data_formats': {
                'sleep_sessions': [
                    'bedtime',
                    'waketime',
                    'duration_hours',
                    'efficiency_score',
                    'interruptions',
                    'morning_mood'
                ],
                'profile': [
                    'age',
                    'work_schedule',
                    'caffeine_intake',
                    'screen_time',
                    'exercise',
                    'stress_level'
                ]
            },
            'features': {
                'memory_system': True,
                'stm_retention_days': Config.STM_RETENTION_DAYS,
                'ltm_retention_days': Config.LTM_RETENTION_DAYS,
                'llm_support': Config.USE_GEMINI,
                'mongodb_support': Config.USE_MONGODB
            }
        }
        
        logger.info(f'Agent registration requested: {Config.AGENT_ID}')
        
        return jsonify(agent_info), 200
        
    except Exception as e:
        logger.error(f'Registration endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': {'message': str(e)}
        }), 500

