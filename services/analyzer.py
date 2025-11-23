"""
Sleep data analysis service.
Analyzes sleep patterns, consistency, efficiency, and issues.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import Counter
from config import Config
from utils.logger import logger

class SleepAnalyzer:
    """Analyzes sleep data to identify patterns and issues."""
    
    def analyze(self, sessions: List[Dict[str, Any]], profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive sleep analysis.
        
        Args:
            sessions: List of sleep session dictionaries
            profile: Optional user profile data
        
        Returns:
            Analysis results dictionary
        """
        if not sessions:
            return {
                'duration_analysis': {},
                'consistency_analysis': {},
                'efficiency_analysis': {},
                'interruption_analysis': {},
                'issues': ['No sleep data available'],
                'summary': 'No sleep sessions found for analysis'
            }
        
        analysis = {
            'duration_analysis': self._analyze_duration(sessions),
            'consistency_analysis': self._analyze_consistency(sessions),
            'efficiency_analysis': self._analyze_efficiency(sessions),
            'interruption_analysis': self._analyze_interruptions(sessions),
            'caffeine_analysis': self._analyze_caffeine_timing(sessions, profile),
            'screen_time_analysis': self._analyze_screen_time(sessions, profile),
            'exercise_analysis': self._analyze_exercise_timing(sessions, profile),
            'issues': [],
            'summary': ''
        }
        
        # Compile issues
        analysis['issues'] = self._identify_issues(analysis, profile)
        analysis['summary'] = self._generate_summary(analysis)
        
        return analysis
    
    def _analyze_duration(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sleep duration patterns."""
        durations = [s.get('duration_hours', 0) for s in sessions if s.get('duration_hours')]
        
        if not durations:
            return {}
        
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        # Count optimal vs suboptimal
        optimal_count = sum(1 for d in durations if Config.OPTIMAL_SLEEP_DURATION_MIN <= d <= Config.OPTIMAL_SLEEP_DURATION_MAX)
        too_short = sum(1 for d in durations if d < Config.OPTIMAL_SLEEP_DURATION_MIN)
        too_long = sum(1 for d in durations if d > Config.OPTIMAL_SLEEP_DURATION_MAX)
        
        return {
            'average': round(avg_duration, 2),
            'minimum': round(min_duration, 2),
            'maximum': round(max_duration, 2),
            'optimal_count': optimal_count,
            'too_short_count': too_short,
            'too_long_count': too_long,
            'total_sessions': len(durations),
            'is_optimal': Config.OPTIMAL_SLEEP_DURATION_MIN <= avg_duration <= Config.OPTIMAL_SLEEP_DURATION_MAX
        }
    
    def _analyze_consistency(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze bedtime and wake time consistency."""
        bedtimes = [s.get('bedtime') for s in sessions if s.get('bedtime')]
        waketimes = [s.get('waketime') for s in sessions if s.get('waketime')]
        
        bedtime_consistency = 0.0
        waketime_consistency = 0.0
        
        if bedtimes:
            # Count unique bedtimes
            unique_bedtimes = len(set(bedtimes))
            bedtime_consistency = 1.0 - (unique_bedtimes - 1) / len(bedtimes) if len(bedtimes) > 1 else 1.0
            bedtime_consistency = max(0.0, bedtime_consistency)
        
        if waketimes:
            unique_waketimes = len(set(waketimes))
            waketime_consistency = 1.0 - (unique_waketimes - 1) / len(waketimes) if len(waketimes) > 1 else 1.0
            waketime_consistency = max(0.0, waketime_consistency)
        
        return {
            'bedtime_consistency': round(bedtime_consistency, 2),
            'waketime_consistency': round(waketime_consistency, 2),
            'overall_consistency': round((bedtime_consistency + waketime_consistency) / 2, 2) if bedtimes and waketimes else 0.0,
            'unique_bedtimes': len(set(bedtimes)) if bedtimes else 0,
            'unique_waketimes': len(set(waketimes)) if waketimes else 0
        }
    
    def _analyze_efficiency(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sleep efficiency scores."""
        efficiency_scores = [s.get('efficiency_score', 0) for s in sessions if s.get('efficiency_score')]
        
        if not efficiency_scores:
            return {}
        
        avg_efficiency = sum(efficiency_scores) / len(efficiency_scores)
        min_efficiency = min(efficiency_scores)
        max_efficiency = max(efficiency_scores)
        
        # Categorize efficiency
        excellent = sum(1 for e in efficiency_scores if e >= 85)
        good = sum(1 for e in efficiency_scores if 70 <= e < 85)
        fair = sum(1 for e in efficiency_scores if 50 <= e < 70)
        poor = sum(1 for e in efficiency_scores if e < 50)
        
        return {
            'average': round(avg_efficiency, 2),
            'minimum': round(min_efficiency, 2),
            'maximum': round(max_efficiency, 2),
            'excellent_count': excellent,
            'good_count': good,
            'fair_count': fair,
            'poor_count': poor,
            'is_efficient': avg_efficiency >= 70
        }
    
    def _analyze_interruptions(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sleep interruptions."""
        total_interruptions = 0
        sessions_with_interruptions = 0
        
        for session in sessions:
            interruptions = session.get('interruptions', [])
            if isinstance(interruptions, list):
                count = len(interruptions)
                total_interruptions += count
                if count > 0:
                    sessions_with_interruptions += 1
        
        avg_interruptions = total_interruptions / len(sessions) if sessions else 0
        
        return {
            'total_interruptions': total_interruptions,
            'sessions_with_interruptions': sessions_with_interruptions,
            'average_per_session': round(avg_interruptions, 2),
            'interruption_rate': round(sessions_with_interruptions / len(sessions), 2) if sessions else 0.0
        }
    
    def _analyze_caffeine_timing(self, sessions: List[Dict[str, Any]], profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze caffeine intake timing impact."""
        if not profile:
            return {}
        
        caffeine_intake = profile.get('caffeine_intake', 'none')
        caffeine_after_8pm = profile.get('caffeine_after_8pm', False)
        
        # Analyze correlation with sleep quality
        if caffeine_after_8pm or caffeine_intake in ['medium', 'high']:
            efficiency_scores = [s.get('efficiency_score', 0) for s in sessions if s.get('efficiency_score')]
            if efficiency_scores:
                avg_efficiency = sum(efficiency_scores) / len(efficiency_scores)
                return {
                    'caffeine_intake': caffeine_intake,
                    'caffeine_after_8pm': caffeine_after_8pm,
                    'avg_sleep_efficiency': round(avg_efficiency, 2),
                    'potential_impact': avg_efficiency < 75
                }
        
        return {
            'caffeine_intake': caffeine_intake,
            'caffeine_after_8pm': caffeine_after_8pm,
            'potential_impact': False
        }
    
    def _analyze_screen_time(self, sessions: List[Dict[str, Any]], profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze screen time before bed impact."""
        if not profile:
            return {}
        
        screen_time = profile.get('screen_time', 0)
        
        if screen_time > Config.SCREEN_TIME_WARNING_HOURS:
            efficiency_scores = [s.get('efficiency_score', 0) for s in sessions if s.get('efficiency_score')]
            if efficiency_scores:
                avg_efficiency = sum(efficiency_scores) / len(efficiency_scores)
                return {
                    'screen_time_hours': screen_time,
                    'avg_sleep_efficiency': round(avg_efficiency, 2),
                    'potential_impact': avg_efficiency < 75,
                    'recommendation': f'Reduce screen time before bed (currently {screen_time} hours)'
                }
        
        return {
            'screen_time_hours': screen_time,
            'potential_impact': False
        }
    
    def _analyze_exercise_timing(self, sessions: List[Dict[str, Any]], profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze exercise frequency and timing."""
        if not profile:
            return {}
        
        exercise = profile.get('exercise', 'rarely')
        
        return {
            'exercise_frequency': exercise,
            'has_regular_exercise': exercise in ['daily', '3-4-times'],
            'recommendation': 'Incorporate regular exercise' if exercise == 'rarely' else 'Maintain exercise routine'
        }
    
    def _identify_issues(self, analysis: Dict[str, Any], profile: Dict[str, Any] = None) -> List[str]:
        """Identify sleep issues from analysis."""
        issues = []
        
        # Duration issues
        duration_analysis = analysis.get('duration_analysis', {})
        if duration_analysis:
            avg = duration_analysis.get('average', 0)
            if avg < Config.OPTIMAL_SLEEP_DURATION_MIN:
                issues.append(f'Average sleep duration is too short ({avg:.1f} hours). Aim for 7-9 hours.')
            elif avg > Config.OPTIMAL_SLEEP_DURATION_MAX:
                issues.append(f'Average sleep duration is too long ({avg:.1f} hours). Consider if you need this much sleep.')
        
        # Consistency issues
        consistency = analysis.get('consistency_analysis', {})
        if consistency.get('overall_consistency', 1.0) < 0.6:
            issues.append('Sleep schedule is inconsistent. Try maintaining the same bedtime and wake time.')
        
        # Efficiency issues
        efficiency = analysis.get('efficiency_analysis', {})
        if efficiency.get('average', 100) < 70:
            issues.append(f'Sleep efficiency is low ({efficiency.get("average", 0):.0f}%). Focus on improving sleep quality.')
        
        # Interruption issues
        interruptions = analysis.get('interruption_analysis', {})
        if interruptions.get('interruption_rate', 0) > 0.5:
            issues.append('Frequent sleep interruptions detected. Consider optimizing your sleep environment.')
        
        # Caffeine issues
        caffeine = analysis.get('caffeine_analysis', {})
        if caffeine.get('potential_impact', False):
            issues.append('Caffeine intake may be affecting sleep quality. Avoid caffeine after 8 PM.')
        
        # Screen time issues
        screen_time = analysis.get('screen_time_analysis', {})
        if screen_time.get('potential_impact', False):
            issues.append(screen_time.get('recommendation', 'Reduce screen time before bed.'))
        
        return issues
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a summary of the analysis."""
        duration = analysis.get('duration_analysis', {})
        efficiency = analysis.get('efficiency_analysis', {})
        
        summary_parts = []
        
        if duration.get('average'):
            summary_parts.append(f"Average sleep duration: {duration['average']:.1f} hours")
        
        if efficiency.get('average'):
            summary_parts.append(f"Average efficiency: {efficiency['average']:.0f}%")
        
        consistency = analysis.get('consistency_analysis', {})
        if consistency.get('overall_consistency'):
            summary_parts.append(f"Schedule consistency: {consistency['overall_consistency']*100:.0f}%")
        
        if summary_parts:
            return ". ".join(summary_parts) + "."
        
        return "Sleep analysis completed."

