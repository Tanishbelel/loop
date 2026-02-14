# API Quick Reference Guide

## Authentication Flow

1. Register or Login to get JWT tokens
2. Include token in all requests: `Authorization: Bearer <access_token>`
3. Access token expires in 24 hours
4. Refresh token expires in 7 days

## Base URL
```
http://localhost:8000/api/
```

## Quick Start Examples

### 1. Login as Project Manager
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "pm_john",
    "password": "password123"
  }'
```

### 2. Get Manager Dashboard
```bash
curl http://localhost:8000/api/manager/dashboard/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Login as Employee
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "password123"
  }'
```

### 4. Get Employee Dashboard
```bash
curl http://localhost:8000/api/employee/dashboard/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Create New Task (Manager Only)
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement new feature",
    "description": "Add user authentication",
    "project": 1,
    "sprint": 1,
    "assigned_to": 2,
    "status": "TODO",
    "priority": "HIGH",
    "estimated_hours": 16
  }'
```

### 6. Update Task Hours
```bash
curl -X POST http://localhost:8000/api/tasks/1/update_hours/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "actual_hours": 12
  }'
```

### 7. Detect Project Risks
```bash
curl -X POST http://localhost:8000/api/projects/1/detect-risks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 8. Get Performance Score
```bash
curl http://localhost:8000/api/performance-score/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Status Codes

- 200: Success
- 201: Created
- 400: Bad Request (validation error)
- 401: Unauthorized (invalid/missing token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found

## Task Status Values

- TODO
- IN_PROGRESS
- BLOCKED
- DONE

## Priority Values

- LOW
- MEDIUM
- HIGH
- CRITICAL

## Severity Values (Risk Alerts)

- LOW
- MEDIUM
- HIGH
- CRITICAL

## Workload Status Values

- NORMAL
- ELEVATED
- HIGH
- CRITICAL
