from django.utils.decorators import method_decorator
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from .models import Project, Sprint, Task, CommitLog, RiskAlert, ScrumMeeting, Team, Phase, MicroTask, \
    GithubInstallation, PendingRepoDeletion
from .serializers import (
    UserSerializer, UserProfileSerializer, ProjectSerializer,
    SprintSerializer, TaskSerializer, CommitLogSerializer, RiskAlertSerializer,
    ScrumMeetingSerializer, TeamSerializer, PhaseSerializer, MicroTaskSerializer
)
from .permissions import IsProjectManager, IsOwnerOrProjectManager
from .services import ProjectIntelligenceService, GithubServices, GithubAPIError
import json
import os
import hmac
import hashlib
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

load_dotenv()

User = get_user_model()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    print(username)
    print(password)

    user = authenticate(username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsProjectManager()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PROJECT_MANAGER':
            return Project.objects.filter(manager=user)
        else:
            return Project.objects.filter(tasks__assigned_to=user).distinct()

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)


class SprintViewSet(viewsets.ModelViewSet):
    queryset = Sprint.objects.all()
    serializer_class = SprintSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsProjectManager()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PROJECT_MANAGER':
            return Sprint.objects.filter(project__manager=user)
        else:
            return Sprint.objects.filter(tasks__assigned_to=user).distinct()


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsProjectManager()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PROJECT_MANAGER':
            return Task.objects.filter(project__manager=user)
        else:
            return Task.objects.filter(assigned_to=user)

    @action(detail=True, methods=['post'])
    def update_hours(self, request, pk=None):
        task = self.get_object()
        actual_hours = request.data.get('actual_hours')

        if actual_hours is not None:
            task.actual_hours = float(actual_hours)
            task.save()

            delay_prediction = ProjectIntelligenceService.calculate_delay_prediction(task)

            return Response({
                'task': TaskSerializer(task).data,
                'delay_prediction': delay_prediction
            })

        return Response({'error': 'actual_hours required'}, status=status.HTTP_400_BAD_REQUEST)


class CommitLogViewSet(viewsets.ModelViewSet):
    queryset = CommitLog.objects.all()
    serializer_class = CommitLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PROJECT_MANAGER':
            return CommitLog.objects.filter(task__project__manager=user)
        else:
            return CommitLog.objects.filter(task__assigned_to=user)


class RiskAlertViewSet(viewsets.ModelViewSet):
    queryset = RiskAlert.objects.all()
    serializer_class = RiskAlertSerializer
    permission_classes = [IsProjectManager]

    def get_queryset(self):
        return RiskAlert.objects.filter(project__manager=self.request.user)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.is_resolved = True
        alert.save()
        return Response({'status': 'resolved'})


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.prefetch_related("members").all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class PhaseViewSet(viewsets.ModelViewSet):
    queryset = Phase.objects.select_related("project").all()
    serializer_class = PhaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class MicroTaskViewSet(viewsets.ModelViewSet):
    queryset = MicroTask.objects.select_related(
        "task",
        "developer",
        "task__team"
    ).all()

    serializer_class = MicroTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()

        task_id = self.request.query_params.get("task")
        dev_id = self.request.query_params.get("developer")
        team_id = self.request.query_params.get("team")

        if task_id:
            qs = qs.filter(task_id=task_id)
        if dev_id:
            qs = qs.filter(developer_id=dev_id)
        if team_id:
            qs = qs.filter(task__team_id=team_id)

        return qs


