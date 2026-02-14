# Project Intelligence System - Virtual Scrum Master

A Django-based AI-powered project management system that transforms engineering activity into predictive project intelligence.

## Core Features

- **Predictive Delay Insights**: Analyzes task progress and predicts delays before impact
- **Blocker Detection**: Automatically identifies and alerts on project blockers
- **Workload Analysis**: Detects employee overload and distributes work fairly
- **Sprint Completion Probability**: Real-time calculation of sprint success likelihood
- **Project Health Score**: Comprehensive risk scoring for projects
- **Performance Scoring**: Fair, data-driven employee evaluation
- **Role-Based Dashboards**: Customized views for managers and employees

## System Architecture

```
project_intelligence/
├── manage.py
├── requirements.txt
├── project_intelligence/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── main/
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── services.py
    ├── permissions.py
    ├── urls.py
    ├── tests.py
    └── admin.py
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt --break-system-packages
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Load sample data:
```bash
python manage.py load_sample_data
```

4. Create superuser (optional):
```bash
python manage.py createsuperuser
```

5. Run server:
```bash
python manage.py runserver
```

## Sample Users

**Project Manager:**
- Username: `pm_john`
- Password: `password123`

**Employees:**
- Username: `alice` / Password: `password123`
- Username: `bob` / Password: `password123`
- Username: `carol` / Password: `password123`

## API Endpoints

### Authentication

**Register User**
```
POST /api/register/
{
    "username": "newuser",
    "password": "password123",
    "email": "user@example.com",
    "role": "EMPLOYEE"
}
```

**Login**
```
POST /api/login/
{
    "username": "pm_john",
    "password": "password123"
}
Response: { "access": "...", "refresh": "...", "user": {...} }
```

**Get Profile**
```
GET /api/profile/
Headers: Authorization: Bearer <access_token>
```

### Projects

**List Projects**
```
GET /api/projects/
```

**Create Project** (Project Manager only)
```
POST /api/projects/
{
    "name": "New Project",
    "description": "Project description",
    "start_date": "2026-01-01",
    "end_date": "2026-03-01"
}
```

**Get Project Details**
```
GET /api/projects/{id}/
```

**Detect Project Risks** (Project Manager only)
```
POST /api/projects/{id}/detect-risks/
```

### Sprints

**List Sprints**
```
GET /api/sprints/
```

**Create Sprint** (Project Manager only)
```
POST /api/sprints/
{
    "project": 1,
    "sprint_number": 1,
    "start_date": "2026-01-01",
    "end_date": "2026-01-14"
}
```

### Tasks

**List Tasks**
```
GET /api/tasks/
```

**Create Task** (Project Manager only)
```
POST /api/tasks/
{
    "title": "New Task",
    "description": "Task description",
    "project": 1,
    "sprint": 1,
    "assigned_to": 2,
    "status": "TODO",
    "priority": "HIGH",
    "estimated_hours": 16
}
```

**Update Task Hours**
```
POST /api/tasks/{id}/update_hours/
{
    "actual_hours": 10
}
Response includes delay prediction
```

### Dashboards

**Manager Dashboard** (Project Manager only)
```
GET /api/manager/dashboard/

Response:
{
    "projects": [
        {
            "id": 1,
            "name": "AI Dashboard Platform",
            "health_score": 75.5,
            "risk_score": 24.5,
            "sprints": [...],
            "active_alerts": [...],
            "predicted_delays": [...]
        }
    ],
    "overall_health": 75.5,
    "total_risk_alerts": 2,
    "overloaded_employees": [...]
}
```

**Employee Dashboard** (Employee only)
```
GET /api/employee/dashboard/

