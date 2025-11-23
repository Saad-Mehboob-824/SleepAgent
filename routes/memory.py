"""
Memory retrieval endpoint - Returns user memory data.
"""
from flask import Blueprint, jsonify, request
from memory.stm import ShortTermMemory
from memory.ltm import LongTermMemory
from utils.logger import logger, log_with_context

memory_bp = Blueprint('memory', __name__)
stm = ShortTermMemory()
ltm = LongTermMemory()

@memory_bp.route('/memory', methods=['GET'])
def get_memory():
    """
    Retrieve memory data for a specific user.
    
    Query Parameters:
        user_id (required): User identifier
    
    Returns:
        JSON response with STM and LTM data
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'error': 'Missing required parameter',
                'code': 'MISSING_PARAMETER',
                'details': {'parameter': 'user_id'}
            }), 400
        
        # Validate user_id - reject default_user
        if user_id == 'default_user' or user_id.strip() == '':
            log_with_context(logger, 'WARNING', f'Invalid user_id attempted in memory: {user_id}', 
                           user_id=user_id)
            return jsonify({
                'error': 'Invalid user_id. Please login through supervisor agent.',
                'code': 'INVALID_USER_ID'
            }), 400
        
        log_with_context(logger, 'INFO', f'Retrieving memory for user {user_id}', 
                         user_id=user_id)
        
        # Get STM
        stm_sessions = stm.get_sessions(user_id)
        
        # Get LTM
        ltm_data = ltm.get_memory(user_id)
        
        memory_response = {
            'user_id': user_id,
            'stm': {
                'sessions': stm_sessions or [],
                'count': len(stm_sessions) if stm_sessions else 0
            },
            'ltm': {
                'trends': ltm_data.get('trends', {}) if ltm_data else {},
                'patterns': ltm_data.get('patterns', []) if ltm_data else [],
                'preferences': ltm_data.get('preferences', {}) if ltm_data else {},
                'available': bool(ltm_data)
            }
        }
        
        return jsonify(memory_response), 200
        
    except Exception as e:
        logger.error(f'Memory endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': {'message': str(e)}
        }), 500

