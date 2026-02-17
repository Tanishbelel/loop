from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('EMPLOYEE', 'Employee'),
        ('PROJECT_MANAGER', 'Project Manager'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_projects')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Phase(models.Model):
    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        related_name="phases"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    phase_order = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["project", "phase_order"]
        ordering = ["phase_order"]

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class Sprint(models.Model):
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name='phases')
    sprint_number = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    completion_probability = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['phase', 'sprint_number']
        ordering = ['-sprint_number']

    def __str__(self):
        return f"{self.phase.name} - Sprint {self.sprint_number}"


class Team(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        related_name="teams"
    )
    members = models.ManyToManyField(
        User,
        related_name="teams"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('BLOCKED', 'Blocked'),
        ('DONE', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    team = models.ForeignKey(Team,on_delete=models.SET_NULL,null=True,blank=True,related_name="tasks")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    estimated_hours = models.FloatField(default=0.0)
    actual_hours = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class MicroTask(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('BLOCKED', 'Blocked'),
        ('DONE', 'Done'),
    ]

    task = models.ForeignKey(
        "Task",
        on_delete=models.CASCADE,
        related_name="micro_tasks"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    developer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="micro_tasks"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='TODO'
    )

    estimated_minutes = models.IntegerField(default=0)
    actual_minutes = models.IntegerField(default=0)

    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]
        unique_together = ["task", "order"]

    def __str__(self):
        return f"{self.task.title} → {self.title}"


class CommitLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='commits')
    commit_message = models.TextField()
    commit_time = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-commit_time']

    def __str__(self):
        return f"Commit for {self.task.title} at {self.commit_time}"


class RiskAlert(models.Model):
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='risk_alerts')
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.severity}: {self.message[:50]}"


class ScrumMeeting(models.Model):
    MEETING_TYPES = [
        ('DAILY_STANDUP', 'Daily Standup'),
        ('SPRINT_PLANNING', 'Sprint Planning'),
        ('SPRINT_REVIEW', 'Sprint Review'),
        ('SPRINT_RETRO', 'Sprint Retrospective'),
    ]

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='meetings')
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetings')
    participants = models.ManyToManyField(User, related_name='scrum_meetings', blank=True)
    agenda = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True)
    action_items = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-scheduled_time']

    def __str__(self):
        return f"{self.title} - {self.get_meeting_type_display()}"
