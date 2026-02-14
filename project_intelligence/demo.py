#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_intelligence.settings')
django.setup()

from django.contrib.auth import get_user_model
from main.models import Project, Sprint, Task
from main.services import ProjectIntelligenceService

User = get_user_model()

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def demo_system():
    print_header("PROJECT INTELLIGENCE SYSTEM DEMONSTRATION")
    
    manager = User.objects.filter(role='PROJECT_MANAGER').first()
    if not manager:
        print("Error: No project manager found. Please run load_sample_data first.")
        return
    
    employee = User.objects.filter(role='EMPLOYEE').first()
    if not employee:
        print("Error: No employees found. Please run load_sample_data first.")
        return
    
    project = Project.objects.first()
    if not project:
        print("Error: No projects found. Please run load_sample_data first.")
        return
    
    print_header("1. PROJECT OVERVIEW")
    print(f"Project: {project.name}")
    print(f"Manager: {project.manager.username}")
    print(f"Duration: {project.start_date} to {project.end_date}")
    print(f"Total Tasks: {project.tasks.count()}")
    
    print_header("2. PROJECT RISK ANALYSIS")
    risk_score = ProjectIntelligenceService.calculate_project_risk_score(project)
    health_score = 100 - risk_score
    print(f"Project Health Score: {health_score:.2f}/100")
    print(f"Project Risk Score: {risk_score:.2f}/100")
    
    if risk_score > 70:
        print("Status: CRITICAL - Immediate attention required")
    elif risk_score > 40:
        print("Status: AT RISK - Monitor closely")
    else:
        print("Status: HEALTHY - On track")
    
    print_header("3. SPRINT COMPLETION ANALYSIS")
    sprint = project.sprints.first()
    if sprint:
        completion_prob = ProjectIntelligenceService.calculate_sprint_completion_probability(sprint)
        print(f"Sprint {sprint.sprint_number}")
        print(f"Period: {sprint.start_date} to {sprint.end_date}")
        print(f"Completion Probability: {completion_prob:.2f}%")
        
        tasks_by_status = {
            'TODO': sprint.tasks.filter(status='TODO').count(),
            'IN_PROGRESS': sprint.tasks.filter(status='IN_PROGRESS').count(),
            'BLOCKED': sprint.tasks.filter(status='BLOCKED').count(),
            'DONE': sprint.tasks.filter(status='DONE').count(),
        }
        
        print("\nTask Distribution:")
        for status, count in tasks_by_status.items():
            print(f"  {status}: {count}")
    
    print_header("4. DELAY PREDICTIONS")
    at_risk_tasks = []
    for task in project.tasks.exclude(status='DONE'):
        prediction = ProjectIntelligenceService.calculate_delay_prediction(task)
        if prediction['delay_score'] > 50:
            at_risk_tasks.append((task, prediction))
    
    if at_risk_tasks:
        print(f"Found {len(at_risk_tasks)} tasks at risk of delay:\n")
        for task, prediction in at_risk_tasks[:5]:
            print(f"Task: {task.title}")
            print(f"  Status: {task.status}")
            print(f"  Delay Score: {prediction['delay_score']:.2f}")
            print(f"  Risk Level: {prediction['risk_level']}")
            print(f"  Predicted Delay: {prediction['predicted_delay_days']} days")
            print()
    else:
        print("No tasks currently at risk of delay")
    
    print_header("5. WORKLOAD ANALYSIS")
    overloaded = ProjectIntelligenceService.detect_workload_issues()
    
    if overloaded:
        print(f"Found {len(overloaded)} overloaded employees:\n")
        for emp_data in overloaded:
            print(f"Employee: {emp_data['username']}")
            print(f"  Active Tasks: {emp_data['active_tasks']}")
            print(f"  Overload Level: {emp_data['overload_level']}")
            print()
    else:
        print("All employees have manageable workloads")
    
    print_header("6. BLOCKER DETECTION")
    alerts = ProjectIntelligenceService.detect_blockers(project)
    
    if alerts:
        print(f"Detected {len(alerts)} new blockers:\n")
        for alert in alerts[:5]:
            print(f"[{alert.severity}] {alert.message}")
            print()
    else:
        print("No new blockers detected")
    
    print_header("7. EMPLOYEE PERFORMANCE SCORES")
    employees = User.objects.filter(role='EMPLOYEE')
    
    print("Performance Rankings:\n")
    employee_scores = []
    
    for emp in employees:
        score = ProjectIntelligenceService.calculate_performance_score(emp)
        employee_scores.append((emp, score))
    
    employee_scores.sort(key=lambda x: x[1], reverse=True)
    
    for emp, score in employee_scores:
        tasks_completed = emp.assigned_tasks.filter(status='DONE').count()
        tasks_active = emp.assigned_tasks.filter(status__in=['TODO', 'IN_PROGRESS', 'BLOCKED']).count()
        
        print(f"{emp.username}:")
        print(f"  Performance Score: {score:.2f}/100")
        print(f"  Completed Tasks: {tasks_completed}")
        print(f"  Active Tasks: {tasks_active}")
        print()
    
    print_header("8. MANAGER DASHBOARD PREVIEW")
    dashboard = ProjectIntelligenceService.generate_manager_dashboard(manager)
    
    print(f"Overall Health: {dashboard['overall_health']:.2f}/100")
    print(f"Total Projects: {len(dashboard['projects'])}")
    print(f"Active Risk Alerts: {dashboard['total_risk_alerts']}")
    print(f"Overloaded Employees: {len(dashboard['overloaded_employees'])}")
    
    print_header("9. EMPLOYEE DASHBOARD PREVIEW")
    emp_dashboard = ProjectIntelligenceService.generate_employee_dashboard(employee)
    
    print(f"Employee: {employee.username}")
    print(f"Performance Score: {emp_dashboard['performance_score']}/100")
    print(f"Workload Status: {emp_dashboard['workload_status']}")
    print(f"Active Tasks: {emp_dashboard['active_tasks_count']}")
    print(f"Completed Tasks: {emp_dashboard['completed_tasks_count']}")
    
    print("\nTask Breakdown:")
    for status, count in emp_dashboard['task_breakdown'].items():
        print(f"  {status}: {count}")
    
    print_header("DEMONSTRATION COMPLETE")
    print("\nKey Insights:")
    print(f"✓ Project health automatically calculated: {health_score:.2f}/100")
    print(f"✓ Sprint completion probability: {completion_prob:.2f}%")
    print(f"✓ At-risk tasks identified: {len(at_risk_tasks)}")
    print(f"✓ Workload issues detected: {len(overloaded)}")
    print(f"✓ Performance scores calculated for {len(employee_scores)} employees")
    print("\nThe system provides continuous, automated project intelligence")
    print("without manual updates or status meetings.")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    demo_system()
