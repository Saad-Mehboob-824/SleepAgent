"""
Sleep score calculation service.
Calculates overall sleep quality score and confidence level.
"""
from typing import Dict, Any, List
from config import Config
from utils.logger import logger

class SleepScorer:
    """Calculates sleep quality scores and confidence levels."""
    
    def calculate_score(self, sessions: List[Dict[str, Any]], analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate overall sleep score and confidence.
        
        Args:
            sessions: List of sleep session dictionaries
            analysis: Optional pre-computed analysis results
        
        Returns:
            Dictionary with sleep_score (0-100) and confidence (0.0-1.0)
        """
        if not sessions:
            return {
                'sleep_score': 0,
                'confidence': 0.0,
                'breakdown': {}
            }
        
        # Calculate component scores
        duration_score = self._score_duration(sessions, analysis)
        consistency_score = self._score_consistency(sessions, analysis)
        efficiency_score = self._score_efficiency(sessions, analysis)
        interruption_score = self._score_interruptions(sessions, analysis)
        
        # Weighted average
        weights = {
            'duration': 0.3,
            'consistency': 0.25,
            'efficiency': 0.3,
            'interruptions': 0.15
        }
        
        overall_score = (
            duration_score * weights['duration'] +
            consistency_score * weights['consistency'] +
            efficiency_score * weights['efficiency'] +
            interruption_score * weights['interruptions']
        )
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(sessions, analysis)
        
        return {
            'sleep_score': round(overall_score),
            'confidence': round(confidence, 2),
            'breakdown': {
                'duration_score': round(duration_score, 1),
                'consistency_score': round(consistency_score, 1),
                'efficiency_score': round(efficiency_score, 1),
                'interruption_score': round(interruption_score, 1)
            }
        }
    
    def _score_duration(self, sessions: List[Dict[str, Any]], analysis: Dict[str, Any] = None) -> float:
        """Score based on sleep duration."""
        if analysis and 'duration_analysis' in analysis:
            avg_duration = analysis['duration_analysis'].get('average', 0)
        else:
            durations = [s.get('duration_hours', 0) for s in sessions if s.get('duration_hours')]
            if not durations:
                return 0.0
            avg_duration = sum(durations) / len(durations)
        
        # Optimal range: 7-9 hours = 100 points
        if Config.OPTIMAL_SLEEP_DURATION_MIN <= avg_duration <= Config.OPTIMAL_SLEEP_DURATION_MAX:
            return 100.0
        elif avg_duration < Config.OPTIMAL_SLEEP_DURATION_MIN:
            # Linear decrease from 100 to 0
            ratio = avg_duration / Config.OPTIMAL_SLEEP_DURATION_MIN
            return max(0.0, ratio * 100.0)
        else:  # avg_duration > OPTIMAL_SLEEP_DURATION_MAX
            # Linear decrease from 100 to 0
            excess = avg_duration - Config.OPTIMAL_SLEEP_DURATION_MAX
            max_excess = Config.MAX_SLEEP_DURATION - Config.OPTIMAL_SLEEP_DURATION_MAX
            ratio = 1.0 - (excess / max_excess) if max_excess > 0 else 0.0
            return max(0.0, ratio * 100.0)
    
    def _score_consistency(self, sessions: List[Dict[str, Any]], analysis: Dict[str, Any] = None) -> float:
        """Score based on schedule consistency."""
        if analysis and 'consistency_analysis' in analysis:
            consistency = analysis['consistency_analysis'].get('overall_consistency', 0.0)
        else:
            # Calculate consistency
            bedtimes = [s.get('bedtime') for s in sessions if s.get('bedtime')]
            waketimes = [s.get('waketime') for s in sessions if s.get('waketime')]
            
            if not bedtimes or not waketimes:
                return 50.0
            
            unique_bedtimes = len(set(bedtimes))
            unique_waketimes = len(set(waketimes))
            
            bedtime_consistency = 1.0 - (unique_bedtimes - 1) / len(bedtimes) if len(bedtimes) > 1 else 1.0
            waketime_consistency = 1.0 - (unique_waketimes - 1) / len(waketimes) if len(waketimes) > 1 else 1.0
            consistency = (bedtime_consistency + waketime_consistency) / 2
        
        return consistency * 100.0
    
    def _score_efficiency(self, sessions: List[Dict[str, Any]], analysis: Dict[str, Any] = None) -> float:
        """Score based on sleep efficiency."""
        if analysis and 'efficiency_analysis' in analysis:
            avg_efficiency = analysis['efficiency_analysis'].get('average', 0)
        else:
            efficiency_scores = [s.get('efficiency_score', 0) for s in sessions if s.get('efficiency_score')]
            if not efficiency_scores:
                return 50.0  # Default if no efficiency data
            avg_efficiency = sum(efficiency_scores) / len(efficiency_scores)
        
        return avg_efficiency
    
    def _score_interruptions(self, sessions: List[Dict[str, Any]], analysis: Dict[str, Any] = None) -> float:
        """Score based on interruption frequency."""
        if analysis and 'interruption_analysis' in analysis:
            interruption_rate = analysis['interruption_analysis'].get('interruption_rate', 0.0)
            avg_interruptions = analysis['interruption_analysis'].get('average_per_session', 0.0)
        else:
            total_interruptions = 0
            for session in sessions:
                interruptions = session.get('interruptions', [])
                if isinstance(interruptions, list):
                    total_interruptions += len(interruptions)
            
            avg_interruptions = total_interruptions / len(sessions) if sessions else 0
            interruption_rate = sum(1 for s in sessions if len(s.get('interruptions', [])) > 0) / len(sessions) if sessions else 0
        
        # Score decreases with interruptions
        # 0 interruptions = 100, 3+ interruptions = 0
        if avg_interruptions == 0:
            return 100.0
        elif avg_interruptions <= 1:
            return 80.0
        elif avg_interruptions <= 2:
            return 60.0
        elif avg_interruptions <= 3:
            return 40.0
        else:
            return max(0.0, 100.0 - (avg_interruptions * 20.0))
    
    def _calculate_confidence(self, sessions: List[Dict[str, Any]], analysis: Dict[str, Any] = None) -> float:
        """
        Calculate confidence level based on data quality and quantity.
        
        Returns:
            Confidence value between 0.0 and 1.0
        """
        if not sessions:
            return 0.0
        
        # Base confidence on number of sessions
        session_count_confidence = min(1.0, len(sessions) / 7.0)  # 7+ sessions = full confidence
        
        # Check data completeness
        complete_sessions = 0
        for session in sessions:
            has_duration = bool(session.get('duration_hours'))
            has_bedtime = bool(session.get('bedtime'))
            has_waketime = bool(session.get('waketime'))
            
            if has_duration and has_bedtime and has_waketime:
                complete_sessions += 1
        
        completeness_confidence = complete_sessions / len(sessions) if sessions else 0.0
        
        # Check for efficiency scores (optional but improves confidence)
        has_efficiency = sum(1 for s in sessions if s.get('efficiency_score')) / len(sessions) if sessions else 0.0
        
        # Weighted confidence
        confidence = (
            session_count_confidence * 0.4 +
            completeness_confidence * 0.4 +
            has_efficiency * 0.2
        )
        
        return min(1.0, max(0.0, confidence))

