from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, SprintViewSet, TaskViewSet, CommitLogViewSet, RiskAlertViewSet,
    register, login, profile, manager_dashboard, employee_dashboard,
    detect_project_risks, performance_score,
    list_employees, assign_task,
    meetings_list, meeting_detail, join_meeting, start_meeting, complete_meeting, generate_meeting_summary
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'sprints', SprintViewSet, basename='sprint')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'commits', CommitLogViewSet, basename='commit')
router.register(r'alerts', RiskAlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('profile/', profile, name='profile'),
    path('manager/dashboard/', manager_dashboard, name='manager-dashboard'),
    path('employee/dashboard/', employee_dashboard, name='employee-dashboard'),
    path('projects/<int:project_id>/detect-risks/', detect_project_risks, name='detect-risks'),
    path('performance-score/', performance_score, name='performance-score'),
    
    # Employee Management
    path('employees/', list_employees, name='list-employees'),
    
    # Task Assignment
    path('tasks/<int:task_id>/assign/', assign_task, name='assign-task'),
    
    # Scrum Meetings
    path('meetings/', meetings_list, name='meetings-list'),
    path('meetings/<int:meeting_id>/', meeting_detail, name='meeting-detail'),
    path('meetings/<int:meeting_id>/join/', join_meeting, name='join-meeting'),
    path('meetings/<int:meeting_id>/start/', start_meeting, name='start-meeting'),
    path('meetings/<int:meeting_id>/complete/', complete_meeting, name='complete-meeting'),
    path('meetings/<int:meeting_id>/generate-summary/', generate_meeting_summary, name='generate-summary'),
]

