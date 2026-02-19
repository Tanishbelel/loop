from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from .models import Project, Sprint, Task, CommitLog, RiskAlert, ScrumMeeting
import re
from .serializers import (
    UserSerializer, UserProfileSerializer, ProjectSerializer,
    SprintSerializer, TaskSerializer, CommitLogSerializer, RiskAlertSerializer,
    ScrumMeetingSerializer
)
from .permissions import IsProjectManager, IsOwnerOrProjectManager
from .services import ProjectIntelligenceService, GitHubService

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
@permission_classes([permissions.IsAuthenticated])
def save_transcript(request, meeting_id):
    """Save speech transcript from the meeting room"""
    meeting = get_object_or_404(ScrumMeeting, id=meeting_id)
    transcript = request.data.get('transcript', '')
    meeting.transcript = transcript
    meeting.save()
    return Response({'status': 'success', 'message': 'Transcript saved'})


def _generate_ai_summary_gemini(transcript, meeting, participants):
    """
    Use Google Gemini to generate an intelligent, structured meeting summary.
    Falls back to basic extraction if the API key is not set or the call fails.
    """
    from django.conf import settings
    import json as json_lib

    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key or api_key == 'YOUR_GEMINI_API_KEY_HERE':
        return _fallback_summary(transcript, meeting, participants)

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        participant_list = ', '.join(participants) if participants else 'the team'
        meeting_type = meeting.get_meeting_type_display()
        agenda = meeting.agenda or 'Not specified'

        prompt = f"""You are an expert meeting analyst. Analyze the following meeting transcript and produce a structured, insightful summary.

Meeting Details:
- Type: {meeting_type}
- Participants: {participant_list}
- Agenda: {agenda}

Transcript:
\"\"\"
{transcript}
\"\"\"

Produce a JSON response with EXACTLY this structure (no markdown, raw JSON only):
{{
  "summary": "A concise 3-5 sentence executive summary of what was discussed, decided, and accomplished. Do NOT just repeat the transcript — synthesize and interpret it intelligently.",
  "key_decisions": ["decision 1", "decision 2"],
  "blockers": ["blocker 1", "blocker 2"],
  "action_items": [
    {{"item": "clear action description", "owner": "person name or Team", "priority": "HIGH|MEDIUM|LOW"}}
  ]
}}

Rules:
- summary must be analytical and insightful, NOT a repetition of words spoken
- Extract real action items from what was said (things people committed to doing)
- If the transcript is in Hindi or mixed language, still respond in English
- If no blockers/decisions found, use empty arrays []
- Limit action_items to max 5
"""

        # Single request — no retries (free tier has low RPM; retrying just burns quota)
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=prompt,
        )

        raw = response.text.strip()

        # Strip markdown code fences if present
        if raw.startswith('```'):
            raw = re.sub(r'^```[a-z]*\n?', '', raw)
            raw = re.sub(r'\n?```$', '', raw)

        parsed = json_lib.loads(raw)
        summary_text = parsed.get('summary', '')
        action_items = parsed.get('action_items', [])

        # Append key decisions and blockers to summary
        decisions = parsed.get('key_decisions', [])
        blockers = parsed.get('blockers', [])
        if decisions:
            summary_text += '\n\nKey Decisions: ' + '; '.join(decisions) + '.'
        if blockers:
            summary_text += '\n\nBlockers Identified: ' + '; '.join(blockers) + '.'

        # Normalise action items
        normalised = []
        for item in action_items[:5]:
            normalised.append({
                'item': str(item.get('item', '')).strip(),
                'owner': str(item.get('owner', 'Team')).strip(),
                'priority': str(item.get('priority', 'MEDIUM')).upper(),
            })

        return summary_text, normalised

    except Exception as e:
        print(f'Gemini summary generation failed: {e}')
        return _fallback_summary(transcript, meeting, participants)



def _fallback_summary(transcript, meeting, participants):
    """
    Smart rule-based summary when Gemini is unavailable.
    Extracts real sentences, detects blockers/decisions/commitments, names owners.
    """
    import re as _re

    meeting_type = meeting.get_meeting_type_display()
    participant_str = ', '.join(participants) if participants else 'the team'

    if not transcript or len(transcript.strip()) < 20:
        summary = (
            f"A {meeting_type} was held with {participant_str}. "
            f"No transcript was recorded."
        )
        return summary, [{'item': 'Review meeting notes', 'owner': participants[0] if participants else 'Team', 'priority': 'MEDIUM'}]

    t = transcript.strip()
    sentences = [s.strip() for s in _re.split(r'(?<=[.!?])\s+', t) if len(s.strip()) > 10]

    # Pattern buckets
    blocker_kw   = ['blocked', 'blocker', 'stuck', 'issue', 'problem', 'error', 'bug', 'delay', 'waiting', 'can\'t', 'cannot', 'not working']
    decision_kw  = ['decided', 'agreed', 'will', 'going to', 'deadline', 'by friday', 'by tomorrow', 'by end of', 'approved', 'confirmed']
    progress_kw  = ['completed', 'done', 'finished', 'deployed', 'merged', 'shipped', 'fixed', 'resolved', 'implemented']
    action_kw    = ['will', 'need to', 'should', 'must', 'going to', 'assigned', 'take care', 'handle', 'follow up']

    tl = t.lower()
    blocker_sentences  = [s for s in sentences if any(k in s.lower() for k in blocker_kw)]
    decision_sentences = [s for s in sentences if any(k in s.lower() for k in decision_kw)]
    progress_sentences = [s for s in sentences if any(k in s.lower() for k in progress_kw)]

    # Build summary paragraph
    parts = []
    parts.append(f"The {meeting_type} was attended by {participant_str}.")

    if progress_sentences:
        parts.append(f"Progress reported: {progress_sentences[0]}")
    if decision_sentences:
        parts.append(f"Key point: {decision_sentences[0]}")
    if blocker_sentences:
        parts.append(f"A blocker was raised: {blocker_sentences[0]}")
    if not (progress_sentences or decision_sentences or blocker_sentences) and sentences:
        parts.append(sentences[0])

    summary = ' '.join(parts)

    # Extract action items: sentences with action keywords, try to find owner
    action_items = []
    for s in sentences:
        sl = s.lower()
        if any(k in sl for k in action_kw):
            owner = 'Team'
            for p in participants:
                if p.lower() in sl:
                    owner = p
                    break
            priority = 'HIGH' if any(k in sl for k in ['urgent', 'asap', 'today', 'tomorrow', 'friday', 'deadline']) else 'MEDIUM'
            action_items.append({'item': s[:120], 'owner': owner, 'priority': priority})
            if len(action_items) >= 3:
                break

    if not action_items:
        action_items = [{'item': 'Review meeting notes and follow up on discussed topics',
                         'owner': participants[0] if participants else 'Team', 'priority': 'MEDIUM'}]

    return summary, action_items



