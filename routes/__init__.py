"""
Routes package initialization.
"""
from .task import task_bp
from .register import register_bp
from .health import health_bp
from .memory import memory_bp
from .logs import logs_bp
from .frontend import frontend_bp
from .profile import profile_bp

__all__ = ['task_bp', 'register_bp', 'health_bp', 'memory_bp', 'logs_bp', 'frontend_bp', 'profile_bp']
