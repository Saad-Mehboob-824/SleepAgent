"""
Long-Term Memory (LTM) - Stores trends, patterns, and user preferences.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from .storage import storage
from config import Config
from utils.logger import logger

class LongTermMemory:
    """Manages long-term memory for sleep trends and patterns."""
    
    def __init__(self):
        self.storage = storage
        self.retention_days = Config.LTM_RETENTION_DAYS
    
    def update_trends(self, user_id: str, sessions: List[Dict[str, Any]]) -> bool:
        """
        Update long-term trends from sleep sessions.
        Preserves existing recommendations, sleep_score, and confidence.
        
        Args:
            user_id: User identifier
            sessions: List of sleep session dictionaries
        
        Returns:
            True if successful
        """
        try:
            existing_ltm = self.get_memory(user_id) or {}
            
            # Calculate trends
            trends = self._calculate_trends(sessions)
            
            # Update existing trends (preserve sleep_score and confidence if they exist in trends)
            existing_trends = existing_ltm.get('trends', {}).copy()
            existing_trends.update(trends)
            
            # Calculate patterns
            patterns = self._identify_patterns(sessions)
            
            # Update preferences
            preferences = self._extract_preferences(sessions, existing_ltm.get('preferences', {}))
            
            # Build LTM data, preserving all existing data
            ltm_data = existing_ltm.copy()  # Start with all existing data
            
            # Update with new calculated values
            ltm_data.update({
                'trends': existing_trends,
                'patterns': patterns,
                'preferences': preferences,
                'last_updated': datetime.utcnow().isoformat(),
                'total_sessions_analyzed': existing_ltm.get('total_sessions_analyzed', 0) + len(sessions)
            })
            
            return self.storage.save_memory(user_id, 'ltm', ltm_data)
        except Exception as e:
            logger.error(f"Error updating LTM trends: {str(e)}", extra={'user_id': user_id})
            return False
    
    def update_recommendations(self, user_id: str, recommendations: Dict[str, Any], 
                               sleep_score: int, confidence: float, 
                               personalized_tips: List[str], issues: List[str] = None) -> bool:
        """
        Update recommendations, sleep score, confidence, and issues in LTM.
        
        Args:
            user_id: User identifier
            recommendations: Recommendations dictionary
            sleep_score: Sleep score (0-100)
            confidence: Confidence level (0.0-1.0)
            personalized_tips: List of personalized tips
            issues: Optional list of issues
        
        Returns:
            True if successful
        """
        try:
            existing_ltm = self.get_memory(user_id) or {}
            
            # Update LTM with recommendations data (preserve all existing data)
            ltm_data = existing_ltm.copy()
            ltm_data['recommendations'] = recommendations
            ltm_data['sleep_score'] = sleep_score
            ltm_data['confidence'] = confidence
            ltm_data['personalized_tips'] = personalized_tips
            if issues is not None:
                ltm_data['issues'] = issues
            ltm_data['last_updated'] = datetime.utcnow().isoformat()
            
            # Also update trends with sleep_score and confidence
            if 'trends' not in ltm_data:
                ltm_data['trends'] = {}
            ltm_data['trends']['avg_sleep_score'] = sleep_score
            ltm_data['trends']['confidence'] = confidence
            
            logger.info(f"Updating LTM recommendations for user {user_id}: "
                       f"score={sleep_score}, confidence={confidence}, "
                       f"rec_keys={list(recommendations.keys()) if recommendations else 'none'}, "
                       f"tips={len(personalized_tips)}, issues={len(issues) if issues else 0}")
            
            return self.storage.save_memory(user_id, 'ltm', ltm_data)
        except Exception as e:
            logger.error(f"Error updating LTM recommendations: {str(e)}", extra={'user_id': user_id})
            return False
    
    def get_memory(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve long-term memory for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            LTM data dictionary or None
        """
        try:
            return self.storage.get_memory(user_id, 'ltm')
        except Exception as e:
            logger.error(f"Error retrieving LTM: {str(e)}", extra={'user_id': user_id})
            return None
    
    def get_trends(self, user_id: str) -> Dict[str, Any]:
        """Get sleep trends for a user."""
        ltm = self.get_memory(user_id) or {}
        return ltm.get('trends', {})
    
    def get_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """Get identified sleep patterns for a user."""
        ltm = self.get_memory(user_id) or {}
        return ltm.get('patterns', [])
    
    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user sleep preferences."""
        ltm = self.get_memory(user_id) or {}
        return ltm.get('preferences', {})
    
    def _calculate_trends(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate sleep trends from sessions."""
        if not sessions:
            return {}
        
        durations = [s.get('duration_hours', 0) for s in sessions if s.get('duration_hours')]
        efficiency_scores = [s.get('efficiency_score', 0) for s in sessions if s.get('efficiency_score')]
        morning_moods = [s.get('morning_mood', 5) for s in sessions if s.get('morning_mood')]
        
        trends = {}
        
        if durations:
            trends['avg_duration'] = sum(durations) / len(durations)
            trends['min_duration'] = min(durations)
            trends['max_duration'] = max(durations)
            trends['duration_consistency'] = 1.0 - (max(durations) - min(durations)) / max(durations) if max(durations) > 0 else 0.0
        
        if efficiency_scores:
            trends['avg_efficiency'] = sum(efficiency_scores) / len(efficiency_scores)
            trends['min_efficiency'] = min(efficiency_scores)
            trends['max_efficiency'] = max(efficiency_scores)
        
        if morning_moods:
            trends['avg_morning_mood'] = sum(morning_moods) / len(morning_moods)
        
        # Calculate weekly averages
        if len(sessions) >= 7:
            recent_7 = sessions[:7]
            durations_7 = [s.get('duration_hours', 0) for s in recent_7 if s.get('duration_hours')]
            if durations_7:
                trends['weekly_avg_duration'] = sum(durations_7) / len(durations_7)
        
        return trends
    
    def _identify_patterns(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify sleep patterns from sessions."""
        patterns = []
        
        if len(sessions) < 3:
            return patterns
        
        # Pattern: Consistent bedtime
        bedtimes = [s.get('bedtime') for s in sessions if s.get('bedtime')]
        if bedtimes and len(set(bedtimes)) <= 2:
            patterns.append({
                'type': 'consistent_bedtime',
                'description': 'Maintains consistent bedtime',
                'confidence': 0.8
            })
        
        # Pattern: Weekend vs weekday difference
        # This would require day-of-week data, simplified here
        if len(sessions) >= 7:
            patterns.append({
                'type': 'sufficient_data',
                'description': 'Has sufficient data for pattern analysis',
                'confidence': 0.7
            })
        
        return patterns
    
    def _extract_preferences(self, sessions: List[Dict[str, Any]], existing: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user preferences from sessions."""
        preferences = existing.copy()
        
        # Extract preferred sleep duration
        durations = [s.get('duration_hours', 0) for s in sessions if s.get('duration_hours')]
        if durations:
            avg_duration = sum(durations) / len(durations)
            preferences['preferred_duration'] = round(avg_duration, 1)
        
        # Extract preferred bedtime range
        bedtimes = [s.get('bedtime') for s in sessions if s.get('bedtime')]
        if bedtimes:
            # Find most common bedtime
            from collections import Counter
            bedtime_counts = Counter(bedtimes)
            if bedtime_counts:
                preferences['preferred_bedtime'] = bedtime_counts.most_common(1)[0][0]
        
        return preferences

