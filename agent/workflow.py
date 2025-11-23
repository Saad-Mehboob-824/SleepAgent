"""
LangGraph workflow definition for the Sleep Optimizer Agent.
"""
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    validation_node,
    memory_fetch_node,
    reasoning_node,
    recommendation_engine_node,
    memory_write_node,
    scorer_node,
    formatter_node
)
from utils.logger import logger

def create_workflow() -> StateGraph:
    """
    Create and configure the LangGraph workflow.
    
    Workflow structure:
    input → validation → memory_fetch → reasoning → [recommendation_engine, scorer] → memory_write → formatter → output
    
    Returns:
        Configured StateGraph
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("validation", validation_node)
    workflow.add_node("memory_fetch", memory_fetch_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("recommendation_engine", recommendation_engine_node)
    workflow.add_node("scorer", scorer_node)
    workflow.add_node("memory_write", memory_write_node)
    workflow.add_node("formatter", formatter_node)
    
    # Define edges
    workflow.set_entry_point("validation")
    
    # Validation → memory_fetch (if valid) or END (if error)
    workflow.add_conditional_edges(
        "validation",
        _should_continue,
        {
            "continue": "memory_fetch",
            "error": END
        }
    )
    
    # memory_fetch → reasoning
    workflow.add_edge("memory_fetch", "reasoning")
    
    # reasoning → [recommendation_engine, scorer] (parallel)
    workflow.add_edge("reasoning", "recommendation_engine")
    workflow.add_edge("reasoning", "scorer")
    
    # Both recommendation_engine and scorer → memory_write
    workflow.add_edge("recommendation_engine", "memory_write")
    workflow.add_edge("scorer", "memory_write")
    
    # memory_write → formatter
    workflow.add_edge("memory_write", "formatter")
    
    # formatter → END
    workflow.add_edge("formatter", END)
    
    return workflow.compile()

def _should_continue(state: AgentState) -> str:
    """
    Conditional edge function to determine if workflow should continue.
    
    Args:
        state: Current agent state
    
    Returns:
        "continue" if valid, "error" if errors found
    """
    if state.get('status') == 'error' or state.get('errors'):
        return "error"
    return "continue"

# Global workflow instance
workflow = create_workflow()

def process_task(task_data: dict) -> dict:
    """
    Process a task through the workflow.
    
    Args:
        task_data: Task data from Supervisor Agent
    
    Returns:
        Processed result dictionary
    """
    # Initialize state
    initial_state: AgentState = {
        'task_id': task_data.get('task_id', ''),
        'user_id': task_data.get('user_id', ''),
        'payload': task_data.get('payload', {}),
        'memory': {},
        'stm_sessions': None,
        'ltm_data': None,
        'analysis': None,
        'sleep_score': 0,
        'confidence': 0.0,
        'recommendations': None,
        'personalized_tips': [],
        'result': None,
        'summary': '',
        'issues': [],
        'errors': [],
        'status': 'processing'
    }
    
    try:
        # Run workflow
        final_state = workflow.invoke(initial_state)
        
        # Check for errors
        if final_state.get('status') == 'error' or final_state.get('errors'):
            return {
                'task_id': final_state['task_id'],
                'status': 'error',
                'error': '; '.join(final_state.get('errors', ['Unknown error']))
            }
        
        # Return successful result
        return {
            'task_id': final_state['task_id'],
            'status': 'completed',
            'result': final_state.get('result', {})
        }
    
    except Exception as e:
        logger.error(f'Workflow execution error: {str(e)}', 
                     extra={'task_id': task_data.get('task_id'), 
                            'user_id': task_data.get('user_id')})
        return {
            'task_id': task_data.get('task_id', ''),
            'status': 'error',
            'error': f'Workflow execution failed: {str(e)}'
        }