class GithubViews(APIView):

    # =========================================================
    # 1️⃣ Handle App Install Events
    # =========================================================
    @staticmethod
    @csrf_exempt
    def github_app_events(request):
        if request.method != "POST":
            return HttpResponse(status=405)

        payload = json.loads(request.body)
        print(payload)

        event = request.headers.get("X-GitHub-Event")

        if event == "installation":
            installation_id = payload["installation"]["id"]
            org_name = payload["installation"]["account"]["login"]

            GithubInstallation.objects.update_or_create(
                org_name=org_name,
                defaults={"installation_id": installation_id}
            )

            return JsonResponse({"status": "installation saved"})

        return JsonResponse({"status": "ignored"})

    # =========================================================
    # 2️⃣ Create Repo + Webhook
    # =========================================================
    @staticmethod
    @permission_classes([IsProjectManager])
    @csrf_exempt
    def create_repo(request):
        if request.method != "POST":
            return HttpResponse(status=405)

        data = json.loads(request.body)
        repo_name = data["repo_name"]
        org_name = data["org_name"]

        install = GithubInstallation.objects.get(org_name=org_name)

        gh = GithubServices(org_name, install.installation_id)

        repo = gh.create_repository(repo_name)
        gh.create_webhook(repo_name)

        return JsonResponse(repo)

    # =========================================================
    # 3️⃣ List Repos
    # =========================================================
    @staticmethod
    @permission_classes([IsProjectManager])
    @csrf_exempt
    def list_repos(request):
        org_name = request.GET.get("org")

        install = GithubInstallation.objects.get(org_name=org_name)

        gh = GithubServices(org_name, install.installation_id)
        repos = gh.list_repositories()

        return JsonResponse(repos, safe=False)

    # =========================================================
    # 4️⃣ Repo Webhook Listener
    # =========================================================
    @staticmethod
    @csrf_exempt
    def github_repo_webhook(request):
        if request.method != "POST":
            return HttpResponse(status=405)

        secret = os.getenv("GITHUB_WEBHOOK_SECRET").encode()
        signature = request.headers.get("X-Hub-Signature-256")

        digest = "sha256=" + hmac.new(secret, request.body, hashlib.sha256).hexdigest()

        if signature != digest:
            return HttpResponse("Invalid signature", status=401)

        payload = json.loads(request.body)
        print(payload)
        event = request.headers.get("X-GitHub-Event")

        print("Event:", event)

        if event == "push":
            print("Repo:", payload["repository"]["name"])
            print("Commits:", len(payload["commits"]))

        elif event == "pull_request":
            print("PR:", payload["pull_request"]["title"])

        return HttpResponse("OK")

    @staticmethod
    @permission_classes([IsProjectManager])
    @csrf_exempt
    def safe_delete_repo(request):
        try:
            data = json.loads(request.body)
            repo_name = data["repo_name"]
            org_name = data["org_name"]
            install = GithubInstallation.objects.get(org_name=org_name)
            installation_id = install.installation_id

            gh = GithubServices(org_name,installation_id)
            gh.archive_repository(repo_name)

            PendingRepoDeletion.objects.create(
                repo_name=repo_name,
                owner=gh.org
            )

            return JsonResponse({"message": "Repo archived successfully"}, status=200)

        except GithubAPIError as e:

            # 👇 Handle known GitHub messages
            if "archived so is read-only" in e.message:
                return JsonResponse({
                    "message": "Repo already archived. Nothing to do."
                }, status=200)

            if e.status_code == 404:
                return JsonResponse({"error": "Repository not found"}, status=404)

            if e.status_code == 403:
                return JsonResponse({"error": "Permission denied"}, status=403)

            return JsonResponse({"error": e.message}, status=400)

    @staticmethod
    @permission_classes([IsProjectManager])
    @csrf_exempt
    def confirm_delete_repo(request):
        if request.method != "POST":
            return HttpResponse(status=405)

        data = json.loads(request.body)

        repo_name = data["repo_name"]
        org_name = data["org_name"]
        install = GithubInstallation.objects.get(org_name=org_name)
        installation_id = install.installation_id

        gh = GithubServices(org_name,installation_id)

        gh.delete_repository(repo_name)

        PendingRepoDeletion.objects.filter(repo_name=repo_name).update(confirmed=True)

        return JsonResponse({"message": "Repository permanently deleted"})


