"""
Input validation utilities for the Sleep Optimizer Agent.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import Config

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_task_request(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate a task request from the Supervisor Agent.
    
    Args:
        data: Request data dictionary
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Request must be a JSON object"
    
    # Check required fields
    required_fields = ['task_id', 'user_id', 'payload']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate task_id
    if not isinstance(data['task_id'], str) or not data['task_id'].strip():
        return False, "task_id must be a non-empty string"
    
    # Validate user_id
    if not isinstance(data['user_id'], str) or not data['user_id'].strip():
        return False, "user_id must be a non-empty string"
    
    # Validate payload
    if not isinstance(data['payload'], dict):
        return False, "payload must be a JSON object"
    
    # Validate sleep_sessions if present
    if 'sleep_sessions' in data['payload']:
        sessions = data['payload']['sleep_sessions']
        if not isinstance(sessions, list):
            return False, "sleep_sessions must be an array"
        
        if len(sessions) > Config.MAX_SLEEP_SESSIONS_PER_TASK:
            return False, f"Too many sleep sessions (max: {Config.MAX_SLEEP_SESSIONS_PER_TASK})"
        
        # Validate each session structure
        for i, session in enumerate(sessions):
            if not isinstance(session, dict):
                return False, f"sleep_sessions[{i}] must be an object"
            
            # Check for required session fields
            session_required = ['bedtime', 'waketime', 'duration_hours']
            for field in session_required:
                if field not in session:
                    return False, f"sleep_sessions[{i}] missing required field: {field}"
            
            # Validate duration
            try:
                duration = float(session['duration_hours'])
                if duration < Config.MIN_SLEEP_DURATION or duration > Config.MAX_SLEEP_DURATION:
                    return False, f"sleep_sessions[{i}] has invalid duration: {duration}"
            except (ValueError, TypeError):
                return False, f"sleep_sessions[{i}] duration_hours must be a number"
    
    return True, None

def validate_sleep_session(session: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate a single sleep session.
    
    Args:
        session: Sleep session dictionary
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['bedtime', 'waketime', 'duration_hours']
    for field in required_fields:
        if field not in session:
            return False, f"Missing required field: {field}"
    
    # Validate duration
    try:
        duration = float(session['duration_hours'])
        if duration < Config.MIN_SLEEP_DURATION or duration > Config.MAX_SLEEP_DURATION:
            return False, f"Invalid sleep duration: {duration} hours"
    except (ValueError, TypeError):
        return False, "duration_hours must be a number"
    
    # Validate optional fields
    if 'efficiency_score' in session:
        try:
            score = float(session['efficiency_score'])
            if score < 0 or score > 100:
                return False, "efficiency_score must be between 0 and 100"
        except (ValueError, TypeError):
            return False, "efficiency_score must be a number"
    
    if 'morning_mood' in session:
        try:
            mood = int(session['morning_mood'])
            if mood < 1 or mood > 10:
                return False, "morning_mood must be between 1 and 10"
        except (ValueError, TypeError):
            return False, "morning_mood must be an integer"
    
    return True, None

def validate_user_profile(profile: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate user profile data.
    
    Args:
        profile: User profile dictionary
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(profile, dict):
        return False, "profile must be a JSON object"
    
    # Validate age if present
    if 'age' in profile:
        try:
            age = int(profile['age'])
            if age < 1 or age > 120:
                return False, "age must be between 1 and 120"
        except (ValueError, TypeError):
            return False, "age must be an integer"
    
    # Validate stress_level if present
    if 'stress_level' in profile:
        try:
            stress = int(profile['stress_level'])
            if stress < 1 or stress > 5:
                return False, "stress_level must be between 1 and 5"
        except (ValueError, TypeError):
            return False, "stress_level must be an integer"
    
    return True, None