Response:
{
    "performance_score": 68.5,
    "workload_status": "ELEVATED",
    "active_tasks_count": 5,
    "completed_tasks_count": 3,
    "task_breakdown": {...},
    "current_sprints": [...],
    "assigned_tasks": [...]
}
```

**Performance Score**
```
GET /api/performance-score/
```

### Risk Alerts

**List Alerts** (Project Manager only)
```
GET /api/alerts/
```

**Resolve Alert** (Project Manager only)
```
POST /api/alerts/{id}/resolve/
```

### Commit Logs

**List Commits**
```
GET /api/commits/
```

**Create Commit**
```
POST /api/commits/
{
    "task": 1,
    "commit_message": "Fixed bug in authentication",
    "commit_time": "2026-02-14T10:30:00Z"
}
```

## AI Intelligence Services

All AI logic is centralized in `main/services.py`:

### ProjectIntelligenceService

**calculate_delay_prediction(task)**
- Analyzes actual vs estimated hours
- Detects blocked task duration
- Flags stale tasks (no update >5 days)
- Returns delay score and predicted delay days

**calculate_sprint_completion_probability(sprint)**
- Calculates completion rate vs expected progress
- Factors in blocked tasks
- Accounts for average task delays
- Returns probability (0-100%)

**calculate_project_risk_score(project)**
- Evaluates blocked task ratio
- Analyzes overdue tasks
- Detects stale tasks
- Returns risk score (0-100)

**detect_workload_issues(user)**
- Counts active tasks per employee
- Flags overload if >5 active tasks
- Returns overload level (MEDIUM/HIGH/CRITICAL)

**detect_blockers(project)**
- Identifies tasks blocked >3 days
- Detects repeated bug keywords (>10 occurrences)
- Creates RiskAlerts automatically
- Returns new alerts

**analyze_sentiment(text)**
- Keyword-based sentiment analysis
- Negative: stuck, urgent, delay, frustrated, issue
- Positive: completed, done, success, finished
- Returns sentiment score and classification

**calculate_performance_score(user)**
- On-time completion rate (30%)
- Overall completion rate (40%)
- Blocked task penalty
- Task consistency bonus (30%)
- Returns score (0-100)

**generate_manager_dashboard(manager)**
- Aggregates all project data
- Calculates health scores
- Detects workload issues
- Compiles risk alerts
- Returns comprehensive dashboard

**generate_employee_dashboard(employee)**
- Lists assigned tasks
- Calculates performance score
- Determines workload status
- Shows current sprint info
- Returns personalized dashboard

## Role-Based Access Control

### PROJECT_MANAGER
- Create/update/delete projects
- Create/update/delete sprints
- Create/assign/delete tasks
- View all project data
- Access manager dashboard
- View all alerts and predictions

### EMPLOYEE
- View assigned tasks only
- Update task hours
- View own performance score
- Access employee dashboard
- View own commits

## Security Features

- JWT-based authentication
- Role-based permissions
- Input validation on all endpoints
- Secure password hashing
- CSRF protection
- SQL injection prevention (Django ORM)

## Running Tests

```bash
python manage.py test main
```

Test coverage includes:
- Authentication (registration, login)
- Role-based access control
- Task creation and validation
- Workload detection
- Delay prediction
- Sprint completion probability
- Performance scoring
- Blocker detection
- Dashboard generation

## Future Enhancements (Placeholders)

The system is designed for future ML/AI integration:

- **GitHub API Integration**: Automatic commit tracking
- **Slack Integration**: Real-time notifications
- **ML Time-Series Forecasting**: Advanced delay prediction
- **Graph-Based Dependency Engine**: Task relationship analysis
- **NLP Sentiment Analysis**: Advanced emotion detection
- **WebSockets (Django Channels)**: Real-time updates
- **Automated Task Assignment**: AI-powered work distribution
- **Predictive Resource Allocation**: Optimize team capacity

## Admin Interface

Access Django admin at `/admin/`

Create superuser:
```bash
python manage.py createsuperuser
```

## Database Schema

**User**
- Custom user model extending AbstractUser
- Role field (EMPLOYEE/PROJECT_MANAGER)

**Project**
- Name, description, dates
- Manager (FK to User)

**Sprint**
- Project reference
- Sprint number
- Dates, completion probability

**Task**
- Project and Sprint references
- Assigned user
- Status (TODO/IN_PROGRESS/BLOCKED/DONE)
- Priority, hours tracking

**CommitLog**
- Task reference
- Commit message and timestamp

**RiskAlert**
- Project reference
- Message, severity
- Resolution status

## Performance Considerations

- Database indexes on foreign keys
- Efficient queries using select_related/prefetch_related
- Pagination support on list endpoints
- Caching potential for dashboard data (future enhancement)

## License

Proprietary - Internal Use Only