@api_view(['GET'])
@permission_classes([IsProjectManager])
def manager_dashboard(request):
    dashboard_data = ProjectIntelligenceService.generate_manager_dashboard(request.user)
    return Response(dashboard_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def employee_dashboard(request):
    if request.user.role != 'EMPLOYEE':
        return Response({'error': 'Only employees can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

    dashboard_data = ProjectIntelligenceService.generate_employee_dashboard(request.user)
    return Response(dashboard_data)


@api_view(['POST'])
@permission_classes([IsProjectManager])
def detect_project_risks(request, project_id):
    try:
        project = Project.objects.get(id=project_id, manager=request.user)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    alerts = ProjectIntelligenceService.detect_blockers(project)

    return Response({
        'project_id': project_id,
        'new_alerts': RiskAlertSerializer(alerts, many=True).data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def performance_score(request):
    score = ProjectIntelligenceService.calculate_performance_score(request.user)
    return Response({
        'user_id': request.user.id,
        'username': request.user.username,
        'performance_score': round(score, 2)
    })


# Employee Management
@api_view(['GET'])
@permission_classes([IsProjectManager])
def list_employees(request):
    """List all employees for task assignment"""
    employees = User.objects.filter(role='EMPLOYEE').annotate(
        active_tasks=Count('assigned_tasks', filter=Q(assigned_tasks__status__in=['TODO', 'IN_PROGRESS']))
    )
    return Response(UserSerializer(employees, many=True).data)


# Task Assignment
@api_view(['POST'])
@permission_classes([IsProjectManager])
def assign_task(request, task_id):
    """Assign task to employee"""
    task = get_object_or_404(Task, id=task_id)
    employee_id = request.data.get('employee_id')
    employee = get_object_or_404(User, id=employee_id, role='EMPLOYEE')

    task.assigned_to = employee
    task.save()

    return Response({
        'status': 'success',
        'message': f'Task assigned to {employee.username}',
        'task': TaskSerializer(task).data
    })


# Scrum Meetings
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def meetings_list(request):
    """List or create scrum meetings"""
    if request.method == 'GET':
        if request.user.role == 'PROJECT_MANAGER':
            meetings = ScrumMeeting.objects.filter(
                project__manager=request.user
            ).order_by('-scheduled_time')
        else:
            meetings = ScrumMeeting.objects.filter(
                Q(participants=request.user) | Q(project__tasks__assigned_to=request.user)
            ).distinct().order_by('-scheduled_time')

        return Response(ScrumMeetingSerializer(meetings, many=True).data)

    elif request.method == 'POST':
        if request.user.role != 'PROJECT_MANAGER':
            return Response({'error': 'Only managers can create meetings'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ScrumMeetingSerializer(data=request.data)
        if serializer.is_valid():
            meeting = serializer.save(organizer=request.user)
            return Response(ScrumMeetingSerializer(meeting).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def meeting_detail(request, meeting_id):
    """Get meeting details"""
    meeting = get_object_or_404(ScrumMeeting, id=meeting_id)
    return Response(ScrumMeetingSerializer(meeting).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_meeting(request, meeting_id):
    """Employee joins a meeting"""
    meeting = get_object_or_404(ScrumMeeting, id=meeting_id)
    meeting.participants.add(request.user)

    return Response({
        'status': 'success',
        'message': f'Joined meeting: {meeting.title}',
        'meeting': ScrumMeetingSerializer(meeting).data
    })


@api_view(['POST'])
@permission_classes([IsProjectManager])
def start_meeting(request, meeting_id):
    """Start a meeting"""
    meeting = get_object_or_404(ScrumMeeting, id=meeting_id, organizer=request.user)
    meeting.status = 'IN_PROGRESS'
    meeting.save()

    return Response({
        'status': 'success',
        'message': 'Meeting started',
        'meeting': ScrumMeetingSerializer(meeting).data
    })


@api_view(['POST'])
@permission_classes([IsProjectManager])
def complete_meeting(request, meeting_id):
    """Complete a meeting and optionally add notes"""
    from django.utils import timezone

    meeting = get_object_or_404(ScrumMeeting, id=meeting_id, organizer=request.user)
    meeting.status = 'COMPLETED'
    meeting.completed_at = timezone.now()

    if 'notes' in request.data:
        meeting.notes = request.data['notes']

    meeting.save()

    return Response({
        'status': 'success',
        'message': 'Meeting completed',
        'meeting': ScrumMeetingSerializer(meeting).data
    })


@api_view(['POST'])
@permission_classes([IsProjectManager])
def generate_meeting_summary(request, meeting_id):
    """Generate AI summary for completed meeting"""
    meeting = get_object_or_404(ScrumMeeting, id=meeting_id, organizer=request.user)

    # Generate AI summary
    participants = [p.username for p in meeting.participants.all()]

    # Simulate AI summary (in production, use actual AI service)
    summary_text = f"Productive {meeting.get_meeting_type_display()} with {len(participants)} participants. "
    summary_text += "Team discussed progress, identified blockers, and planned next steps."

    action_items = [
        {
            'item': 'Review sprint progress',
            'owner': participants[0] if participants else 'Unassigned',
            'priority': 'HIGH'
        },
        {
            'item': 'Update task estimates',
            'owner': participants[1] if len(participants) > 1 else 'Unassigned',
            'priority': 'MEDIUM'
        }
    ]

    meeting.ai_summary = summary_text
    meeting.action_items = action_items
    meeting.save()

    return Response({
        'status': 'success',
        'summary': summary_text,
        'action_items': action_items,
        'meeting': ScrumMeetingSerializer(meeting).data
    })
