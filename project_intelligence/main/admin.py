from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    Project,
    Phase,
    Sprint,
    Team,
    Task,
    MicroTask,
    CommitLog,
    RiskAlert,
)

# =====================================
# USER ADMIN
# =====================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


# =====================================
# PROJECT ADMIN
# =====================================

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'start_date', 'end_date', 'created_at']
    list_filter = ['start_date', 'end_date']
    search_fields = ['name', 'description']


# =====================================
# TEAM ADMIN
# =====================================

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'member_count', 'created_at']
    list_filter = ['project']
    search_fields = ['name']
    filter_horizontal = ['members']

    def member_count(self, obj):
        return obj.members.count()


# =====================================
# PHASE ADMIN
# =====================================

@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'phase_order', 'start_date', 'end_date']
    list_filter = ['project']
    ordering = ['project', 'phase_order']
    search_fields = ['name', 'description']


# =====================================
# SPRINT ADMIN
# =====================================

@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = [
        'get_project',
        'phase',
        'sprint_number',
        'start_date',
        'end_date',
        'completion_probability'
    ]
    list_filter = ['phase', 'phase__project', 'start_date']
    ordering = ['phase__project', 'phase', '-sprint_number']
    search_fields = ['phase__name', 'phase__project__name']

    def get_project(self, obj):
        return obj.phase.project
    get_project.short_description = "Project"


# =====================================
# MICRO TASK INLINE
# =====================================

class MicroTaskInline(admin.TabularInline):
    model = MicroTask
    extra = 1
    autocomplete_fields = ['developer']


# =====================================
# TASK ADMIN
# =====================================

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = [MicroTaskInline]

    list_display = [
        'title',
        'project',
        'team',
        'status',
        'priority',
        'estimated_hours',
        'actual_hours'
    ]

    list_filter = ['status', 'priority', 'project', 'team']
    search_fields = ['title', 'description']
    autocomplete_fields = ['team', 'sprint']


# =====================================
# MICRO TASK ADMIN
# =====================================

@admin.register(MicroTask)
class MicroTaskAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'task',
        'developer',
        'status',
        'estimated_minutes',
        'actual_minutes',
        'created_at'
    ]

    list_filter = ['status', 'task__project']
    search_fields = ['title', 'description']
    autocomplete_fields = ['developer', 'task']


# =====================================
# COMMIT LOG ADMIN
# =====================================

@admin.register(CommitLog)
class CommitLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'commit_time', 'commit_message']
    list_filter = ['commit_time']
    search_fields = ['commit_message']


# =====================================
# RISK ALERT ADMIN
# =====================================

@admin.register(RiskAlert)
class RiskAlertAdmin(admin.ModelAdmin):
    list_display = ['project', 'severity', 'is_resolved', 'created_at', 'message']
    list_filter = ['severity', 'is_resolved', 'created_at']
    search_fields = ['message']
