"""
Logs retrieval endpoint - Returns recent agent logs.
"""
import os
from flask import Blueprint, jsonify, request
from config import Config
from utils.logger import logger

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs', methods=['GET'])
def get_logs():
    """
    Retrieve recent agent logs.
    
    Query Parameters:
        limit (optional): Number of log entries to return (default: 100, max: 1000)
        level (optional): Filter by log level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        JSON response with log entries
    """
    try:
        limit = int(request.args.get('limit', 100))
        limit = min(limit, 1000)  # Cap at 1000
        level_filter = request.args.get('level', '').upper()
        
        logs = []
        
        # Read from log file if it exists
        log_file = Config.LOG_FILE
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    # Read last N lines
                    lines = f.readlines()
                    recent_lines = lines[-limit:] if len(lines) > limit else lines
                    
                    for line in recent_lines:
                        try:
                            import json
                            log_entry = json.loads(line.strip())
                            
                            # Apply level filter
                            if level_filter and log_entry.get('level') != level_filter:
                                continue
                            
                            logs.append(log_entry)
                        except:
                            # If not JSON, add as plain text
                            logs.append({
                                'message': line.strip(),
                                'level': 'INFO',
                                'timestamp': ''
                            })
            except Exception as e:
                logger.warning(f'Error reading log file: {str(e)}')
        
        # If no logs from file, return empty
        if not logs:
            logs = [{
                'message': 'No logs available',
                'level': 'INFO',
                'timestamp': ''
            }]
        
        return jsonify({
            'logs': logs[-limit:],  # Ensure we don't exceed limit
            'count': len(logs),
            'limit': limit,
            'level_filter': level_filter if level_filter else None
        }), 200
        
    except Exception as e:
        logger.error(f'Logs endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': {'message': str(e)}
        }), 500

