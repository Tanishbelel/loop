from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Project, Sprint, Task, CommitLog, RiskAlert

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'start_date', 'end_date', 'created_at']
    list_filter = ['start_date', 'end_date']
    search_fields = ['name', 'description']

@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ['project', 'sprint_number', 'start_date', 'end_date', 'completion_probability']
    list_filter = ['project', 'start_date']
    ordering = ['project', '-sprint_number']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'assigned_to', 'status', 'priority', 'estimated_hours', 'actual_hours']
    list_filter = ['status', 'priority', 'project']
    search_fields = ['title', 'description']

@admin.register(CommitLog)
class CommitLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'commit_time', 'commit_message']
    list_filter = ['commit_time']
    search_fields = ['commit_message']

@admin.register(RiskAlert)
class RiskAlertAdmin(admin.ModelAdmin):
    list_display = ['project', 'severity', 'is_resolved', 'created_at', 'message']
    list_filter = ['severity', 'is_resolved', 'created_at']
    search_fields = ['message']
