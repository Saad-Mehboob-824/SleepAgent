# Sleep Optimizer Worker Agent

A plug-and-play Worker Agent for sleep analysis and personalized recommendations. This agent integrates with a Supervisor Agent system using LangGraph workflows, maintains user-specific memory (STM/LTM), and generates AI-powered sleep insights.

## Features

- **Sleep Analysis**: Comprehensive analysis of sleep patterns, duration, consistency, and efficiency
- **Personalized Recommendations**: AI-generated recommendations for ideal sleep windows, caffeine cutoff, environment optimization, and wind-down routines
- **Memory System**: Short-term (STM) and long-term (LTM) memory per user for trend analysis
- **Sleep Scoring**: Calculates sleep quality scores (0-100) with confidence levels
- **LangGraph Workflow**: Orchestrated multi-step processing pipeline
- **RESTful API**: Standard HTTP endpoints for Supervisor Agent integration

## Architecture

```
Supervisor Agent → POST /task → LangGraph Workflow → Analysis → Recommendations → Response
```

### Workflow Pipeline

1. **Validation**: Validates input task structure
2. **Memory Fetch**: Retrieves STM and LTM for user
3. **Reasoning**: Analyzes sleep data (with optional LLM enhancement)
4. **Recommendation Engine**: Generates personalized recommendations
5. **Scorer**: Calculates sleep score and confidence
6. **Memory Write**: Persists insights to memory
7. **Formatter**: Structures final output

## Installation

### Prerequisites

- Python 3.8+
- MongoDB (optional, for persistent storage)
- Gemini API key (optional, for LLM features)

### Setup

1. **Clone and navigate to the Backend directory:**
```bash
cd Backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
Create a `.env` file in the Backend directory:
```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
HOST=0.0.0.0
PORT=8000

# MongoDB (Optional)
USE_MONGODB=False
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=sleep_optimizer_agent

# Memory Storage
MEMORY_STORAGE_PATH=instance/memory
STM_RETENTION_DAYS=7
LTM_RETENTION_DAYS=365

# Gemini API (Optional)
USE_GEMINI=False
GEMINI_API_KEY=your-gemini-api-key-here

# Agent Configuration
AGENT_ID=sleep-optimizer-agent-001
AGENT_VERSION=1.0.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=instance/logs/agent.log
```

5. **Run the application:**
```bash
python app.py
```

The agent will start on `http://localhost:8000`

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. POST /register
Register the agent with the Supervisor.

**Request:**
```json
POST /register
```

**Response:**
```json
{
  "agent_id": "sleep-optimizer-agent-001",
  "agent_name": "Sleep Optimizer Agent",
  "agent_description": "AI-powered sleep analysis and recommendation agent",
  "version": "1.0.0",
  "capabilities": [
    "sleep_analysis",
    "sleep_scoring",
    "recommendation_generation",
    "memory_management",
    "trend_analysis",
    "personalized_planning"
  ],
  "endpoints": {
    "task": "/task",
    "health": "/health",
    "memory": "/memory",
    "logs": "/logs"
  }
}
```

#### 2. POST /task
Process a sleep analysis task from the Supervisor Agent.

**Request:**
```json
POST /task
Content-Type: application/json

{
  "task_id": "task_123",
  "user_id": "U_101",
  "payload": {
    "sleep_sessions": [
      {
        "bedtime": "22:30:00",
        "waketime": "06:30:00",
        "duration_hours": 8.0,
        "efficiency_score": 85,
        "interruptions": [],
        "morning_mood": 7,
        "session_date": "2024-01-15"
      }
    ],
    "profile": {
      "age": 30,
      "work_schedule": "9am-5pm",
      "caffeine_intake": "medium",
      "screen_time": 2.0,
      "exercise": "3-4-times",
      "stress_level": 3
    }
  }
}
```

**Response:**
```json
{
  "task_id": "task_123",
  "status": "completed",
  "result": {
    "summary": "Average sleep duration: 8.0 hours. Average efficiency: 85%. Schedule consistency: 90%.",
    "issues": [
      "Consider reducing screen time before bed (currently 2.0 hours)"
    ],
    "recommendations": {
      "ideal_sleep_window": {
        "recommended_bedtime": "22:30",
        "recommended_waketime": "06:30",
        "target_duration_hours": 8.0
      },
      "caffeine_cutoff": {
        "cutoff_time": "14:30",
        "recommendation": "Limit caffeine intake and avoid after 14:30"
      },
      "personalized_tips": [
        "Reduce screen time before bed. Use blue light filters or reading mode.",
        "Maintain a consistent sleep schedule, even on weekends."
      ]
    },
    "sleep_score": 85,
    "confidence": 0.92,
    "personalized_tips": [
      "Reduce screen time before bed (currently 2.0 hours). Use blue light filters or reading mode.",
      "Maintain a consistent sleep schedule, even on weekends."
    ]
  }
}
```

#### 3. GET /health
Check agent health status.

