"""
Profile management routes for Worker Agent.
Handles domain-specific profile data (sleep habits, preferences).
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from memory.ltm import LongTermMemory
from utils.logger import logger, log_with_context

profile_bp = Blueprint('profile', __name__)
ltm = LongTermMemory()

@profile_bp.route('/api/profile', methods=['GET'])
def get_profile():
    """
    Get user's domain-specific profile from Worker's LTM.
    
    Query Parameters:
        user_id: User ID
    
    Returns:
        Profile data specific to sleep optimization
    """
    try:
        user_id = request.args.get('user_id', '')
        
        # Validate user_id
        if not user_id or user_id == 'default_user' or user_id.strip() == '':
            log_with_context(logger, 'WARNING', f'Invalid user_id attempted in get_profile: {user_id}', 
                           user_id=user_id)
            return jsonify({
                'error': 'Invalid user_id. Please login through supervisor agent.',
                'code': 'INVALID_USER_ID'
            }), 400
        
        log_with_context(logger, 'INFO', f'Fetching profile for user {user_id}', 
                         user_id=user_id)
        
        # Get LTM data
        ltm_data = ltm.get_memory(user_id)
        
        # Extract profile from preferences
        profile = {}
        if ltm_data:
            preferences = ltm_data.get('preferences', {})
            profile = preferences.get('profile', {})
        
        return jsonify({
            'user_id': user_id,
            'profile': profile
        }), 200
        
    except Exception as e:
        logger.error(f'Get profile endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': {'message': str(e)}
        }), 500

@profile_bp.route('/api/profile', methods=['PUT', 'POST'])
def save_profile():
    """
    Save user's domain-specific profile to Worker's LTM.
    
    Request Body:
        {
            "user_id": "U_101",
            "profile": {
                "age": 25,
                "work_schedule": "9am-5pm",
                "caffeine_intake": "medium",
                "screen_time": 2,
                "exercise": "3-4-times",
                "stress_level": 3
            }
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
        profile = data.get('profile', {})
        
        # Validate user_id
        if not user_id or user_id == 'default_user' or user_id.strip() == '':
            log_with_context(logger, 'WARNING', f'Invalid user_id attempted in save_profile: {user_id}', 
                           user_id=user_id)
            return jsonify({
                'error': 'Invalid user_id. Please login through supervisor agent.',
                'code': 'INVALID_USER_ID'
            }), 400
        
        if not profile:
            return jsonify({
                'error': 'No profile data provided',
                'code': 'MISSING_DATA'
            }), 400
        
        log_with_context(logger, 'INFO', f'Saving profile for user {user_id}', 
                         user_id=user_id)
        
        # Get existing LTM data
        ltm_data = ltm.get_memory(user_id) or {}
        
        # Update preferences with profile
        preferences = ltm_data.get('preferences', {})
        preferences['profile'] = profile
        ltm_data['preferences'] = preferences
        ltm_data['last_updated'] = datetime.utcnow().isoformat()
        
        # Save to LTM using storage
        success = ltm.storage.save_memory(user_id, 'ltm', ltm_data)
        
        if not success:
            return jsonify({
                'error': 'Failed to save profile',
                'code': 'SAVE_ERROR'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Profile saved successfully',
            'user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f'Save profile endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': {'message': str(e)}
        }), 500