@api_view(['POST'])
@permission_classes([IsProjectManager])
def generate_meeting_summary(request, meeting_id):
    """Generate AI summary for completed meeting using Gemini"""
    meeting = get_object_or_404(ScrumMeeting, id=meeting_id, organizer=request.user)
    participants = [p.username for p in meeting.participants.all()]

    summary_text, action_items = _generate_ai_summary_gemini(meeting.transcript, meeting, participants)

    meeting.ai_summary = summary_text
    meeting.action_items = action_items
    meeting.save()

    return Response({
        'status': 'success',
        'summary': summary_text,
        'action_items': action_items,
        'meeting': ScrumMeetingSerializer(meeting).data
    })






# ─── GitHub Integration Views ────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsProjectManager])
def link_github_repo(request, project_id):
    """Link or create a GitHub repo on a project."""
    project = get_object_or_404(Project, id=project_id, manager=request.user)

    action_type = request.data.get('action', 'link')  # 'link' or 'create'
    token = request.data.get('token', '').strip()
    repo_url = request.data.get('repo_url', '').strip()
    new_repo_name = request.data.get('new_repo_name', '').strip()
    private = bool(request.data.get('private', False))

    if not token:
        return Response({'error': 'GitHub token is required'}, status=status.HTTP_400_BAD_REQUEST)

    if action_type == 'create':
        if not new_repo_name:
            return Response({'error': 'Repository name is required'}, status=status.HTTP_400_BAD_REQUEST)

        html_url, err = GitHubService.create_github_repo(
            owner=None,  # will be inferred by GitHub from the token
            repo_name=new_repo_name,
            token=token,
            description=project.description[:255] if project.description else '',
            private=private,
        )
        if err:
            try:
                import json as _j
                err_data = _j.loads(err)
                err_msg = err_data.get('message', err)
            except Exception:
                err_msg = str(err)
            return Response({'error': f'GitHub API error: {err_msg}'}, status=status.HTTP_400_BAD_REQUEST)

        owner, repo = GitHubService.parse_repo_url(html_url)
        project.github_repo_url = html_url
        project.github_token = token
        project.github_repo_owner = owner or ''
        project.github_repo_name = repo or new_repo_name
        project.save()

        return Response({
            'status': 'created',
            'repo_url': html_url,
            'owner': owner,
            'repo': repo or new_repo_name,
        })

    else:  # link
        if not repo_url:
            return Response({'error': 'Repository URL or owner/repo is required'}, status=status.HTTP_400_BAD_REQUEST)

        owner, repo = GitHubService.parse_repo_url(repo_url)
        if not owner or not repo:
            return Response({'error': 'Could not parse owner/repo from URL'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the token can access the repo
        test = GitHubService._github_request(f'/repos/{owner}/{repo}', token)
        if test is None:
            return Response({'error': 'Cannot access repository. Check URL and token permissions.'}, status=status.HTTP_400_BAD_REQUEST)

        project.github_repo_url = f'https://github.com/{owner}/{repo}'
        project.github_token = token
        project.github_repo_owner = owner
        project.github_repo_name = repo
        project.save()

        return Response({
            'status': 'linked',
            'repo_url': project.github_repo_url,
            'owner': owner,
            'repo': repo,
        })


@api_view(['POST'])
@permission_classes([IsProjectManager])
def sync_github_commits(request, project_id):
    """Sync commits from GitHub for a project."""
    project = get_object_or_404(Project, id=project_id, manager=request.user)

    if not project.github_repo_url:
        return Response({'error': 'No GitHub repository linked to this project'}, status=status.HTTP_400_BAD_REQUEST)

    result = GitHubService.fetch_commits(project)

    if result.get('error'):
        return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)

    # Return updated commits list
    commits = CommitLog.objects.filter(project=project).order_by('-commit_time')[:20]
    return Response({
        'status': 'synced',
        'new_commits': result['new'],
        'tasks_auto_completed': result['tasks_completed'],
        'commits': CommitLogSerializer(commits, many=True).data,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_project_commits(request, project_id):
    """Return recent commits for a project (manager or assigned employee)."""
    project = get_object_or_404(Project, id=project_id)

    # Access control
    user = request.user
    if user.role == 'PROJECT_MANAGER' and project.manager != user:
        return Response({'error': 'Not your project'}, status=status.HTTP_403_FORBIDDEN)

    limit = min(int(request.GET.get('limit', 20)), 100)
    commits = CommitLog.objects.filter(project=project).order_by('-commit_time')[:limit]
    return Response(CommitLogSerializer(commits, many=True).data)
