# PROJECT INTELLIGENCE SYSTEM
## Virtual Scrum Master - Complete Django Implementation

**Transform engineering activity into predictive project intelligence**

---

## 🚀 Quick Start

1. **Get Started Immediately**
   - Read: `QUICKSTART.md`
   - Run: `bash setup.sh`
   - Start: `python manage.py runserver`

2. **Sample Login**
   - Manager: `pm_john` / `password123`
   - Employee: `alice` / `password123`

---

## 📚 Documentation Index

### For New Users
1. **QUICKSTART.md** - 5-minute setup guide
2. **README.md** - Complete user manual
3. **API_GUIDE.md** - API reference with examples

### For Developers
4. **ARCHITECTURE.md** - System design & data flow
5. **PROJECT_SUMMARY.md** - Technical implementation details

### Getting Help
- All endpoints documented in API_GUIDE.md
- All features explained in README.md
- Code structure in ARCHITECTURE.md

---

## 🎯 What This System Does

### Replaces Manual Processes
❌ Daily standup meetings
❌ Manual status reports
❌ Late blocker discovery
❌ Subjective performance reviews

### Provides Automated Intelligence
✅ **Delay Prediction** - Before impact
✅ **Blocker Detection** - Automatic alerts
✅ **Workload Analysis** - Fair distribution
✅ **Sprint Forecasting** - Real-time probability
✅ **Performance Scoring** - Data-driven (0-100)
✅ **Risk Alerts** - Proactive notifications

---

## 🏗️ System Components

### Core Features
- **6 Data Models** (User, Project, Sprint, Task, CommitLog, RiskAlert)
- **JWT Authentication** (Role-based: Employee/Manager)
- **REST API** (15+ endpoints)
- **AI Intelligence Engine** (8 core algorithms)
- **Role-Based Dashboards** (Manager & Employee views)
- **Comprehensive Tests** (Full coverage)

### Technology Stack
- **Backend**: Django 5.0 + Django REST Framework
- **Authentication**: Simple JWT (24h access, 7d refresh)
- **Database**: SQLite (dev) / PostgreSQL ready
- **API Design**: RESTful with ViewSets
- **Testing**: Django TestCase + APIClient

---

## 📁 File Structure

```
project_intelligence/
│
├── QUICKSTART.md          ← START HERE
├── README.md              ← Full documentation
├── API_GUIDE.md           ← API reference
├── ARCHITECTURE.md        ← System design
├── PROJECT_SUMMARY.md     ← Technical details
│
├── setup.sh               ← Automated setup
├── demo.py                ← Live demonstration
├── requirements.txt       ← Dependencies
├── manage.py              ← Django CLI
│
├── project_intelligence/  ← Django config
│   ├── settings.py        (JWT, DRF, custom user)
│   ├── urls.py            (Root routing)
│   └── wsgi.py
│
└── main/                  ← All features here
    ├── models.py          (6 models)
    ├── serializers.py     (DRF serializers)
    ├── views.py           (API endpoints)
    ├── services.py        ← ALL AI LOGIC
    ├── permissions.py     (Role-based access)
    ├── urls.py            (API routing)
    ├── admin.py           (Django admin)
    ├── tests.py           (Comprehensive tests)
    └── management/
        └── commands/
            └── load_sample_data.py
```

---

## 🎮 How to Use

### Setup (One Time)
```bash
bash setup.sh
```

### Run Server
```bash
python manage.py runserver
```

### Run Demo
```bash
python demo.py
```

### Run Tests
```bash
python manage.py test main
```

### Access Points
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

---

## 🔑 Key API Endpoints

### Authentication
```
POST /api/register/    - Create account
POST /api/login/       - Get JWT tokens
GET  /api/profile/     - View/update profile
```

### Resources
```
GET/POST /api/projects/         - Projects
GET/POST /api/sprints/          - Sprints
GET/POST /api/tasks/            - Tasks
GET/POST /api/commits/          - Commit logs
GET      /api/alerts/           - Risk alerts
```

### Intelligence
```
GET  /api/manager/dashboard/        - Full analytics
GET  /api/employee/dashboard/       - Personal view
POST /api/tasks/{id}/update_hours/  - With prediction
POST /api/projects/{id}/detect-risks/ - Scan risks
GET  /api/performance-score/        - Your score
```

---

## 🧠 AI Capabilities

### Predictive Analytics
1. **Delay Prediction**
   - Analyzes actual vs estimated hours
   - Detects blocked tasks (>3 days)
   - Flags stale tasks (>5 days no update)
   - Returns delay score & predicted days

2. **Sprint Completion**
   - Real-time probability calculation
   - Factors in progress vs time
   - Accounts for blockers
   - Returns 0-100% likelihood

3. **Project Health**
   - Blocked task ratio (30%)
   - Overdue task ratio (40%)
   - Stale task ratio (30%)
   - Returns risk score 0-100

### Detection Systems
4. **Workload Detection**
   - Counts active tasks per employee
   - Flags overload at >5 tasks
   - Levels: NORMAL/ELEVATED/HIGH/CRITICAL

5. **Blocker Detection**
   - Auto-alerts for tasks blocked >3 days
   - Analyzes commit keywords
   - Creates severity-rated alerts

