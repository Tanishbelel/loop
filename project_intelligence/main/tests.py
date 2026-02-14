from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from .models import Project, Sprint, Task, RiskAlert, CommitLog
from .services import ProjectIntelligenceService

User = get_user_model()

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_user_registration(self):
        data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com',
            'role': 'EMPLOYEE'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_login(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='EMPLOYEE'
        )
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_invalid_login(self):
        data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class RoleBasedAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.manager = User.objects.create_user(
            username='manager',
            password='pass123',
            role='PROJECT_MANAGER'
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            password='pass123',
            role='EMPLOYEE'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            manager=self.manager
        )
    
    def test_employee_cannot_create_project(self):
        self.client.force_authenticate(user=self.employee)
        
        data = {
            'name': 'New Project',
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=30))
        }
        response = self.client.post('/api/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_manager_can_create_project(self):
        self.client.force_authenticate(user=self.manager)
        
        data = {
            'name': 'New Project',
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=30))
        }
        response = self.client.post('/api/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_employee_can_view_assigned_tasks(self):
        task = Task.objects.create(
            title='Test Task',
            project=self.project,
            assigned_to=self.employee,
            status='TODO',
            estimated_hours=8
        )
        
        self.client.force_authenticate(user=self.employee)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_manager_dashboard_access(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/manager/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('projects', response.data)
    
    def test_employee_cannot_access_manager_dashboard(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.get('/api/manager/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TaskCreationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.manager = User.objects.create_user(
            username='manager',
            password='pass123',
            role='PROJECT_MANAGER'
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            password='pass123',
            role='EMPLOYEE'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            manager=self.manager
        )
        
        self.sprint = Sprint.objects.create(
            project=self.project,
            sprint_number=1,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14)
        )
    
    def test_create_task(self):
        self.client.force_authenticate(user=self.manager)
        
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'project': self.project.id,
            'sprint': self.sprint.id,
            'assigned_to': self.employee.id,
            'status': 'TODO',
            'priority': 'HIGH',
            'estimated_hours': 16
        }
        
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
    
    def test_task_validation(self):
        self.client.force_authenticate(user=self.manager)
        
        data = {
            'title': 'Invalid Task',
            'project': self.project.id,
            'estimated_hours': -5
        }
        
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class WorkloadDetectionTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager',
            password='pass123',
            role='PROJECT_MANAGER'
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            password='pass123',
            role='EMPLOYEE'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            manager=self.manager
        )
    
    def test_overload_detection(self):
        for i in range(7):
            Task.objects.create(
                title=f'Task {i}',
                project=self.project,
                assigned_to=self.employee,
                status='IN_PROGRESS',
                estimated_hours=8
            )
        
        overloaded = ProjectIntelligenceService.detect_workload_issues(self.employee)
        self.assertEqual(len(overloaded), 1)
        self.assertEqual(overloaded[0]['active_tasks'], 7)
        self.assertIn(overloaded[0]['overload_level'], ['HIGH', 'MEDIUM'])
    
    def test_normal_workload(self):
        for i in range(3):
            Task.objects.create(
                title=f'Task {i}',
                project=self.project,
                assigned_to=self.employee,
                status='TODO',
                estimated_hours=8
            )
        
        overloaded = ProjectIntelligenceService.detect_workload_issues(self.employee)
        self.assertEqual(len(overloaded), 0)

class DelayPredictionTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager',
            password='pass123',
            role='PROJECT_MANAGER'
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            password='pass123',
            role='EMPLOYEE'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            manager=self.manager
        )
    
    def test_delay_prediction_overage(self):
        task = Task.objects.create(
            title='Delayed Task',
            project=self.project,
            assigned_to=self.employee,
            status='IN_PROGRESS',
            estimated_hours=8,
            actual_hours=16
        )
        
        prediction = ProjectIntelligenceService.calculate_delay_prediction(task)
        self.assertGreater(prediction['delay_score'], 0)
        self.assertGreater(prediction['predicted_delay_days'], 0)
    
    def test_delay_prediction_blocked(self):
        task = Task.objects.create(
            title='Blocked Task',
            project=self.project,
            assigned_to=self.employee,
            status='BLOCKED',
            estimated_hours=8
        )
        
        task.last_updated = date.today() - timedelta(days=5)
        task.save()
        
        prediction = ProjectIntelligenceService.calculate_delay_prediction(task)
        self.assertGreater(prediction['delay_score'], 0)
        self.assertEqual(prediction['risk_level'], 'HIGH')

class SprintCompletionTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager',
            password='pass123',
            role='PROJECT_MANAGER'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            manager=self.manager
        )
        
        self.sprint = Sprint.objects.create(
            project=self.project,
            sprint_number=1,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today() + timedelta(days=7)
        )
    
    def test_sprint_completion_probability(self):
        for i in range(5):
            Task.objects.create(
                title=f'Task {i}',
                project=self.project,
                sprint=self.sprint,
                status='DONE',
                estimated_hours=8
            )
        
        for i in range(5):
            Task.objects.create(
                title=f'Task In Progress {i}',
                project=self.project,
                sprint=self.sprint,
                status='IN_PROGRESS',
                estimated_hours=8
            )
        
        probability = ProjectIntelligenceService.calculate_sprint_completion_probability(self.sprint)
        self.assertGreater(probability, 0)
        self.assertLessEqual(probability, 100)

class PerformanceScoringTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager',
            password='pass123',
            role='PROJECT_MANAGER'
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            password='pass123',
            role='EMPLOYEE'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            manager=self.manager
        )
    
    def test_performance_score_calculation(self):
        for i in range(5):
            Task.objects.create(
                title=f'Completed Task {i}',
                project=self.project,
                assigned_to=self.employee,
                status='DONE',
                estimated_hours=8,
                actual_hours=7
            )
        
        for i in range(2):
            Task.objects.create(
                title=f'In Progress Task {i}',
                project=self.project,
                assigned_to=self.employee,
                status='IN_PROGRESS',
                estimated_hours=8,
                actual_hours=4
            )
        
        score = ProjectIntelligenceService.calculate_performance_score(self.employee)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_performance_score_with_blocks(self):
        for i in range(3):
            Task.objects.create(
                title=f'Blocked Task {i}',
                project=self.project,
                assigned_to=self.employee,
                status='BLOCKED',
                estimated_hours=8
            )
        
        score = ProjectIntelligenceService.calculate_performance_score(self.employee)
        self.assertGreater(score, 0)

class BlockerDetectionTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager',
            password='pass123',
            role='PROJECT_MANAGER'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            manager=self.manager
        )
    
    def test_blocker_detection(self):
        task = Task.objects.create(
            title='Blocked Task',
            project=self.project,
            status='BLOCKED',
            estimated_hours=8
        )
        
        task.last_updated = date.today() - timedelta(days=5)
        task.save()
        
        alerts = ProjectIntelligenceService.detect_blockers(self.project)
        self.assertGreater(len(alerts), 0)
    
    def test_bug_keyword_detection(self):
        task = Task.objects.create(
            title='Test Task',
            project=self.project,
            status='IN_PROGRESS',
            estimated_hours=8
        )
        
        for i in range(12):
            CommitLog.objects.create(
                task=task,
                commit_message=f'Fixed bug #{i}'
            )
        
        alerts = ProjectIntelligenceService.detect_blockers(self.project)
        self.assertGreater(len(alerts), 0)

class DashboardTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.manager = User.objects.create_user(
            username='manager',
            password='pass123',
            role='PROJECT_MANAGER'
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            password='pass123',
            role='EMPLOYEE'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            manager=self.manager
        )
        
        self.sprint = Sprint.objects.create(
            project=self.project,
            sprint_number=1,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14)
        )
    
    def test_manager_dashboard_structure(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/manager/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('projects', response.data)
        self.assertIn('overall_health', response.data)
        self.assertIn('overloaded_employees', response.data)
    
    def test_employee_dashboard_structure(self):
        Task.objects.create(
            title='Employee Task',
            project=self.project,
            sprint=self.sprint,
            assigned_to=self.employee,
            status='IN_PROGRESS',
            estimated_hours=8
        )
        
        self.client.force_authenticate(user=self.employee)
        response = self.client.get('/api/employee/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('performance_score', response.data)
        self.assertIn('workload_status', response.data)
        self.assertIn('assigned_tasks', response.data)