**Request:**
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "agent_id": "sleep-optimizer-agent-001",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "uptime_hours": 1.0,
  "memory_usage_mb": 128.5,
  "storage_healthy": true,
  "features": {
    "llm_enabled": false,
    "mongodb_enabled": false
  },
  "timestamp": "2024-01-15T12:00:00Z"
}
```

#### 4. GET /memory
Retrieve memory data for a specific user.

**Request:**
```bash
GET /memory?user_id=U_101
```

**Response:**
```json
{
  "user_id": "U_101",
  "stm": {
    "sessions": [
      {
        "bedtime": "22:30:00",
        "waketime": "06:30:00",
        "duration_hours": 8.0
      }
    ],
    "count": 1
  },
  "ltm": {
    "trends": {
      "avg_duration": 8.0,
      "avg_efficiency": 85.0
    },
    "patterns": [
      {
        "type": "consistent_bedtime",
        "description": "Maintains consistent bedtime"
      }
    ],
    "preferences": {
      "preferred_duration": 8.0
    },
    "available": true
  }
}
```

#### 5. GET /logs
Retrieve recent agent logs.

**Request:**
```bash
GET /logs?limit=100&level=INFO
```

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-01-15T12:00:00Z",
      "level": "INFO",
      "message": "Processing task task_123",
      "user_id": "U_101",
      "task_id": "task_123"
    }
  ],
  "count": 1,
  "limit": 100,
  "level_filter": "INFO"
}
```

## Data Formats

### Sleep Session
```json
{
  "bedtime": "22:30:00",          // Required: HH:MM:SS format
  "waketime": "06:30:00",         // Required: HH:MM:SS format
  "duration_hours": 8.0,          // Required: float (3-16 hours)
  "efficiency_score": 85,         // Optional: 0-100
  "interruptions": [              // Optional: array
    {
      "time": "02:30:00",
      "duration_min": 5
    }
  ],
  "morning_mood": 7,              // Optional: 1-10
  "session_date": "2024-01-15"    // Optional: YYYY-MM-DD
}
```

### User Profile
```json
{
  "age": 30,                      // Optional: 1-120
  "work_schedule": "9am-5pm",    // Optional: "9am-5pm", "flexible", "night-shift", "rotating"
  "caffeine_intake": "medium",   // Optional: "none", "low", "medium", "high"
  "screen_time": 2.0,             // Optional: float (hours before bed)
  "exercise": "3-4-times",        // Optional: "daily", "3-4-times", "1-2-times", "rarely"
  "stress_level": 3               // Optional: 1-5
}
```

## Memory System

### Short-Term Memory (STM)
- Stores last 3-7 days of sleep sessions
- Fast access for recent patterns
- Auto-expires old entries
- Retention: Configurable (default: 7 days)

### Long-Term Memory (LTM)
- Stores trends and patterns
- Weekly/monthly averages
- User preferences
- Retention: Configurable (default: 365 days)

## Error Handling

All endpoints return JSON error responses:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "additional": "information"
  }
}
```

Common error codes:
- `VALIDATION_ERROR`: Input validation failed
- `MISSING_PARAMETER`: Required parameter missing
- `INTERNAL_ERROR`: Server-side error
- `NOT_FOUND`: Endpoint not found
- `METHOD_NOT_ALLOWED`: HTTP method not allowed

## Supervisor Agent Integration

### Integration Steps

1. **Register the agent:**
```bash
POST http://localhost:8000/register
```

2. **Send tasks:**
```bash
POST http://localhost:8000/task
Content-Type: application/json

{
  "task_id": "unique_task_id",
  "user_id": "user_identifier",
  "payload": {
    "sleep_sessions": [...],
    "profile": {...}
  }
}
```

3. **Monitor health:**
```bash
GET http://localhost:8000/health
```

### Response Format

The agent always returns:
```json
{
  "task_id": "task_123",
  "status": "completed" | "error",
  "result": {...} | null,
  "error": "..." | null
}
```

## Configuration

See `config.py` for all configuration options. Key settings:

- **Memory Storage**: JSON file-based (default) or MongoDB
- **LLM Support**: Optional Gemini API integration
- **CORS**: Configurable origins for Supervisor Agent
- **Logging**: Structured JSON logs with rotation

## Testing

Run tests:
```bash
pytest tests/
```

## Development

### Project Structure
```
Backend/
├── app.py                 # Flask application
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── agent/                 # LangGraph workflow
│   ├── workflow.py
│   ├── nodes.py
│   └── state.py
├── memory/                # Memory system
│   ├── stm.py
│   ├── ltm.py
│   └── storage.py
├── services/              # Analysis services
│   ├── analyzer.py
│   ├── recommender.py
│   └── scorer.py
├── routes/                # API routes
│   ├── task.py
│   ├── register.py
│   ├── health.py
│   ├── memory.py
│   └── logs.py
└── utils/                 # Utilities
    ├── logger.py
    └── validators.py
```

## License

This project is part of a multi-agent system architecture.

## Support

For issues or questions, refer to the Supervisor Agent team or project documentation.

