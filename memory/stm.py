"""
Short-Term Memory (STM) - Stores recent sleep sessions.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from memory.storage import storage
from config import Config
from utils.logger import logger

class ShortTermMemory:
    """Manages short-term memory for recent sleep sessions."""
    
    def __init__(self):
        self.storage = storage
        self.retention_days = Config.STM_RETENTION_DAYS
    
    def save_sessions(self, user_id: str, sessions: List[Dict[str, Any]]) -> bool:
        """
        Save recent sleep sessions to STM.
        
        Args:
            user_id: User identifier
            sessions: List of sleep session dictionaries
        
        Returns:
            True if successful
        """
        try:
            # Get existing STM
            existing = self.get_sessions(user_id) or []
            
            # Merge and deduplicate sessions
            session_map = {}
            for session in existing:
                session_id = session.get('session_id') or self._generate_session_id(session)
                session_map[session_id] = session
            
            for session in sessions:
                session_id = session.get('session_id') or self._generate_session_id(session)
                session_map[session_id] = session
            
            # Filter by retention period
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            filtered_sessions = []
            
            for session in session_map.values():
                session_date = self._parse_session_date(session)
                if session_date and session_date >= cutoff_date:
                    filtered_sessions.append(session)
            
            # Sort by date (newest first)
            filtered_sessions.sort(
                key=lambda s: self._parse_session_date(s) or datetime.min,
                reverse=True
            )
            
            stm_data = {
                'sessions': filtered_sessions,
                'last_updated': datetime.utcnow().isoformat(),
                'count': len(filtered_sessions)
            }
            
            return self.storage.save_memory(user_id, 'stm', stm_data)
        except Exception as e:
            logger.error(f"Error saving STM sessions: {str(e)}", extra={'user_id': user_id})
            return False
    
    def get_sessions(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve recent sleep sessions from STM.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of sleep session dictionaries or None
        """
        try:
            stm_data = self.storage.get_memory(user_id, 'stm')
            if stm_data:
                return stm_data.get('sessions', [])
            return []
        except Exception as e:
            logger.error(f"Error retrieving STM sessions: {str(e)}", extra={'user_id': user_id})
            return []
    
    def get_recent_sessions(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get sessions from the last N days.
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve
        
        Returns:
            List of recent sleep sessions
        """
        sessions = self.get_sessions(user_id) or []
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recent = []
        for session in sessions:
            session_date = self._parse_session_date(session)
            if session_date and session_date >= cutoff_date:
                recent.append(session)
        
        return recent
    
    def clear_old_sessions(self, user_id: str) -> bool:
        """Remove sessions older than retention period."""
        return self.save_sessions(user_id, [])  # Will filter automatically
    
    def _generate_session_id(self, session: Dict[str, Any]) -> str:
        """Generate a unique session ID from session data."""
        bedtime = session.get('bedtime', '')
        waketime = session.get('waketime', '')
        session_date = session.get('session_date', '')
        return f"{session_date}_{bedtime}_{waketime}"
    
    def _parse_session_date(self, session: Dict[str, Any]) -> Optional[datetime]:
        """Parse session date from various formats."""
        session_date = session.get('session_date')
        if not session_date:
            return None
        
        if isinstance(session_date, datetime):
            return session_date
        
        if isinstance(session_date, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(session_date.replace('Z', '+00:00'))
            except:
                try:
                    # Try date format
                    return datetime.strptime(session_date, '%Y-%m-%d')
                except:
                    return None
        
        return None
