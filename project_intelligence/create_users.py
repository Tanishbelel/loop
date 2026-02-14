import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_intelligence.settings')
django.setup()

from django.contrib.auth import get_user_model
from main.models import Project, Task, Sprint
from datetime import datetime, timedelta

User = get_user_model()

# Create users
users_data = [
    {'username': 'tanish', 'password': 'tanish123', 'role': 'PROJECT_MANAGER', 'first_name': 'Tanish', 'last_name': 'Kumar', 'email': 'tanish@example.com'},
    {'username': 'drash', 'password': 'drash123', 'role': 'EMPLOYEE', 'first_name': 'Drash', 'last_name': 'Patel', 'email': 'drash@example.com'},
    {'username': 'manas', 'password': 'manas123', 'role': 'EMPLOYEE', 'first_name': 'Manas', 'last_name': 'Singh', 'email': 'manas@example.com'},
    {'username': 'sidi', 'password': 'sidi123', 'role': 'EMPLOYEE', 'first_name': 'Sidi', 'last_name': 'Sharma', 'email': 'sidi@example.com'},
]

print("Creating users...")
for user_data in users_data:
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults={
            'email': user_data['email'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'role': user_data['role']
        }
    )
    if created:
        user.set_password(user_data['password'])
        user.save()
        print(f"✓ Created {user_data['role']}: {user_data['username']} (password: {user_data['password']})")
    else:
        print(f"- User {user_data['username']} already exists")

# Create sample project
tanish = User.objects.get(username='tanish')
project, created = Project.objects.get_or_create(
    name='E-Commerce Platform',
    defaults={
        'description': 'Building a modern e-commerce platform with React and Django',
        'start_date': datetime.now().date(),
        'end_date': (datetime.now() + timedelta(days=90)).date(),
        'manager': tanish
    }
)

if created:
    print(f"\n✓ Created project: {project.name}")
    
    # Create sprint
    sprint = Sprint.objects.create(
        project=project,
        sprint_number=1,
        start_date=datetime.now().date(),
        end_date=(datetime.now() + timedelta(days=14)).date()
    )
    print(f"✓ Created Sprint 1")
    
    # Create sample tasks
    tasks_data = [
        {'title': 'Setup React Frontend', 'description': 'Initialize React app with Vite and configure routing', 'priority': 'HIGH', 'estimated_hours': 8},
        {'title': 'Design Database Schema', 'description': 'Create ERD and define all models', 'priority': 'HIGH', 'estimated_hours': 6},
        {'title': 'Implement User Authentication', 'description': 'JWT-based authentication system', 'priority': 'CRITICAL', 'estimated_hours': 12},
        {'title': 'Create Product Catalog UI', 'description': 'Product listing and detail pages', 'priority': 'MEDIUM', 'estimated_hours': 10},
        {'title': 'Shopping Cart Functionality', 'description': 'Add to cart, update quantities, checkout flow', 'priority': 'HIGH', 'estimated_hours': 16},
        {'title': 'Payment Integration', 'description': 'Integrate payment gateway', 'priority': 'MEDIUM', 'estimated_hours': 14},
    ]
    
    for task_data in tasks_data:
        Task.objects.create(
            project=project,
            sprint=sprint,
            **task_data
        )
    
    print(f"✓ Created {len(tasks_data)} tasks")
else:
    print(f"\n- Project '{project.name}' already exists")

print("\n✅ Setup complete!")
print("\nLogin credentials:")
print("=" * 50)
for user_data in users_data:
    print(f"{user_data['role']:20} | {user_data['username']:10} | {user_data['password']}")
print("=" * 50)
