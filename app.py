"""
Main Flask application for Sleep Optimizer Worker Agent.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.task import task_bp
from routes.register import register_bp
from routes.health import health_bp
from routes.memory import memory_bp
from routes.logs import logs_bp
from routes.frontend import frontend_bp
from routes.profile import profile_bp
from utils.logger import logger, setup_logger

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure CORS
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(task_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(memory_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(frontend_bp)
    app.register_blueprint(profile_bp)
    
    # Root endpoint - serve sleep.html interface
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint - serve sleep.html interface."""
        from flask import send_from_directory, send_file
        import os
        # Get the directory where sleep.html is located (current directory)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sleep_html_path = os.path.join(current_dir, 'sleep.html')
        if os.path.exists(sleep_html_path):
            return send_file(sleep_html_path)
        else:
            # Fallback to API info if sleep.html not found
            return jsonify({
                'agent': Config.AGENT_NAME,
                'agent_id': Config.AGENT_ID,
                'version': Config.AGENT_VERSION,
                'status': 'running',
                'message': 'sleep.html not found. Please ensure sleep.html is in the project root directory.',
                'endpoints': {
                    'register': '/register',
                    'task': '/task',
                    'health': '/health',
                    'memory': '/memory?user_id=<user_id>',
                    'logs': '/logs',
                    'frontend_analyze': '/api/analyze',
                    'frontend_sessions': '/api/sessions',
                    'frontend_recommendations': '/api/recommendations/<user_id>'
                }
            }), 200
    
    # API info endpoint
    @app.route('/api', methods=['GET'])
    def api_info():
        """API information endpoint."""
        return jsonify({
            'agent': Config.AGENT_NAME,
            'agent_id': Config.AGENT_ID,
            'version': Config.AGENT_VERSION,
            'status': 'running',
            'endpoints': {
                'register': '/register',
                'task': '/task',
                'health': '/health',
                'memory': '/memory?user_id=<user_id>',
                'logs': '/logs',
                'frontend_analyze': '/api/analyze',
                'frontend_sessions': '/api/sessions',
                'frontend_recommendations': '/api/recommendations/<user_id>'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'code': 'NOT_FOUND',
            'details': {}
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method not allowed',
            'code': 'METHOD_NOT_ALLOWED',
            'details': {}
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal server error: {str(error)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': {}
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f'Unhandled exception: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': {'message': str(e)}
        }), 500
    
    logger.info(f'{Config.AGENT_NAME} initialized')
    logger.info(f'Agent ID: {Config.AGENT_ID}')
    logger.info(f'Version: {Config.AGENT_VERSION}')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )

