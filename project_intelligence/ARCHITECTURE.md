# SYSTEM ARCHITECTURE OVERVIEW

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT APPLICATIONS                       │
│  (Web, Mobile, Postman, curl, Third-party integrations)        │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTPS/HTTP
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DJANGO REST FRAMEWORK                       │
│                        (API Gateway)                             │
├─────────────────────────────────────────────────────────────────┤
│  Authentication Layer (JWT via SimpleJWT)                       │
│  - Token Generation & Validation                                │
│  - Access/Refresh Token Management                              │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERMISSION LAYER                              │
│  - IsProjectManager (create/delete resources)                   │
│  - IsEmployee (view own tasks only)                             │
│  - IsOwnerOrProjectManager (update tasks)                       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                 │
                ▼                                 ▼
┌───────────────────────────┐    ┌───────────────────────────┐
│   VIEW LAYER (views.py)   │    │  INTELLIGENCE ENGINE      │
│                           │    │    (services.py)          │
├───────────────────────────┤    ├───────────────────────────┤
│ • ProjectViewSet          │◄───┤ • Delay Prediction        │
│ • SprintViewSet           │    │ • Risk Calculation        │
│ • TaskViewSet             │───►│ • Workload Detection      │
│ • CommitLogViewSet        │    │ • Blocker Detection       │
│ • RiskAlertViewSet        │    │ • Sprint Completion       │
│ • manager_dashboard()     │◄───┤ • Performance Scoring     │
│ • employee_dashboard()    │    │ • Sentiment Analysis      │
│ • performance_score()     │    │ • Dashboard Generation    │
└───────────────────────────┘    └───────────────────────────┘
                │                                 │
                └────────────────┬────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SERIALIZATION LAYER                             │
│                   (serializers.py)                               │
├─────────────────────────────────────────────────────────────────┤
│ • UserSerializer          • TaskSerializer                      │
│ • ProjectSerializer       • CommitLogSerializer                 │
│ • SprintSerializer        • RiskAlertSerializer                 │
│                                                                  │
│ Validates input, transforms data, handles representation        │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA MODEL LAYER                            │
│                        (models.py)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐         ┌──────────┐        ┌──────────┐        │
│  │   User   │         │ Project  │        │  Sprint  │        │
│  ├──────────┤         ├──────────┤        ├──────────┤        │
│  │ username │◄────────│ manager  │◄───────│ project  │        │
│  │ role     │         │ name     │        │ sprint_# │        │
│  │ email    │         │ dates    │        │ dates    │        │
│  └──────────┘         └──────────┘        └──────────┘        │
│       │                     │                    │              │
│       │                     │                    │              │
│       │              ┌──────▼──────┐            │              │
│       └──────────────┤    Task     ├────────────┘              │
│                      ├─────────────┤                            │
│                      │ title       │                            │
│                      │ status      │◄───┐                       │
│                      │ priority    │    │                       │
│                      │ est_hours   │    │                       │
│                      │ actual_hours│    │                       │
│                      └─────────────┘    │                       │
│                           │              │                       │
│                ┌──────────┴────────┐    │                       │
│                ▼                   ▼    │                       │
│         ┌──────────┐        ┌──────────┐                       │
│         │CommitLog │        │RiskAlert │                       │
│         ├──────────┤        ├──────────┤                       │
│         │ task     │        │ project  │                       │
│         │ message  │        │ message  │                       │
│         │ time     │        │ severity │                       │
│         └──────────┘        └──────────┘                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                            │
│                     SQLite (dev) / PostgreSQL (prod)            │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow Examples

### Example 1: Manager Views Dashboard

```
Client Request:
  GET /api/manager/dashboard/
  Headers: Authorization: Bearer <token>
         │
         ▼
  JWT Authentication:
    ✓ Token valid?
    ✓ User authenticated?
         │
         ▼
  Permission Check:
    ✓ IsProjectManager?
         │
         ▼
  View Layer:
    manager_dashboard(request)
         │
         ▼
  Intelligence Engine:
    generate_manager_dashboard(user)
      ├─► calculate_project_risk_score()
      ├─► calculate_sprint_completion_probability()
      ├─► detect_workload_issues()
      ├─► detect_blockers()
      └─► calculate_delay_prediction()
         │
         ▼
  Database Queries:
    ├─► Get all managed projects
    ├─► Get sprints for each project
    ├─► Get tasks, commits, alerts
    └─► Calculate metrics
         │
         ▼
  Response:
    JSON with complete dashboard data
```

### Example 2: Employee Updates Task Hours

```
Client Request:
  POST /api/tasks/5/update_hours/
  Body: {"actual_hours": 12}
  Headers: Authorization: Bearer <token>
         │
         ▼
  JWT Authentication & Permissions
         │
         ▼
  View Layer:
    TaskViewSet.update_hours()
         │
         ▼
  Database:
    Update task.actual_hours = 12
         │
         ▼
  Intelligence Engine:
    calculate_delay_prediction(task)
      ├─► Check actual vs estimated
      ├─► Check if blocked
      └─► Calculate delay score
         │
         ▼
  Response:
    {
      "task": {...},
      "delay_prediction": {
        "delay_score": 45,
        "predicted_delay_days": 1,
        "risk_level": "MEDIUM"
      }
    }
```

### Example 3: Auto Risk Detection

```
Trigger:
  POST /api/projects/1/detect-risks/
         │
         ▼
  Intelligence Engine:
    detect_blockers(project)
      │
      ├─► Find tasks blocked >3 days
      │     ├─► For each: Create RiskAlert
      │     └─► Severity: CRITICAL if >7 days
      │
      └─► Analyze commit messages
            ├─► Count bug keywords
            ├─► If count >10: Create RiskAlert
            └─► Severity: MEDIUM
         │
         ▼
  Database:
    Insert new RiskAlert records
         │
         ▼
  Response:
    {
      "project_id": 1,
      "new_alerts": [...]
    }
```

