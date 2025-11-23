"""
Task processing endpoint - Main entry point for Supervisor Agent.
"""
from flask import Blueprint, jsonify, request
from agent.workflow import process_task
from utils.validators import validate_task_request
from utils.logger import logger, log_with_context
from config import Config

task_bp = Blueprint('task', __name__)

@task_bp.route('/task', methods=['POST'])
def handle_task():
    """
    Process a sleep analysis task from the Supervisor Agent.
    
    Request Body:
        {
            "task_id": "task_123",
            "user_id": "U_101",
            "payload": {
                "sleep_sessions": [...],
                "profile": {...}
            }
        }
    
    Returns:
        JSON response with task results
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'code': 'INVALID_REQUEST',
                'details': 'Request body must be valid JSON'
            }), 400
        
        # Validate request
        is_valid, error_msg = validate_task_request(data)
        if not is_valid:
            return jsonify({
                'error': error_msg,
                'code': 'VALIDATION_ERROR',
                'details': {}
            }), 400
        
        task_id = data.get('task_id')
        user_id = data.get('user_id')
        
        log_with_context(logger, 'INFO', f'Processing task {task_id}', 
                         user_id=user_id, task_id=task_id)
        
        # Process task through workflow
        result = process_task(data)
        
        if result.get('status') == 'error':
            log_with_context(logger, 'ERROR', f'Task {task_id} failed: {result.get("error")}', 
                             user_id=user_id, task_id=task_id)
            return jsonify({
                'task_id': task_id,
                'status': 'error',
                'error': result.get('error', 'Unknown error')
            }), 500
        
        log_with_context(logger, 'INFO', f'Task {task_id} completed successfully', 
                         user_id=user_id, task_id=task_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'Task endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': {'message': str(e)}
        }), 500

