# Worker Agent API Documentation

## Overview

The **Sleep Optimizer Worker Agent** is a specialized AI agent that analyzes sleep patterns, generates personalized recommendations, and maintains user-specific memory for sleep optimization.

**Base URL**: `http://localhost:8000`  
**Version**: 1.0.0  
**Agent ID**: `sleep-optimizer-agent-001`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Profile Management](#profile-management)
3. [Sleep Session Management](#sleep-session-management)
4. [Analysis & Recommendations](#analysis--recommendations)
5. [Memory Management](#memory-management)
6. [System Endpoints](#system-endpoints)
7. [Error Handling](#error-handling)
8. [Data Models](#data-models)

---

## Authentication

The Worker requires a valid `user_id` for all operations. The user must be verified with the Supervisor before accessing Worker endpoints.

### User ID Format
- **Pattern**: `U_<unique_identifier>`
- **Example**: `U_55bee4e9`
- **Invalid**: `default_user`, empty string, or null

---

## Profile Management

### Get User Profile

Retrieve domain-specific profile data from Worker's Long-Term Memory (LTM).

**Endpoint**: `GET /api/profile`

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User identifier |

**Request Example**:
```http
GET /api/profile?user_id=U_55bee4e9
```

**Response** (200 OK):
```json
{
  "user_id": "U_55bee4e9",
  "profile": {
    "age": 28,
    "work_schedule": "9am-5pm",
    "caffeine_intake": "medium",
    "screen_time": 2.5,
    "exercise": "3-4-times",
    "stress_level": 3
  }
}
```

**Response** (Empty Profile):
```json
{
  "user_id": "U_55bee4e9",
  "profile": {}
}
```

---

### Save User Profile

Store or update domain-specific profile data in Worker's LTM.

**Endpoint**: `PUT /api/profile`

**Request Body**:
```json
{
  "user_id": "U_55bee4e9",
  "profile": {
    "age": 28,
    "work_schedule": "9am-5pm",
    "caffeine_intake": "medium",
    "screen_time": 2.5,
    "exercise": "3-4-times",
    "stress_level": 3
  }
}
```

**Profile Fields**:
| Field | Type | Options | Description |
|-------|------|---------|-------------|
| `age` | integer | 1-120 | User's age in years |
| `work_schedule` | string | `9am-5pm`, `flexible`, `night-shift`, `rotating` | Work schedule type |
| `caffeine_intake` | string | `none`, `low`, `medium`, `high` | Daily caffeine consumption |
| `screen_time` | float | 0-24 | Hours of screen time before bed |
| `exercise` | string | `daily`, `3-4-times`, `1-2-times`, `rarely` | Exercise frequency per week |
| `stress_level` | integer | 1-5 | Stress level (1=low, 5=high) |

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Profile saved successfully",
  "user_id": "U_55bee4e9"
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "Invalid user_id. Please login through supervisor agent.",
  "code": "INVALID_USER_ID"
}
```

---

## Sleep Session Management

### Save Sleep Sessions

Store sleep session data in Worker's Short-Term Memory (STM).

**Endpoint**: `POST /api/sessions`

**Request Body**:
```json
{
  "user_id": "U_55bee4e9",
  "sleep_sessions": [
    {
      "session_date": "2025-11-22",
      "bedtime": "23:00:00",
      "waketime": "07:00:00",
      "duration_hours": 8.0,
      "efficiency_score": 85,
      "morning_mood": 7,
      "interruptions": [
        {
          "timestamp": "2025-11-22T02:30:00",
          "reason": "Bathroom break"
        }
      ]
    }
  ]
}
```

**Session Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_date` | string (YYYY-MM-DD) | Yes | Date of sleep session |
| `bedtime` | string (HH:MM:SS) | Yes | Time went to bed |
| `waketime` | string (HH:MM:SS) | Yes | Time woke up |
| `duration_hours` | float | Yes | Total sleep duration in hours |
| `efficiency_score` | integer (0-100) | No | Sleep efficiency percentage |
| `morning_mood` | integer (1-10) | No | Mood upon waking |
| `interruptions` | array | No | List of sleep interruptions |

**Interruption Object**:
```json
{
  "timestamp": "2025-11-22T02:30:00",
  "reason": "Bathroom break"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Saved 1 session(s)",
  "user_id": "U_55bee4e9"
}
```

---

## Analysis & Recommendations

### Analyze Sleep Data

Analyze sleep sessions and generate personalized recommendations.

**Endpoint**: `POST /api/analyze`

**Request Body**:
```json
{
  "user_id": "U_55bee4e9",
  "profile": {
    "age": 28,
    "work_schedule": "9am-5pm",
    "caffeine_intake": "medium",
    "screen_time": 2.5,
    "exercise": "3-4-times",
    "stress_level": 3
  },
  "sleep_sessions": [
    {
      "session_date": "2025-11-22",
      "bedtime": "23:00:00",
      "waketime": "07:00:00",
      "duration_hours": 8.0,
      "efficiency_score": 85,
      "morning_mood": 7,
      "interruptions": []
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "sleep_score": 85,
  "confidence": 0.89,
  "issues": [
    "Sleep schedule is inconsistent",
    "Frequent interruptions detected"
  ],
  "recommendations": {
    "ideal_sleep_window": {
      "recommended_bedtime": "22:30",
      "recommended_waketime": "06:30",
      "target_duration_hours": 8.0,
      "rationale": "Based on 9am-5pm schedule and 28 years old"
    },
    "caffeine_cutoff": {
      "current_intake": "medium",
      "cutoff_time": "14:00",
      "recommendation": "Limit caffeine intake and avoid after 14:00"
    },
    "light_exposure_management": [
      "Reduce screen time before bed (currently 2.5 hours)",
      "Get natural sunlight exposure in the morning"
    ],
    "bedroom_environment": [
      "Keep bedroom temperature between 65-68°F (18-20°C)",
      "Use white noise machine or earplugs"
    ],
    "wind_down_routine": [
      "Start wind-down routine 1 hour before bedtime",
      "Avoid stimulating activities close to bedtime"
    ],
    "weekly_sleep_plan": {
      "daily_bedtime": "22:30",
      "daily_waketime": "06:30",
      "week_goal": "Establish consistent sleep schedule",
      "weekly_tasks": [
        "Maintain current sleep habits and track improvements"
      ]
    }
  },
  "personalized_tips": [
    "Maintain a consistent sleep schedule, even on weekends",
    "Create a relaxing bedtime routine",
    "Avoid large meals and alcohol close to bedtime"
  ],
  "summary": "Average sleep duration: 8.0 hours. Average efficiency: 85%."
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "No sleep sessions provided",
  "code": "MISSING_DATA"
}
```

---

### Get Recommendations

Retrieve stored recommendations from Worker's LTM.

**Endpoint**: `GET /api/recommendations/{user_id}`

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User identifier |

**Request Example**:
```http
GET /api/recommendations/U_55bee4e9
```

**Response** (200 OK):
```json
{
  "sleep_score": 85,
  "confidence": 0.89,
  "issues": [...],
  "recommendations": {...},
  "personalized_tips": [...]
}
```

---

## Memory Management

### Get Memory

Retrieve all memory data (STM + LTM) for a user.

**Endpoint**: `GET /memory`

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User identifier |

**Request Example**:
```http
GET /memory?user_id=U_55bee4e9
```

**Response** (200 OK):
```json
{
  "stm": {
    "sessions": [
      {
        "session_date": "2025-11-22",
        "bedtime": "23:00:00",
        "waketime": "07:00:00",
        "duration_hours": 8.0,
        "efficiency_score": 85,
        "morning_mood": 7,
        "interruptions": []
      }
    ],
    "count": 1
  },
  "ltm": {
    "trends": {
      "avg_duration": 8.0,
      "avg_efficiency": 85.0,
      "avg_morning_mood": 7.0,
      "avg_sleep_score": 85,
      "confidence": 0.89
    },
    "patterns": [
      {
        "type": "consistent_bedtime",
        "description": "Maintains consistent bedtime",
        "confidence": 0.8
      }
    ],
    "preferences": {
      "profile": {
        "age": 28,
        "work_schedule": "9am-5pm",
        "caffeine_intake": "medium",
        "screen_time": 2.5,
        "exercise": "3-4-times",
        "stress_level": 3
      },
      "preferred_duration": 8.0,
      "preferred_bedtime": "23:00"
    },
    "recommendations": {...},
    "sleep_score": 85,
    "confidence": 0.89,
    "personalized_tips": [...]
  }
}
```

---

## System Endpoints

### Health Check

Check if Worker is running and healthy.

**Endpoint**: `GET /health`

**Request Example**:
```http
GET /health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "agent": "Sleep Optimizer Agent",
  "agent_id": "sleep-optimizer-agent-001",
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

---

### Register Worker

Register Worker with Supervisor (for multi-agent systems).

**Endpoint**: `POST /register`

**Request Body**:
```json
{
  "agent_id": "sleep-optimizer-agent-001",
  "agent_name": "Sleep Optimizer Agent",
  "capabilities": ["sleep_analysis", "recommendations"]
}
```

**Response** (200 OK):
```json
{
  "agent_id": "sleep-optimizer-agent-001",
  "agent_name": "Sleep Optimizer Agent",
  "capabilities": [
    "sleep_analysis",
    "sleep_scoring",
    "recommendation_generation",
    "memory_management",
    "trend_analysis",
    "personalized_planning"
  ],
  "endpoints": {
    "health": "/health",
    "task": "/task",
    "memory": "/memory",
    "logs": "/logs"
  },
  "features": {
    "memory_system": true,
    "llm_support": true,
    "mongodb_support": true,
    "stm_retention_days": 7,
    "ltm_retention_days": 365
  },
  "supported_data_formats": {
    "profile": [
      "age",
      "work_schedule",
      "caffeine_intake",
      "screen_time",
      "exercise",
      "stress_level"
    ],
    "sleep_sessions": [
      "bedtime",
      "waketime",
      "duration_hours",
      "efficiency_score",
      "interruptions",
      "morning_mood"
    ]
  },
  "version": "1.0.0"
}
```

---

### Get Logs

Retrieve recent Worker logs.

**Endpoint**: `GET /logs`

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `lines` | integer | No | 100 | Number of log lines to retrieve |

**Request Example**:
```http
GET /logs?lines=50
```

**Response** (200 OK):
```json
{
  "logs": [
    "{\"timestamp\": \"2025-11-23T10:00:00\", \"level\": \"INFO\", \"message\": \"Worker started\"}",
    "{\"timestamp\": \"2025-11-23T10:01:00\", \"level\": \"INFO\", \"message\": \"Processing task\"}"
  ],
  "count": 50
}
```

---

## Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "message": "Additional details"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request format |
| `INVALID_USER_ID` | 400 | Invalid or missing user_id |
| `MISSING_DATA` | 400 | Required data not provided |
| `SAVE_ERROR` | 500 | Failed to save data |
| `ANALYSIS_ERROR` | 500 | Analysis failed |
| `INTERNAL_ERROR` | 500 | Internal server error |

### Common Error Scenarios

#### Invalid User ID
```json
{
  "error": "Invalid user_id. Please login through supervisor agent.",
  "code": "INVALID_USER_ID"
}
```

#### Missing Data
```json
{
  "error": "No sleep sessions provided",
  "code": "MISSING_DATA"
}
```

#### Internal Error
```json
{
  "error": "Internal server error",
  "code": "INTERNAL_ERROR",
  "details": {
    "message": "Database connection failed"
  }
}
```

---

## Data Models

### Profile Model

```typescript
interface Profile {
  age: number;                    // 1-120
  work_schedule: string;          // "9am-5pm" | "flexible" | "night-shift" | "rotating"
  caffeine_intake: string;        // "none" | "low" | "medium" | "high"
  screen_time: number;            // 0-24 (hours)
  exercise: string;               // "daily" | "3-4-times" | "1-2-times" | "rarely"
  stress_level: number;           // 1-5
}
```

### Sleep Session Model

```typescript
interface SleepSession {
  session_date: string;           // YYYY-MM-DD
  bedtime: string;                // HH:MM:SS
  waketime: string;               // HH:MM:SS
  duration_hours: number;         // 0-24
  efficiency_score?: number;      // 0-100
  morning_mood?: number;          // 1-10
  interruptions?: Interruption[];
}

interface Interruption {
  timestamp: string;              // ISO 8601
  reason: string;
}
```

### Analysis Result Model

```typescript
interface AnalysisResult {
  sleep_score: number;            // 0-100
  confidence: number;             // 0.0-1.0
  issues: string[];
  recommendations: Recommendations;
  personalized_tips: string[];
  summary: string;
}

interface Recommendations {
  ideal_sleep_window: {
    recommended_bedtime: string;
    recommended_waketime: string;
    target_duration_hours: number;
    rationale: string;
  };
  caffeine_cutoff: {
    current_intake: string;
    cutoff_time: string;
    recommendation: string;
  };
  light_exposure_management: string[];
  bedroom_environment: string[];
  wind_down_routine: string[];
  weekly_sleep_plan: {
    daily_bedtime: string;
    daily_waketime: string;
    week_goal: string;
    weekly_tasks: string[];
  };
}
```

---

## Rate Limiting

Currently, there are no rate limits. For production use, consider implementing:
- **Per User**: 100 requests/minute
- **Per IP**: 1000 requests/hour
- **Analysis Endpoint**: 10 requests/minute (computationally expensive)

---

## Best Practices

### 1. Always Validate User ID
```javascript
if (!userId || userId === 'default_user' || userId.trim() === '') {
  throw new Error('Invalid user_id');
}
```

### 2. Save Profile Before Analysis
```javascript
// 1. Save profile
await fetch('/api/profile', {
  method: 'PUT',
  body: JSON.stringify({ user_id, profile })
});

// 2. Save sessions
await fetch('/api/sessions', {
  method: 'POST',
  body: JSON.stringify({ user_id, sleep_sessions })
});

// 3. Analyze
await fetch('/api/analyze', {
  method: 'POST',
  body: JSON.stringify({ user_id, profile, sleep_sessions })
});
```

### 3. Handle Errors Gracefully
```javascript
try {
  const response = await fetch('/api/analyze', {...});
  if (!response.ok) {
    const error = await response.json();
    console.error('Analysis failed:', error.code, error.error);
  }
} catch (error) {
  console.error('Network error:', error);
}
```

### 4. Use Appropriate Data Types
- Dates: `YYYY-MM-DD` format
- Times: `HH:MM:SS` format (24-hour)
- Durations: Float (hours)
- Scores: Integer (0-100)

---

## SDK Examples

### JavaScript/TypeScript

```javascript
class WorkerClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async saveProfile(userId, profile) {
    const response = await fetch(`${this.baseUrl}/api/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, profile })
    });
    return response.json();
  }

  async analyze(userId, profile, sleepSessions) {
    const response = await fetch(`${this.baseUrl}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, profile, sleep_sessions: sleepSessions })
    });
    return response.json();
  }
}

// Usage
const client = new WorkerClient();
await client.saveProfile('U_123', { age: 28, ... });
const analysis = await client.analyze('U_123', profile, sessions);
```

### Python

```python
import requests

class WorkerClient:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
    
    def save_profile(self, user_id, profile):
        response = requests.put(
            f'{self.base_url}/api/profile',
            json={'user_id': user_id, 'profile': profile}
        )
        return response.json()
    
    def analyze(self, user_id, profile, sleep_sessions):
        response = requests.post(
            f'{self.base_url}/api/analyze',
            json={
                'user_id': user_id,
                'profile': profile,
                'sleep_sessions': sleep_sessions
            }
        )
        return response.json()

# Usage
client = WorkerClient()
client.save_profile('U_123', {'age': 28, ...})
analysis = client.analyze('U_123', profile, sessions)
```

---

## Changelog

### Version 1.0.0 (2025-11-23)
- Initial release
- Profile management endpoints
- Sleep session storage
- Analysis and recommendations
- Memory management (STM/LTM)
- Health check and logging

---

## Support

For issues or questions:
- **GitHub**: [Repository URL]
- **Email**: support@example.com
- **Documentation**: [Docs URL]

---

## License

[Your License Here]
