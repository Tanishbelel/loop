from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from main.models import Project, Sprint, Task, CommitLog, RiskAlert

User = get_user_model()

class Command(BaseCommand):
    help = 'Load sample data for testing'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        manager = User.objects.create_user(
            username='pm_john',
            email='john@example.com',
            password='password123',
            role='PROJECT_MANAGER',
            first_name='John',
            last_name='Manager'
        )
        self.stdout.write(f'Created Project Manager: {manager.username}')
        
        employees = []
        employee_names = [
            ('alice', 'Alice', 'Developer'),
            ('bob', 'Bob', 'Engineer'),
            ('carol', 'Carol', 'Designer')
        ]
        
        for username, first_name, last_name in employee_names:
            emp = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='password123',
                role='EMPLOYEE',
                first_name=first_name,
                last_name=last_name
            )
            employees.append(emp)
            self.stdout.write(f'Created Employee: {emp.username}')
        
        project = Project.objects.create(
            name='AI Dashboard Platform',
            description='Building an intelligent project management dashboard with predictive analytics',
            start_date=date.today() - timedelta(days=14),
            end_date=date.today() + timedelta(days=60),
            manager=manager
        )
        self.stdout.write(f'Created Project: {project.name}')
        
        sprint = Sprint.objects.create(
            project=project,
            sprint_number=1,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today() + timedelta(days=7)
        )
        self.stdout.write(f'Created Sprint: {sprint}')
        
        tasks_data = [
            {
                'title': 'Setup Django Backend',
                'description': 'Initialize Django project with REST framework',
                'assigned_to': employees[0],
                'status': 'DONE',
                'priority': 'HIGH',
                'estimated_hours': 8,
                'actual_hours': 7
            },
            {
                'title': 'Implement Authentication',
                'description': 'JWT-based authentication with role management',
                'assigned_to': employees[0],
                'status': 'DONE',
                'priority': 'CRITICAL',
                'estimated_hours': 12,
                'actual_hours': 15
            },
            {
                'title': 'Design Dashboard UI',
                'description': 'Create mockups for manager and employee dashboards',
                'assigned_to': employees[2],
                'status': 'IN_PROGRESS',
                'priority': 'HIGH',
                'estimated_hours': 16,
                'actual_hours': 10
            },
            {
                'title': 'Build Task Management API',
                'description': 'CRUD operations for tasks with filters',
                'assigned_to': employees[1],
                'status': 'IN_PROGRESS',
                'priority': 'MEDIUM',
                'estimated_hours': 10,
                'actual_hours': 8
            },
            {
                'title': 'Implement Delay Prediction Logic',
                'description': 'Algorithm to predict task delays based on activity',
                'assigned_to': employees[0],
                'status': 'BLOCKED',
                'priority': 'CRITICAL',
                'estimated_hours': 20,
                'actual_hours': 12
            },
            {
                'title': 'Create Performance Scoring System',
                'description': 'Calculate employee performance metrics',
                'assigned_to': employees[1],
                'status': 'TODO',
                'priority': 'MEDIUM',
                'estimated_hours': 15,
                'actual_hours': 0
            },
            {
                'title': 'Setup Database Models',
                'description': 'Define all required models and relationships',
                'assigned_to': employees[0],
                'status': 'DONE',
                'priority': 'HIGH',
                'estimated_hours': 6,
                'actual_hours': 6
            },
            {
                'title': 'Integrate Risk Alert System',
                'description': 'Automatic detection and notification of project risks',
                'assigned_to': employees[1],
                'status': 'BLOCKED',
                'priority': 'HIGH',
                'estimated_hours': 12,
                'actual_hours': 8
            },
            {
                'title': 'Write Unit Tests',
                'description': 'Comprehensive test coverage for all features',
                'assigned_to': employees[0],
                'status': 'IN_PROGRESS',
                'priority': 'MEDIUM',
                'estimated_hours': 20,
                'actual_hours': 15
            },
            {
                'title': 'Deploy to Production',
                'description': 'Setup CI/CD pipeline and deploy',
                'assigned_to': employees[1],
                'status': 'TODO',
                'priority': 'LOW',
                'estimated_hours': 8,
                'actual_hours': 0
            }
        ]
        
        for task_data in tasks_data:
            task = Task.objects.create(
                project=project,
                sprint=sprint,
                **task_data
            )
            self.stdout.write(f'Created Task: {task.title}')
            
            if task.status == 'DONE':
                CommitLog.objects.create(
                    task=task,
                    commit_message=f'Completed {task.title}',
                    commit_time=date.today() - timedelta(days=2)
                )
            elif task.status == 'BLOCKED':
                CommitLog.objects.create(
                    task=task,
                    commit_message=f'Working on {task.title} - encountered issue',
                    commit_time=date.today() - timedelta(days=4)
                )
        
        blocked_task = Task.objects.filter(status='BLOCKED').first()
        if blocked_task:
            blocked_task.last_updated = date.today() - timedelta(days=5)
            blocked_task.save()
        
        for emp in employees:
            active_tasks = emp.assigned_tasks.filter(status__in=['TODO', 'IN_PROGRESS', 'BLOCKED']).count()
            if active_tasks > 5:
                RiskAlert.objects.create(
                    project=project,
                    message=f'{emp.username} is overloaded with {active_tasks} active tasks',
                    severity='HIGH'
                )
        
        RiskAlert.objects.create(
            project=project,
            message='Multiple tasks blocked for over 3 days',
            severity='CRITICAL'
        )
        
        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
        self.stdout.write(f'\nLogin credentials:')
        self.stdout.write(f'Manager: username=pm_john, password=password123')
        self.stdout.write(f'Employees: username=alice/bob/carol, password=password123')
