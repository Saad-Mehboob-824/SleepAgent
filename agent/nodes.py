"""
LangGraph workflow nodes for the Sleep Optimizer Agent.
"""
from typing import Dict, Any, List, Optional
from agent.state import AgentState
from memory.stm import ShortTermMemory
from memory.ltm import LongTermMemory
from services.analyzer import SleepAnalyzer
from services.scorer import SleepScorer
from services.recommender import SleepRecommender
from utils.validators import validate_task_request, validate_sleep_session
from utils.logger import logger, log_with_context
from config import Config

# Initialize services
stm = ShortTermMemory()
ltm = LongTermMemory()
analyzer = SleepAnalyzer()
scorer = SleepScorer()
recommender = SleepRecommender()

def validation_node(state: AgentState) -> AgentState:
    """
    Validate input task request.
    
    Node: validation
    """
    log_with_context(logger, 'INFO', f'Validating task {state["task_id"]}', 
                     user_id=state.get('user_id'), task_id=state.get('task_id'))
    
    try:
        # Validate task structure
        task_data = {
            'task_id': state['task_id'],
            'user_id': state['user_id'],
            'payload': state['payload']
        }
        
        is_valid, error_msg = validate_task_request(task_data)
        
        if not is_valid:
            state['errors'].append(f'Validation error: {error_msg}')
            state['status'] = 'error'
            return state
        
        # Validate sleep sessions if present
        sessions = state['payload'].get('sleep_sessions', [])
        for i, session in enumerate(sessions):
            is_valid, error_msg = validate_sleep_session(session)
            if not is_valid:
                state['errors'].append(f'Session {i} validation error: {error_msg}')
        
        if state['errors']:
            state['status'] = 'error'
        else:
            state['status'] = 'processing'
        
        log_with_context(logger, 'INFO', 'Validation completed', 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
        
    except Exception as e:
        error_msg = f'Validation node error: {str(e)}'
        state['errors'].append(error_msg)
        state['status'] = 'error'
        log_with_context(logger, 'ERROR', error_msg, 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
    
    return state

def memory_fetch_node(state: AgentState) -> AgentState:
    """
    Retrieve STM and LTM for the user.
    This node automatically fetches all existing memory data for the user_id,
    making stored memory the primary data source for analysis.
    
    Node: memory_fetch
    """
    log_with_context(logger, 'INFO', f'Fetching memory for user {state["user_id"]}', 
                     user_id=state.get('user_id'), task_id=state.get('task_id'))
    
    try:
        user_id = state['user_id']
        
        # Fetch complete STM data (primary source)
        stm_sessions = stm.get_sessions(user_id)
        state['stm_sessions'] = stm_sessions or []
        
        # Fetch complete LTM data (primary source)
        ltm_data = ltm.get_memory(user_id)
        state['ltm_data'] = ltm_data or {}
        
        # Get payload sessions (new sessions to be added)
        payload_sessions = state['payload'].get('sleep_sessions', [])
        
        # Combine all sessions: existing STM (primary) + new payload sessions
        all_sessions = state['stm_sessions'] + payload_sessions
        
        # Extract LTM components for easy access
        ltm_trends = state['ltm_data'].get('trends', {}) if state['ltm_data'] else {}
        ltm_patterns = state['ltm_data'].get('patterns', []) if state['ltm_data'] else []
        ltm_preferences = state['ltm_data'].get('preferences', {}) if state['ltm_data'] else {}
        
        state['memory'] = {
            'stm_count': len(state['stm_sessions']),
            'payload_count': len(payload_sessions),
            'ltm_available': bool(ltm_data),
            'ltm_trends': ltm_trends,
            'ltm_patterns': ltm_patterns,
            'ltm_preferences': ltm_preferences,
            'total_sessions': len(all_sessions)
        }
        
        log_with_context(logger, 'INFO', 
                         f'Retrieved {len(state["stm_sessions"])} existing STM sessions, '
                         f'{len(payload_sessions)} new payload sessions, '
                         f'LTM available: {bool(ltm_data)}', 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
        
    except Exception as e:
        error_msg = f'Memory fetch error: {str(e)}'
        state['errors'].append(error_msg)
        log_with_context(logger, 'ERROR', error_msg, 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
    
    return state

def reasoning_node(state: AgentState) -> AgentState:
    """
    Perform sleep analysis using analyzer and optional LLM.
    Prioritizes existing STM sessions and uses LTM trends/patterns in analysis.
    
    Node: reasoning
    """
    log_with_context(logger, 'INFO', 'Starting sleep analysis', 
                     user_id=state.get('user_id'), task_id=state.get('task_id'))
    
    try:
        # Prioritize existing STM sessions (primary source) over payload sessions
        stm_sessions = state.get('stm_sessions', [])
        payload_sessions = state['payload'].get('sleep_sessions', [])
        
        # Combine: existing STM first, then new payload sessions
        all_sessions = stm_sessions + payload_sessions
        
        # Get user profile from payload
        profile = state['payload'].get('profile', {})
        
        # Get existing LTM data to enhance analysis
        ltm_data = state.get('ltm_data', {})
        ltm_trends = ltm_data.get('trends', {}) if ltm_data else {}
        ltm_patterns = ltm_data.get('patterns', []) if ltm_data else []
        
        # Perform analysis with all available data
        analysis = analyzer.analyze(all_sessions, profile)
        state['analysis'] = analysis
        
        # Enhance analysis with existing LTM trends if available
        if ltm_trends:
            # Merge LTM trends into analysis for comprehensive view
            if 'duration_analysis' not in analysis:
                analysis['duration_analysis'] = {}
            if 'avg_duration' in ltm_trends:
                analysis['duration_analysis']['ltm_average'] = ltm_trends.get('avg_duration')
            
            if 'efficiency_analysis' not in analysis:
                analysis['efficiency_analysis'] = {}
            if 'avg_efficiency' in ltm_trends:
                analysis['efficiency_analysis']['ltm_average'] = ltm_trends.get('avg_efficiency')
        
        # Add LTM patterns to analysis context
        if ltm_patterns:
            analysis['ltm_patterns'] = ltm_patterns
        
        state['analysis'] = analysis
        
        # Optional: Use Gemini LLM for enhanced reasoning
        if Config.USE_GEMINI and Config.GEMINI_API_KEY:
            try:
                llm_insights = _get_llm_insights(all_sessions, profile, analysis)
                if llm_insights:
                    analysis['llm_insights'] = llm_insights
                    state['analysis'] = analysis
            except Exception as e:
                log_with_context(logger, 'WARNING', f'LLM reasoning failed: {str(e)}', 
                                 user_id=state.get('user_id'), task_id=state.get('task_id'))
        
        log_with_context(logger, 'INFO', 
                         f'Analysis completed using {len(stm_sessions)} existing sessions '
                         f'and {len(payload_sessions)} new sessions', 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
        
    except Exception as e:
        error_msg = f'Reasoning node error: {str(e)}'
        state['errors'].append(error_msg)
        log_with_context(logger, 'ERROR', error_msg, 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
    
    return state

def recommendation_engine_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate personalized recommendations.
    Uses existing LTM trends, patterns, and preferences as primary source.
    
    Node: recommendation_engine
    Returns only the keys it modifies to avoid conflicts with parallel nodes.
    """
    log_with_context(logger, 'INFO', 'Generating recommendations', 
                     user_id=state.get('user_id'), task_id=state.get('task_id'))
    
    result = {
        'recommendations': None,
        'personalized_tips': []
    }
    
    try:
        analysis = state.get('analysis', {})
        profile = state['payload'].get('profile', {})
        
        # Get existing LTM data (primary source for recommendations)
        ltm_data = state.get('ltm_data', {})
        trends = ltm_data.get('trends', {}) if ltm_data else {}
        patterns = ltm_data.get('patterns', []) if ltm_data else []
        preferences = ltm_data.get('preferences', {}) if ltm_data else {}
        
        # Enhance profile with stored preferences from LTM
        if preferences:
            # Merge LTM preferences into profile for better recommendations
            enhanced_profile = profile.copy()
            if 'preferred_duration' in preferences:
                enhanced_profile['preferred_duration'] = preferences['preferred_duration']
            if 'preferred_bedtime' in preferences:
                enhanced_profile['preferred_bedtime'] = preferences['preferred_bedtime']
            profile = enhanced_profile
        
        # Generate recommendations using existing LTM trends as primary source
        recommendations = recommender.generate_recommendations(analysis, profile, trends)
        result['recommendations'] = recommendations
        
        # Enhance recommendations with stored patterns
        if patterns:
            # Add pattern-based recommendations
            pattern_recommendations = []
            for pattern in patterns:
                if isinstance(pattern, dict):
                    pattern_type = pattern.get('type', '')
                    if pattern_type == 'consistent_bedtime':
                        pattern_recommendations.append('Maintain your consistent bedtime routine')
                    elif pattern_type == 'sufficient_data':
                        pattern_recommendations.append('Continue tracking for better insights')
            
            if pattern_recommendations:
                existing_tips = recommendations.get('personalized_tips', [])
                recommendations['personalized_tips'] = existing_tips + pattern_recommendations
        
        # Extract personalized tips
        result['personalized_tips'] = recommendations.get('personalized_tips', [])
        
        log_with_context(logger, 'INFO', 
                         f'Recommendations generated using LTM trends and {len(patterns)} patterns', 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
        
    except Exception as e:
        error_msg = f'Recommendation engine error: {str(e)}'
        # Log error but don't add to state (errors are handled by other nodes)
        log_with_context(logger, 'ERROR', error_msg, 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
        # Set default values on error
        result['recommendations'] = {}
        result['personalized_tips'] = []
    
    return result

def memory_write_node(state: AgentState) -> AgentState:
    """
    Persist new insights to memory (STM and LTM).
    Only saves new sessions from payload (STM handles deduplication).
    Updates LTM with all available sessions (existing + new).
    
    Node: memory_write
    """
    log_with_context(logger, 'INFO', 'Writing to memory', 
                     user_id=state.get('user_id'), task_id=state.get('task_id'))
    
    try:
        user_id = state['user_id']
        payload_sessions = state['payload'].get('sleep_sessions', [])
        existing_stm_sessions = state.get('stm_sessions', [])
        
        # Update STM with new sessions only (STM.save_sessions handles deduplication)
        if payload_sessions:
            # STM.save_sessions will merge with existing and deduplicate
            stm.save_sessions(user_id, payload_sessions)
            log_with_context(logger, 'INFO', 
                             f'Saved {len(payload_sessions)} new session(s) to STM', 
                             user_id=state.get('user_id'), task_id=state.get('task_id'))
        
        # Get recommendations, sleep_score, and confidence from state FIRST
        # These should be in state after parallel nodes (recommendation_engine and scorer) complete
        recommendations = state.get('recommendations')
        sleep_score = state.get('sleep_score', 0)
        confidence = state.get('confidence', 0.0)
        personalized_tips = state.get('personalized_tips', [])
        
        log_with_context(logger, 'INFO', 
                         f'Memory write - State check: recommendations={recommendations is not None} '
                         f'(type: {type(recommendations).__name__}), sleep_score={sleep_score}, '
                         f'confidence={confidence}, tips={len(personalized_tips)}', 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
        
        # Update LTM with all available sessions (existing + new)
        # This ensures LTM trends are calculated from complete history
        all_sessions = existing_stm_sessions + payload_sessions
        if all_sessions:
            ltm.update_trends(user_id, all_sessions)
            log_with_context(logger, 'INFO', 
                             f'Updated LTM trends with {len(all_sessions)} total session(s)', 
                             user_id=state.get('user_id'), task_id=state.get('task_id'))
        
        # Get issues from analysis (they're extracted in formatter_node, but we can get them here too)
        analysis = state.get('analysis', {})
        issues = state.get('issues', []) or analysis.get('issues', [])
        
        # Save recommendations, sleep_score, confidence, and issues to LTM
        # Always save if we have any data (recommendations dict, score > 0, confidence > 0, tips, or issues)
        has_recommendations = recommendations is not None and isinstance(recommendations, dict)
        has_score = sleep_score > 0 or confidence > 0.0
        has_tips = len(personalized_tips) > 0
        has_issues = len(issues) > 0
        
        if has_recommendations or has_score or has_tips or has_issues:
            # Ensure recommendations is a dict (not None)
            if recommendations is None:
                recommendations = {}
            
            success = ltm.update_recommendations(
                user_id, 
                recommendations, 
                sleep_score, 
                confidence, 
                personalized_tips,
                issues
            )
            
            if success:
                log_with_context(logger, 'INFO', 
                                 f'Successfully saved recommendations to LTM: score={sleep_score}, '
                                 f'confidence={confidence}, rec_keys={list(recommendations.keys()) if recommendations else "none"}, '
                                 f'tips={len(personalized_tips)}, issues={len(issues)}', 
                                 user_id=state.get('user_id'), task_id=state.get('task_id'))
            else:
                log_with_context(logger, 'ERROR', 
                                 'Failed to save recommendations to LTM', 
                                 user_id=state.get('user_id'), task_id=state.get('task_id'))
        else:
            log_with_context(logger, 'WARNING', 
                             f'No recommendations data to save - recommendations: {has_recommendations}, '
                             f'score: {has_score}, tips: {has_tips}, issues: {has_issues}', 
                             user_id=state.get('user_id'), task_id=state.get('task_id'))
        
        log_with_context(logger, 'INFO', 'Memory updated successfully', 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
        
    except Exception as e:
        error_msg = f'Memory write error: {str(e)}'
        state['errors'].append(error_msg)
        log_with_context(logger, 'ERROR', error_msg, 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
    
    return state

def scorer_node(state: AgentState) -> Dict[str, Any]:
    """
    Calculate sleep score and confidence.
    
    Node: scorer (runs in parallel with recommendation_engine)
    Returns only the keys it modifies to avoid conflicts with parallel nodes.
    """
    log_with_context(logger, 'INFO', 'Calculating sleep score', 
                     user_id=state.get('user_id'), task_id=state.get('task_id'))
    
    result = {
        'sleep_score': 0,
        'confidence': 0.0
    }
    
    try:
        payload_sessions = state['payload'].get('sleep_sessions', [])
        stm_sessions = state.get('stm_sessions', [])
        all_sessions = payload_sessions + stm_sessions
        
        analysis = state.get('analysis', {})
        
        # Calculate score
        score_result = scorer.calculate_score(all_sessions, analysis)
        result['sleep_score'] = score_result['sleep_score']
        result['confidence'] = score_result['confidence']
        
        log_with_context(logger, 'INFO', 
                         f'Sleep score calculated: {result["sleep_score"]} (confidence: {result["confidence"]})', 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
        
    except Exception as e:
        error_msg = f'Scorer node error: {str(e)}'
        # Log error but don't add to state (errors are handled by other nodes)
        log_with_context(logger, 'ERROR', error_msg, 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
        # Set default values on error
        result['sleep_score'] = 0
        result['confidence'] = 0.0
    
    return result

def formatter_node(state: AgentState) -> AgentState:
    """
    Format the final output response.
    
    Node: formatter
    """
    log_with_context(logger, 'INFO', 'Formatting output', 
                     user_id=state.get('user_id'), task_id=state.get('task_id'))
    
    try:
        # Extract issues from analysis
        analysis = state.get('analysis', {})
        issues = analysis.get('issues', [])
        state['issues'] = issues
        
        # Generate summary
        summary = analysis.get('summary', 'Sleep analysis completed.')
        state['summary'] = summary
        
        # Format result
        result = {
            'summary': summary,
            'issues': issues,
            'recommendations': state.get('recommendations', {}),
            'sleep_score': state['sleep_score'],
            'confidence': state['confidence'],
            'personalized_tips': state.get('personalized_tips', [])
        }
        
        state['result'] = result
        state['status'] = 'completed'
        
        log_with_context(logger, 'INFO', 'Output formatted', 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
        
    except Exception as e:
        error_msg = f'Formatter node error: {str(e)}'
        state['errors'].append(error_msg)
        state['status'] = 'error'
        log_with_context(logger, 'ERROR', error_msg, 
                         user_id=state.get('user_id'), task_id=state.get('task_id'))
    
    return state

def _get_llm_insights(sessions: List[Dict[str, Any]], profile: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get additional insights from Gemini LLM (optional).
    
    Args:
        sessions: Sleep sessions
        profile: User profile
        analysis: Analysis results
    
    Returns:
        LLM insights dictionary or None
    """
    if not Config.USE_GEMINI or not Config.GEMINI_API_KEY:
        return None
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare prompt
        prompt = f"""
        Analyze the following sleep data and provide insights:
        
        Sleep Sessions: {len(sessions)} sessions
        Average Duration: {analysis.get('duration_analysis', {}).get('average', 0):.1f} hours
        Sleep Efficiency: {analysis.get('efficiency_analysis', {}).get('average', 0):.0f}%
        
        User Profile:
        - Age: {profile.get('age', 'N/A')}
        - Work Schedule: {profile.get('work_schedule', 'N/A')}
        - Caffeine Intake: {profile.get('caffeine_intake', 'N/A')}
        
        Provide 2-3 key insights in JSON format: {{"insights": ["insight1", "insight2"]}}
        """
        
        response = model.generate_content(prompt)
        
        # Parse response (simplified - would need proper JSON parsing)
        return {
            'llm_insights': response.text[:500]  # Limit length
        }
    except Exception as e:
        logger.warning(f'LLM insight generation failed: {str(e)}')
        return None