6. **Sentiment Analysis**
   - Keyword-based (stuck, urgent, etc.)
   - Returns score & classification

### Evaluation
7. **Performance Scoring**
   - Completion rate (40%)
   - On-time delivery (30%)
   - Blocked penalty
   - Consistency bonus (30%)
   - Returns fair 0-100 score

---

## 🔒 Security Features

✓ JWT authentication (24h access tokens)
✓ Role-based permissions (Employee/Manager)
✓ Input validation (DRF serializers)
✓ CSRF protection
✓ SQL injection prevention
✓ Secure password hashing
✓ Authorization on all endpoints

---

## 🧪 Testing

**Comprehensive Test Suite:**
- Authentication tests
- Role-based access tests
- CRUD operation tests
- AI logic tests (delay, risk, workload)
- Dashboard generation tests
- End-to-end workflow tests

**Run All Tests:**
```bash
python manage.py test main
```

---

## 🎯 Sample Data Included

**1 Project Manager:**
- pm_john (manages AI Dashboard Platform)

**3 Employees:**
- alice (7 tasks, some overloaded)
- bob (5 tasks)
- carol (3 tasks)

**10 Realistic Tasks:**
- Mix of DONE, IN_PROGRESS, BLOCKED, TODO
- Various priorities (LOW → CRITICAL)
- Some delayed, some on-time
- Commit logs attached

**Auto-Generated Alerts:**
- Overload warnings
- Blocker notifications
- Risk alerts

---

## 📊 What Each User Sees

### Project Manager Dashboard
- Project health scores
- Sprint completion probabilities
- Overloaded employees
- Active risk alerts
- Predicted delays (top 5)
- Overall system health

### Employee Dashboard
- Assigned tasks only
- Personal performance score
- Workload status
- Current sprint info
- Task breakdown by status

---

## 🚀 Production Deployment

**Ready for production with:**
1. Change SECRET_KEY
2. Set DEBUG = False
3. Configure PostgreSQL
4. Set ALLOWED_HOSTS
5. Configure static files
6. Add environment variables
7. Set up HTTPS
8. Add monitoring
9. Configure backups
10. Add rate limiting

---

## 🔮 Future Enhancements

**Code includes TODO placeholders for:**
- GitHub API integration
- Slack notifications
- ML time-series forecasting
- Graph-based dependencies
- Advanced NLP sentiment
- WebSockets (real-time updates)
- Automated task assignment
- Predictive resource allocation

---

## 💡 Why This System

### Problem Solved
Manual project management creates:
- Delayed blocker detection
- Late discovery of risks
- Biased performance reviews
- No workload intelligence
- Reactive instead of proactive

### Solution Provided
Automated intelligence that:
- Predicts delays before impact
- Detects blockers immediately
- Provides fair evaluation
- Monitors workload continuously
- Enables proactive decisions

---

## 📖 Document Guide

| Document | Purpose | Read If You... |
|----------|---------|----------------|
| QUICKSTART.md | Get running in 5 minutes | Want to start immediately |
| README.md | Complete user manual | Need full documentation |
| API_GUIDE.md | API reference | Are integrating with API |
| ARCHITECTURE.md | System design | Want to understand internals |
| PROJECT_SUMMARY.md | Implementation details | Are a developer |

---

## ✅ Compliance Checklist

✅ Custom User model with role field
✅ JWT authentication via SimpleJWT
✅ Role-based access (Employee/Manager)
✅ All 6 required models
✅ AI logic in services.py (centralized)
✅ Delay prediction algorithm
✅ Sprint completion probability
✅ Workload detection (>5 tasks)
✅ Blocker detection (>3 days + keywords)
✅ Sentiment analysis (keyword-based)
✅ Performance scoring (0-100)
✅ Manager dashboard
✅ Employee dashboard
✅ REST API with ViewSets
✅ Comprehensive tests
✅ Sample data (1 PM, 3 employees, 10 tasks)
✅ Security & validation
✅ Clean, modular code
✅ Future enhancement placeholders
✅ Everything in 'main' app

---

## 🎓 Learning Path

**Beginner:**
1. Read QUICKSTART.md
2. Run setup.sh
3. Test with curl commands
4. Run demo.py

**Intermediate:**
1. Read README.md
2. Explore API endpoints
3. Review test cases
4. Modify sample data

**Advanced:**
1. Read ARCHITECTURE.md
2. Study services.py (AI logic)
3. Review models & relationships
4. Extend with custom features

---

## 🆘 Common Tasks

**Add a new employee:**
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"pass123","role":"EMPLOYEE"}'
```

**Create a project:**
```bash
# Login as manager first, then:
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"New Project","start_date":"2026-03-01","end_date":"2026-06-01"}'
```

**Assign a task:**
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Task","project":1,"assigned_to":2,"status":"TODO","estimated_hours":8}'
```

---

## 📞 Support

- Full API docs: API_GUIDE.md
- Usage guide: README.md  
- Architecture: ARCHITECTURE.md
- Code is self-documenting with clear structure

---

**Built with Django 5.0, DRF, and SimpleJWT**
**Production-ready with comprehensive testing**
**Designed for future ML/AI enhancement**

**Start now: `bash setup.sh`**
