"""
LangGraph state definition for the Sleep Optimizer Agent workflow.
"""
from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """State schema for the agent workflow."""
    # Input data
    task_id: str
    user_id: str
    payload: Dict[str, Any]
    
    # Memory
    memory: Dict[str, Any]
    stm_sessions: Optional[List[Dict[str, Any]]]
    ltm_data: Optional[Dict[str, Any]]
    
    # Analysis
    analysis: Optional[Dict[str, Any]]
    sleep_score: int
    confidence: float
    
    # Recommendations
    recommendations: Optional[Dict[str, Any]]
    personalized_tips: List[str]
    
    # Output
    result: Optional[Dict[str, Any]]
    summary: str
    issues: List[str]
    
    # Error handling
    errors: List[str]
    status: str  # 'processing', 'completed', 'error'