## Intelligence Engine Deep Dive

```
ProjectIntelligenceService
│
├─► calculate_delay_prediction(task)
│   ├─ If actual > estimated: +delay points
│   ├─ If blocked >3 days: +delay points
│   ├─ If no update >5 days: +delay points
│   └─ Return: {delay_score, predicted_days, risk_level}
│
├─► calculate_sprint_completion_probability(sprint)
│   ├─ completion_rate = done / total
│   ├─ expected_rate = time_passed / total_time
│   ├─ probability = actual / expected * 100
│   ├─ Penalty for blocked tasks
│   └─ Return: probability (0-100%)
│
├─► calculate_project_risk_score(project)
│   ├─ blocked_ratio * 30
│   ├─ overdue_ratio * 40
│   ├─ stale_ratio * 30
│   └─ Return: risk_score (0-100)
│
├─► detect_workload_issues(user?)
│   ├─ Count active tasks per employee
│   ├─ If >5: Flag as overloaded
│   ├─ Classify: MEDIUM/HIGH/CRITICAL
│   └─ Return: list of overloaded employees
│
├─► detect_blockers(project)
│   ├─ Find tasks blocked >3 days
│   ├─ Create RiskAlert for each
│   ├─ Analyze commit keywords
│   ├─ If "bug" mentioned >10 times: Alert
│   └─ Return: list of new alerts
│
├─► analyze_sentiment(text)
│   ├─ Count negative keywords
│   ├─ Count positive keywords
│   ├─ Calculate score: 50 + (pos*10) - (neg*10)
│   └─ Return: {score, sentiment, flags}
│
├─► calculate_performance_score(user)
│   ├─ Completion rate: 40%
│   ├─ On-time rate: 30%
│   ├─ Blocked penalty: -20%
│   ├─ Consistency bonus: 30%
│   └─ Return: score (0-100)
│
├─► generate_manager_dashboard(manager)
│   ├─ For each project:
│   │   ├─ Calculate health & risk
│   │   ├─ Get sprint probabilities
│   │   ├─ Get active alerts
│   │   └─ Get predicted delays
│   ├─ Calculate overall health
│   ├─ Detect overloaded employees
│   └─ Return: comprehensive dashboard
│
└─► generate_employee_dashboard(employee)
    ├─ Get assigned tasks
    ├─ Calculate performance score
    ├─ Determine workload status
    ├─ Get current sprints
    └─ Return: personal dashboard
```

## Data Flow Patterns

### Role-Based Data Filtering

```
User Role: EMPLOYEE
    │
    ├─► Projects: Only where assigned tasks exist
    ├─► Sprints: Only where assigned tasks exist
    ├─► Tasks: Only assigned to this user
    ├─► Commits: Only for own tasks
    └─► Alerts: Cannot view

User Role: PROJECT_MANAGER
    │
    ├─► Projects: Only managed projects
    ├─► Sprints: Only in managed projects
    ├─► Tasks: All in managed projects
    ├─► Commits: All in managed projects
    └─► Alerts: All in managed projects
```

### Automatic Calculations

```
When Task Updated:
    │
    ├─► Recalculate delay prediction
    └─► Update sprint completion probability

When Sprint Queries:
    │
    └─► Auto-calculate completion probability

When Dashboard Requested:
    │
    ├─► Recalculate all project health scores
    ├─► Recalculate sprint probabilities
    ├─► Detect current workload issues
    └─► Compile all active alerts
```

## Technology Stack

```
┌─────────────────────────────────────┐
│         Frontend (Future)           │
│  React, Vue, or Mobile App          │
└─────────────────────────────────────┘
                 │
                 │ REST API
                 ▼
┌─────────────────────────────────────┐
│      Django REST Framework          │
│  - ViewSets                         │
│  - Routers                          │
│  - Serializers                      │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│         Django Core                 │
│  - ORM                              │
│  - Migrations                       │
│  - Admin                            │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│      Authentication                 │
│  djangorestframework-simplejwt      │
│  - Access Tokens (24h)              │
│  - Refresh Tokens (7d)              │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│         Database                    │
│  SQLite (dev)                       │
│  PostgreSQL (production)            │
└─────────────────────────────────────┘
```

## Scalability Considerations

### Current Design
- Supports hundreds of concurrent users
- Thousands of tasks per project
- Efficient database queries
- Stateless API (horizontally scalable)

### Future Enhancements
- Caching layer (Redis)
- Celery for async tasks
- WebSocket for real-time updates
- Load balancing
- Database read replicas
- ML model serving

## Security Layers

```
1. Transport Security (HTTPS)
2. Authentication (JWT tokens)
3. Authorization (Role-based permissions)
4. Input Validation (DRF serializers)
5. SQL Injection Prevention (Django ORM)
6. CSRF Protection (Django middleware)
7. Password Hashing (Django built-in)
```

## Testing Strategy

```
Unit Tests (main/tests.py)
├─► Model Tests
│   └─ Validation, relationships, methods
├─► Service Tests
│   └─ All AI logic functions
├─► API Tests
│   ├─ Authentication
│   ├─ Permissions
│   └─ CRUD operations
└─► Integration Tests
    └─ Complete user workflows
```

This architecture provides:
✓ Separation of concerns
✓ Scalability
✓ Maintainability
✓ Security
✓ Testability
✓ Extensibility
