"""
Frontend API endpoints for sleep.html interface.
These endpoints provide a simplified API for the frontend to interact with the worker agent.
"""
from flask import Blueprint, request, jsonify
from agent.workflow import process_task
from memory.stm import ShortTermMemory
from memory.ltm import LongTermMemory
from utils.logger import logger, log_with_context

frontend_bp = Blueprint('frontend', __name__)
stm = ShortTermMemory()
ltm = LongTermMemory()

@frontend_bp.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze sleep data and return recommendations.
    This endpoint is used by the frontend (sleep.html).
    
    Request Body:
        {
            "user_id": "U_101",
            "profile": {...},
            "sleep_sessions": [...]
        }
    
    Returns:
        Analysis results with recommendations
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'code': 'INVALID_REQUEST'
            }), 400
        
        user_id = data.get('user_id', '')
        profile = data.get('profile', {})
        sleep_sessions = data.get('sleep_sessions', [])
        
        # Validate user_id - reject default_user and empty
        if not user_id or user_id == 'default_user' or user_id.strip() == '':
            log_with_context(logger, 'WARNING', f'Invalid user_id attempted in analyze: {user_id}', 
                           user_id=user_id)
            return jsonify({
                'error': 'Invalid user_id. Please login through supervisor agent.',
                'code': 'INVALID_USER_ID'
            }), 400
        
        if not sleep_sessions:
            return jsonify({
                'error': 'No sleep sessions provided',
                'code': 'MISSING_DATA'
            }), 400
        
        log_with_context(logger, 'INFO', f'Frontend analysis request for user {user_id}', 
                         user_id=user_id)
        
        # Create task payload
        import uuid
        task_id = f"frontend_task_{uuid.uuid4().hex[:8]}"
        
        task_data = {
            'task_id': task_id,
            'user_id': user_id,
            'payload': {
                'sleep_sessions': sleep_sessions,
                'profile': profile
            }
        }
        
        # Process through workflow
        result = process_task(task_data)
        
        if result.get('status') == 'error':
            return jsonify({
                'error': result.get('error', 'Analysis failed'),
                'code': 'ANALYSIS_ERROR'
            }), 500
        
        # Return the result
        analysis_result = result.get('result', {})
        
        return jsonify(analysis_result), 200
        
    except Exception as e:
        logger.error(f'Frontend analyze endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': {'message': str(e)}
        }), 500

@frontend_bp.route('/api/sessions', methods=['POST'])
def save_sessions():
    """
    Save sleep sessions to memory.
    This endpoint is used by the frontend to persist sessions.
    
    Request Body:
        {
            "user_id": "U_101",
            "sleep_sessions": [...]
        }
    
    Returns:
        Success confirmation
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'code': 'INVALID_REQUEST'
            }), 400
        
        user_id = data.get('user_id', '')
        sleep_sessions = data.get('sleep_sessions', [])
        
        # Validate user_id - reject default_user and empty
        if not user_id or user_id == 'default_user' or user_id.strip() == '':
            log_with_context(logger, 'WARNING', f'Invalid user_id attempted in save_sessions: {user_id}', 
                           user_id=user_id)
            return jsonify({
                'error': 'Invalid user_id. Please login through supervisor agent.',
                'code': 'INVALID_USER_ID'
            }), 400
        
        if not sleep_sessions:
            return jsonify({
                'error': 'No sleep sessions provided',
                'code': 'MISSING_DATA'
            }), 400
            log_with_context(logger, 'WARNING', f'Invalid user_id attempted: {user_id}', 
                           user_id=user_id)
            return jsonify({
                'error': 'Invalid user_id. Please login through supervisor agent.',
                'code': 'INVALID_USER_ID'
            }), 400
        
        log_with_context(logger, 'INFO', f'Saving {len(sleep_sessions)} sessions for user {user_id}', 
                         user_id=user_id)
        
        # Save sessions to STM using save_sessions method
        success = stm.save_sessions(user_id, sleep_sessions)
        
        if not success:
            return jsonify({
                'error': 'Failed to save sessions',
                'code': 'SAVE_ERROR'
            }), 500
        
        return jsonify({
            'success': True,
            'message': f'Saved {len(sleep_sessions)} session(s)',
            'user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f'Frontend sessions endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': {'message': str(e)}
        }), 500

@frontend_bp.route('/api/recommendations/<user_id>', methods=['GET'])
def get_recommendations(user_id):
    """
    Get recommendations for a user from memory.
    This endpoint retrieves stored recommendations from LTM.
    
    Returns:
        Recommendations data
    """
    try:
        # Validate user_id - reject default_user
        if not user_id or user_id == 'default_user' or user_id.strip() == '':
            log_with_context(logger, 'WARNING', f'Invalid user_id attempted in recommendations: {user_id}', 
                           user_id=user_id)
            return jsonify({
                'error': 'Invalid user_id. Please login through supervisor agent.',
                'code': 'INVALID_USER_ID'
            }), 400
        
        log_with_context(logger, 'INFO', f'Fetching recommendations for user {user_id}', 
                         user_id=user_id)
        
        # Get LTM data
        ltm_data = ltm.get_memory(user_id)
        
        if not ltm_data:
            return jsonify({
                'sleep_score': None,
                'confidence': None,
                'issues': [],
                'recommendations': {},
                'personalized_tips': []
            }), 200
        
        # Extract recommendations from LTM
        trends = ltm_data.get('trends', {})
        patterns = ltm_data.get('patterns', [])
        recommendations = ltm_data.get('recommendations', {})
        personalized_tips = ltm_data.get('personalized_tips', [])
        
        # Get sleep_score and confidence from LTM (can be at top level or in trends)
        sleep_score = ltm_data.get('sleep_score')
        if sleep_score is None:
            sleep_score = trends.get('avg_sleep_score')
        
        confidence = ltm_data.get('confidence')
        if confidence is None:
            confidence = trends.get('confidence')
        
        # Format issues from patterns (filter out non-issue patterns)
        issues = []
        for pattern in patterns:
            if isinstance(pattern, dict):
                pattern_type = pattern.get('type', '')
                # Only include actual issues, not informational patterns
                if pattern_type == 'issue' or 'problem' in pattern_type.lower() or 'warning' in pattern_type.lower():
                    issues.append(pattern.get('description', ''))
            elif isinstance(pattern, str):
                if 'issue' in pattern.lower() or 'problem' in pattern.lower():
                    issues.append(pattern)
        
        return jsonify({
            'sleep_score': sleep_score,
            'confidence': confidence,
            'issues': issues,
            'recommendations': recommendations,
            'personalized_tips': personalized_tips
        }), 200
        
    except Exception as e:
        logger.error(f'Frontend recommendations endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': {'message': str(e)}
        }), 500

