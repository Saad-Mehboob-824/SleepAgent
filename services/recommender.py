"""
Sleep recommendation engine.
Generates personalized sleep recommendations based on analysis.
"""
from typing import Dict, Any, List
from datetime import time, timedelta
from config import Config
from utils.logger import logger

class SleepRecommender:
    """Generates personalized sleep recommendations."""
    
    def generate_recommendations(
        self,
        analysis: Dict[str, Any],
        profile: Dict[str, Any] = None,
        trends: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive sleep recommendations.
        
        Args:
            analysis: Sleep analysis results
            profile: User profile data
            trends: Long-term trends from LTM
        
        Returns:
            Dictionary with recommendations and sleep plan
        """
        recommendations = {
            'ideal_sleep_window': self._calculate_ideal_sleep_window(analysis, profile),
            'caffeine_cutoff': self._calculate_caffeine_cutoff(profile),
            'light_exposure_management': self._generate_light_recommendations(profile),
            'bedroom_environment': self._generate_environment_recommendations(analysis),
            'wind_down_routine': self._generate_wind_down_routine(profile, analysis),
            'weekly_sleep_plan': self._generate_weekly_plan(analysis, profile),
            'personalized_tips': self._generate_personalized_tips(analysis, profile, trends)
        }
        
        return recommendations
    
    def _calculate_ideal_sleep_window(self, analysis: Dict[str, Any], profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate ideal bedtime and wake time."""
        # Base calculation from profile
        work_schedule = profile.get('work_schedule', '9am-5pm') if profile else '9am-5pm'
        age = profile.get('age', 30) if profile else 30
        avg_sleep_duration = profile.get('avg_sleep_duration', 8.0) if profile else 8.0
        
        # Use analysis if available
        duration_analysis = analysis.get('duration_analysis', {})
        if duration_analysis and duration_analysis.get('average'):
            avg_sleep_duration = duration_analysis['average']
        
        # Determine wake time based on work schedule
        if work_schedule == '9am-5pm':
            wake_hour = 6
            wake_minute = 30
        elif work_schedule == 'night-shift':
            wake_hour = 16
            wake_minute = 0
        elif work_schedule == 'flexible':
            wake_hour = 7
            wake_minute = 0
        else:  # rotating
            wake_hour = 6
            wake_minute = 0
        
        # Adjust for age
        if age < 25:
            wake_hour += 1
        elif age > 50:
            wake_hour -= 1
        
        # Calculate bedtime
        wake_time = time(wake_hour, wake_minute)
        bedtime_delta = timedelta(hours=avg_sleep_duration)
        
        from datetime import datetime, date
        wake_datetime = datetime.combine(date.today(), wake_time)
        bed_datetime = wake_datetime - bedtime_delta
        bedtime = bed_datetime.time()
        
        return {
            'recommended_bedtime': bedtime.strftime('%H:%M'),
            'recommended_waketime': wake_time.strftime('%H:%M'),
            'target_duration_hours': round(avg_sleep_duration, 1),
            'rationale': f'Based on {work_schedule} schedule and {age} years old'
        }
    
    def _calculate_caffeine_cutoff(self, profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate recommended caffeine cutoff time."""
        if not profile:
            return {
                'cutoff_time': '14:00',
                'recommendation': 'Avoid caffeine after 2 PM for optimal sleep'
            }
        
        caffeine_intake = profile.get('caffeine_intake', 'none')
        ideal_window = self._calculate_ideal_sleep_window({}, profile)
        bedtime_str = ideal_window.get('recommended_bedtime', '22:00')
        
        # Parse bedtime
        try:
            bedtime_hour = int(bedtime_str.split(':')[0])
            cutoff_hour = bedtime_hour - Config.CAFFEINE_CUTOFF_HOURS
            if cutoff_hour < 0:
                cutoff_hour += 24
            cutoff_time = f"{cutoff_hour:02d}:00"
        except:
            cutoff_time = '14:00'
        
        if caffeine_intake == 'none':
            recommendation = 'Great job avoiding caffeine! Continue this habit.'
        elif caffeine_intake == 'low':
            recommendation = f'Avoid caffeine after {cutoff_time} to improve sleep quality.'
        elif caffeine_intake == 'medium':
            recommendation = f'Limit caffeine intake and avoid after {cutoff_time}. Consider reducing to 1-2 cups per day.'
        else:  # high
            recommendation = f'Reduce caffeine intake significantly. Stop consuming caffeine after {cutoff_time}.'
        
        return {
            'cutoff_time': cutoff_time,
            'recommendation': recommendation,
            'current_intake': caffeine_intake
        }
    
    def _generate_light_recommendations(self, profile: Dict[str, Any] = None) -> List[str]:
        """Generate light exposure management recommendations."""
        recommendations = []
        
        screen_time = profile.get('screen_time', 0) if profile else 0
        
        if screen_time > Config.SCREEN_TIME_WARNING_HOURS:
            recommendations.append(f'Reduce screen time before bed (currently {screen_time} hours). Use blue light filters or reading mode.')
            recommendations.append('Dim lights 1-2 hours before bedtime to signal your body for sleep.')
        else:
            recommendations.append('Maintain low light exposure before bed. Consider using dimmable lights.')
        
        recommendations.append('Get natural sunlight exposure in the morning to regulate circadian rhythm.')
        recommendations.append('Use blackout curtains or eye mask if your bedroom is not dark enough.')
        
        return recommendations
    
    def _generate_environment_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate bedroom environment optimization recommendations."""
        recommendations = []
        
        interruptions = analysis.get('interruption_analysis', {})
        if interruptions.get('interruption_rate', 0) > 0.3:
            recommendations.append('Keep bedroom temperature between 65-68°F (18-20°C) for optimal sleep.')
            recommendations.append('Use white noise machine or earplugs to block disruptive sounds.')
            recommendations.append('Ensure your mattress and pillows are comfortable and supportive.')
            recommendations.append('Remove electronic devices from bedroom or use airplane mode.')
        else:
            recommendations.append('Your sleep environment seems good. Maintain current conditions.')
        
        recommendations.append('Keep bedroom dark, quiet, and cool.')
        recommendations.append('Reserve bedroom only for sleep and intimacy (no work or screens).')
        
        return recommendations
    
    def _generate_wind_down_routine(self, profile: Dict[str, Any] = None, analysis: Dict[str, Any] = None) -> List[str]:
        """Generate wind-down routine recommendations."""
        recommendations = []
        
        stress_level = profile.get('stress_level', 3) if profile else 3
        
        recommendations.append('Start wind-down routine 1 hour before bedtime.')
        
        if stress_level >= 4:
            recommendations.append('Practice relaxation techniques: meditation, deep breathing, or progressive muscle relaxation.')
            recommendations.append('Try journaling to clear your mind before bed.')
        else:
            recommendations.append('Maintain a consistent pre-sleep routine (reading, light stretching, or calming music).')
        
        recommendations.append('Take a warm bath or shower 1-2 hours before bed (body temperature drop promotes sleep).')
        recommendations.append('Avoid stimulating activities, work, or intense exercise close to bedtime.')
        
        consistency = analysis.get('consistency_analysis', {}) if analysis else {}
        if consistency.get('overall_consistency', 1.0) < 0.7:
            recommendations.append('Establish a fixed bedtime routine to signal your body it\'s time to sleep.')
        
        return recommendations
    
    def _generate_weekly_plan(self, analysis: Dict[str, Any], profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a weekly sleep improvement plan."""
        ideal_window = self._calculate_ideal_sleep_window(analysis, profile)
        
        plan = {
            'week_goal': 'Establish consistent sleep schedule',
            'daily_bedtime': ideal_window.get('recommended_bedtime'),
            'daily_waketime': ideal_window.get('recommended_waketime'),
            'weekly_tasks': []
        }
        
        # Add tasks based on issues
        issues = analysis.get('issues', [])
        
        if any('duration' in issue.lower() for issue in issues):
            plan['weekly_tasks'].append('Gradually adjust sleep duration to reach 7-9 hours')
        
        if any('consistent' in issue.lower() for issue in issues):
            plan['weekly_tasks'].append('Maintain same bedtime and wake time every day, including weekends')
        
        if any('caffeine' in issue.lower() for issue in issues):
            plan['weekly_tasks'].append('Reduce caffeine intake and observe sleep quality improvements')
        
        if any('screen' in issue.lower() for issue in issues):
            plan['weekly_tasks'].append('Reduce screen time 2 hours before bed')
        
        if not plan['weekly_tasks']:
            plan['weekly_tasks'].append('Maintain current sleep habits and track improvements')
        
        return plan
    
    def _generate_personalized_tips(self, analysis: Dict[str, Any], profile: Dict[str, Any] = None, trends: Dict[str, Any] = None) -> List[str]:
        """Generate personalized tips based on analysis and trends."""
        tips = []
        
        # Tips from analysis issues
        issues = analysis.get('issues', [])
        for issue in issues[:3]:  # Top 3 issues
            tips.append(issue)
        
        # Tips from profile
        if profile:
            exercise = profile.get('exercise', 'rarely')
            if exercise == 'rarely':
                tips.append('Incorporate regular exercise into your routine (3-4 times per week) for better sleep.')
            elif exercise == 'daily':
                tips.append('Great job with daily exercise! Avoid intense workouts within 3 hours of bedtime.')
        
        # Tips from trends
        if trends:
            avg_duration = trends.get('avg_duration', 0)
            if avg_duration and avg_duration < Config.OPTIMAL_SLEEP_DURATION_MIN:
                tips.append(f'Your average sleep duration is {avg_duration:.1f} hours. Gradually increase to 7-9 hours for optimal rest.')
        
        # General tips if not enough
        if len(tips) < 3:
            tips.extend([
                'Maintain a consistent sleep schedule, even on weekends.',
                'Create a relaxing bedtime routine to signal your body for sleep.',
                'Avoid large meals and alcohol close to bedtime.'
            ])
        
        return tips[:6]  # Limit to 6 tips

