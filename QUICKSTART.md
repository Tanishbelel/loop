# QUICK START GUIDE

## Getting Started in 5 Minutes

### Step 1: Navigate to Project
```bash
cd project_intelligence
```

### Step 2: Run Setup Script
```bash
bash setup.sh
```

This will:
- Install all dependencies
- Create database
- Load sample data (1 manager, 3 employees, 10 tasks)

### Step 3: Start Server
```bash
python manage.py runserver
```

Server runs at: http://localhost:8000

### Step 4: Test the API

**Login as Manager:**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "pm_john", "password": "password123"}'
```

Copy the "access" token from response.

**Get Manager Dashboard:**
```bash
curl http://localhost:8000/api/manager/dashboard/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Login as Employee:**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'
```

**Get Employee Dashboard:**
```bash
curl http://localhost:8000/api/employee/dashboard/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Sample Credentials

**Project Manager:**
- Username: `pm_john`
- Password: `password123`
- Can create projects, sprints, tasks
- Access full analytics dashboard

**Employees:**
- Username: `alice` / Password: `password123`
- Username: `bob` / Password: `password123`
- Username: `carol` / Password: `password123`
- View assigned tasks only
- Personal performance dashboard

## Run Demo
```bash
python demo.py
```

This shows:
- Project risk analysis
- Sprint completion predictions
- Delay predictions for tasks
- Workload analysis
- Blocker detection
- Performance scores
- Dashboard previews

## Run Tests
```bash
python manage.py test main
```

Tests cover:
- Authentication
- Role-based access
- Task management
- AI predictions
- Dashboards

## Access Admin Interface

1. Create superuser:
```bash
python manage.py createsuperuser
```

2. Visit: http://localhost:8000/admin/

## Key Endpoints

- POST /api/register/ - Register new user
- POST /api/login/ - Get JWT token
- GET /api/profile/ - View profile
- GET /api/projects/ - List projects
- GET /api/tasks/ - List tasks (filtered by role)
- GET /api/manager/dashboard/ - Manager analytics
- GET /api/employee/dashboard/ - Employee dashboard
- GET /api/performance-score/ - Performance score

## What Makes This Special

✓ **No Manual Updates** - System analyzes activity automatically
✓ **Predicts Delays** - Before they impact deadlines
✓ **Detects Blockers** - Automatically flags stale/blocked tasks
✓ **Fair Evaluation** - Data-driven performance scoring
✓ **Role-Based Access** - Employees see only their tasks
✓ **Real-Time Intelligence** - Continuous analysis
✓ **Production Ready** - Comprehensive tests, security, validation

## Next Steps

1. Explore API endpoints in API_GUIDE.md
2. Read full documentation in README.md
3. Review system architecture in PROJECT_SUMMARY.md
4. Customize for your needs
5. Deploy to production

## Need Help?

- Full API documentation: API_GUIDE.md
- Complete guide: README.md
- System overview: PROJECT_SUMMARY.md
- All code has clear structure and follows Django best practices
