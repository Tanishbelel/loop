from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, Sprint, Task, CommitLog, RiskAlert, ScrumMeeting

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'EMPLOYEE'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'role']

class ProjectSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'manager', 'manager_name', 'created_at',
            'github_repo_url', 'github_repo_owner', 'github_repo_name', 'last_commit_sync'
        ]
        read_only_fields = ['id', 'manager', 'manager_name', 'created_at', 'last_commit_sync']
    
    def validate(self, data):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("End date must be after start date")
        return data

class SprintSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Sprint
        fields = ['id', 'project', 'project_name', 'sprint_number', 'start_date', 'end_date', 'completion_probability', 'created_at']
        read_only_fields = ['completion_probability', 'created_at']
    
    def validate(self, data):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("End date must be after start date")
        return data

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    sprint_number = serializers.IntegerField(source='sprint.sprint_number', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'project_name',
            'sprint', 'sprint_number', 'assigned_to', 'assigned_to_name',
            'status', 'priority', 'estimated_hours', 'actual_hours',
            'last_updated', 'created_at'
        ]
        read_only_fields = ['last_updated', 'created_at']
    
    def validate(self, data):
        if data.get('actual_hours', 0) < 0:
            raise serializers.ValidationError("Actual hours cannot be negative")
        if data.get('estimated_hours', 0) < 0:
            raise serializers.ValidationError("Estimated hours cannot be negative")
        return data

class CommitLogSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True, allow_null=True)
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    
    class Meta:
        model = CommitLog
        fields = [
            'id', 'task', 'task_title', 'project', 'project_name',
            'commit_message', 'commit_sha', 'commit_author', 'commit_author_email',
            'branch', 'files_changed', 'lines_added', 'lines_deleted',
            'is_meaningful', 'trivial_reason', 'github_url',
            'commit_time', 'created_at'
        ]
        read_only_fields = ['created_at']

class RiskAlertSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = RiskAlert
        fields = ['id', 'project', 'project_name', 'message', 'severity', 'is_resolved', 'created_at']
        read_only_fields = ['created_at']

class ScrumMeetingSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    participant_count = serializers.SerializerMethodField()
    participant_names = serializers.SerializerMethodField()
    
    class Meta:
        model = ScrumMeeting
        fields = [
            'id', 'project', 'project_name', 'meeting_type', 'title', 'description',
            'scheduled_time', 'duration_minutes', 'status', 'organizer', 'organizer_name',
            'participants', 'participant_count', 'participant_names', 'agenda', 'notes',
            'transcript', 'ai_summary', 'action_items', 'created_at', 'completed_at'
        ]
        read_only_fields = ['created_at', 'organizer']
    
    def get_participant_count(self, obj):
        return obj.participants.count()
    
    def get_participant_names(self, obj):
        return [p.username for p in obj.participants.all()]

