from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q, Avg
from .models import Task, RiskAlert, Sprint, User, CommitLog, Project
import urllib.request
import urllib.error
import json
import re as _re


class GitHubService:

    @staticmethod
    def parse_repo_url(repo_url):
        """Parse owner/repo from a GitHub URL or 'owner/repo' shorthand."""
        repo_url = repo_url.strip().rstrip('/')
        # Handle full URLs: https://github.com/owner/repo
        match = _re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', repo_url)
        if match:
            return match.group(1), match.group(2)
        # Handle shorthand: owner/repo
        if '/' in repo_url and not repo_url.startswith('http'):
            parts = repo_url.split('/')
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        return None, None

    @staticmethod
    def _github_request(path, token):
        """Make an authenticated GitHub API GET request, return parsed JSON or None."""
        url = f'https://api.github.com{path}'
        req = urllib.request.Request(url, headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'ProjectIntelligence/1.0',
        })
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f'GitHub API HTTPError {e.code} for {url}: {e.read().decode("utf-8", errors="replace")}')
            return None
        except Exception as e:
            print(f'GitHub API error for {url}: {e}')
            return None

    @staticmethod
    def is_meaningful_commit(commit_data, stats):
        """
        Returns (is_meaningful: bool, reason: str).
        A commit is TRIVIAL if:
          - It is a merge commit (2+ parents)
          - Total lines changed < 5
          - Message starts with 'Merge' / 'chore' / 'wip' (case-insensitive) with < 10 lines
          - Only .md / .txt / .json lock files changed
        """
        message = commit_data.get('commit', {}).get('message', '')
        parents = commit_data.get('parents', [])
        total = stats.get('total', 0)
        additions = stats.get('additions', 0)
        deletions = stats.get('deletions', 0)
        files = stats.get('files', [])

        # Merge commit
        if len(parents) >= 2:
            return False, 'Merge commit'

        # Trivially small (at least 1 meaningful line must change)
        if total < 1:
            return False, f'Too few lines changed ({total})'

        # Trivial message prefixes with tiny diff
        trivial_prefixes = ('merge ', 'wip ', 'chore:', 'chore ', 'style:', 'typo ', 'minor ')
        if any(message.lower().startswith(p) for p in trivial_prefixes) and total < 10:
            return False, 'Trivial commit prefix with small diff'

        # Only documentation/config files
        non_trivial_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go',
                                   '.c', '.cpp', '.cs', '.rb', '.php', '.rs', '.kt', '.swift',
                                   '.html', '.css', '.sql', '.sh', '.yaml', '.yml'}
        changed_exts = set()
        for f in files:
            fname = f.get('filename', '')
            ext = '.' + fname.rsplit('.', 1)[-1].lower() if '.' in fname else ''
            changed_exts.add(ext)
        if changed_exts and not changed_exts.intersection(non_trivial_extensions):
            return False, 'Only documentation/config files changed'

        return True, ''

    @staticmethod
    def auto_complete_tasks(project, commit_message, commit_sha):
        """
        Find tasks in project that are referenced by commit_message.
        Reference patterns: #<id>  or  exact task title substring (case-insensitive).
        Moves matched tasks to DONE and returns list of completed task objects.
        """
        completed = []
        tasks = project.tasks.exclude(status='DONE')

        for task in tasks:
            referenced = False
            # Pattern: #<task_id>
            if _re.search(rf'#\s*{task.id}\b', commit_message):
                referenced = True
            # Pattern: task title substring (at least 5 chars to avoid accidental matches)
            elif len(task.title) >= 5 and task.title.lower() in commit_message.lower():
                referenced = True

            if referenced:
                task.status = 'DONE'
                task.save()
                completed.append(task)

        return completed

    @staticmethod
    def fetch_commits(project, max_commits=50):
        """
        Fetch commits from GitHub for the given project, store new ones, judge meaningfulness,
        and auto-complete tasks. Returns dict with counts.
        """
        if not project.github_token or not project.github_repo_owner or not project.github_repo_name:
            return {'error': 'GitHub not configured for this project', 'new': 0, 'tasks_completed': 0}

        owner = project.github_repo_owner
        repo = project.github_repo_name
        token = project.github_token

        # Fetch list of commits
        since_param = ''
        if project.last_commit_sync:
            since_param = f'&since={project.last_commit_sync.strftime("%Y-%m-%dT%H:%M:%SZ")}'

        commits_data = GitHubService._github_request(
            f'/repos/{owner}/{repo}/commits?per_page={max_commits}{since_param}',
            token
        )
        if commits_data is None:
            return {'error': 'Failed to fetch commits from GitHub', 'new': 0, 'tasks_completed': 0}
        if not isinstance(commits_data, list):
            return {'error': str(commits_data), 'new': 0, 'tasks_completed': 0}

        new_count = 0
        tasks_completed_count = 0
        existing_shas = set(
            CommitLog.objects.filter(project=project).values_list('commit_sha', flat=True)
        )

        for commit_data in reversed(commits_data):  # oldest first
            sha = commit_data.get('sha', '')
            if not sha or sha in existing_shas:
                continue

            # Fetch individual commit for stats
            detail = GitHubService._github_request(f'/repos/{owner}/{repo}/commits/{sha}', token)
            if detail is None:
                detail = commit_data

            stats = detail.get('stats', {})
            files = detail.get('files', [])
            stats['files'] = files  # inject files list into stats

            is_meaningful, trivial_reason = GitHubService.is_meaningful_commit(commit_data, stats)

            commit_info = commit_data.get('commit', {})
            author_info = commit_info.get('author', {})
            committer = (
                commit_data.get('author') or {}
            ).get('login') or author_info.get('name', 'Unknown')

            commit_time_str = author_info.get('date', '')
            from datetime import datetime
            try:
                commit_time = datetime.strptime(commit_time_str, '%Y-%m-%dT%H:%M:%SZ')
                from django.utils.timezone import make_aware
                commit_time = make_aware(commit_time)
            except Exception:
                commit_time = timezone.now()

            message = commit_info.get('message', '')
            html_url = commit_data.get('html_url', '')

            log = CommitLog.objects.create(
                project=project,
                commit_sha=sha,
                commit_message=message,
                commit_author=committer,
                commit_author_email=author_info.get('email', ''),
                branch='main',
                files_changed=len(files),
                lines_added=stats.get('additions', 0),
                lines_deleted=stats.get('deletions', 0),
                is_meaningful=is_meaningful,
                trivial_reason=trivial_reason,
                github_url=html_url,
                commit_time=commit_time,
            )
            new_count += 1
            existing_shas.add(sha)

            # Auto-complete tasks for all commits (meaningful or trivial)
            # Task references (#id or title) should always trigger completion
            completed = GitHubService.auto_complete_tasks(project, message, sha)
            for task in completed:
                log.task = task
                log.save(update_fields=['task'])
            tasks_completed_count += len(completed)

        # Update sync timestamp
        project.last_commit_sync = timezone.now()
        project.save(update_fields=['last_commit_sync'])

        return {
            'new': new_count,
            'tasks_completed': tasks_completed_count,
            'error': None
        }

    @staticmethod
    def create_github_repo(owner, repo_name, token, description='', private=False):
        """Create a new GitHub repo via API. Returns (html_url, error)."""
        import urllib.request, json, urllib.error
        url = 'https://api.github.com/user/repos'
        payload = json.dumps({
            'name': repo_name,
            'description': description,
            'private': private,
            'auto_init': True,
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, method='POST', headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
            'User-Agent': 'ProjectIntelligence/1.0',
        })
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data.get('html_url', ''), None
        except urllib.error.HTTPError as e:
            try:
                err_body = json.loads(e.read().decode('utf-8', errors='replace'))
                err_msg = err_body.get('message', str(e))
                errors = err_body.get('errors', [])
                if errors:
                    details = '; '.join(str(x.get('message', x)) for x in errors)
                    err_msg = f'{err_msg}: {details}'
            except Exception:
                err_msg = f'HTTP {e.code} error from GitHub'
            return '', err_msg
        except Exception as e:
            return '', str(e)


class ProjectIntelligenceService:
    
    @staticmethod
    def calculate_delay_prediction(task):
        delay_score = 0
        predicted_delay_days = 0
        
        if task.actual_hours > task.estimated_hours:
            overage = task.actual_hours - task.estimated_hours
            delay_score += min(overage / task.estimated_hours * 50, 50) if task.estimated_hours > 0 else 30
            predicted_delay_days += int(overage / 8)
        
        if task.status == 'BLOCKED':
            days_blocked = (timezone.now() - task.last_updated).days
            if days_blocked > 3:
                delay_score += min(days_blocked * 10, 40)
                predicted_delay_days += days_blocked
        
        days_since_update = (timezone.now() - task.last_updated).days
        if days_since_update > 5 and task.status not in ['DONE', 'BLOCKED']:
            delay_score += 20
            predicted_delay_days += max(0, days_since_update - 5)
        
        return {
            'task_id': task.id,
            'delay_score': min(delay_score, 100),
            'predicted_delay_days': predicted_delay_days,
            'risk_level': 'HIGH' if delay_score > 70 else 'MEDIUM' if delay_score > 40 else 'LOW'
        }
    
    @staticmethod
    def calculate_sprint_completion_probability(sprint):
        tasks = sprint.tasks.all()
        total_tasks = tasks.count()
        
        if total_tasks == 0:
            return 0.0
        
        completed_tasks = tasks.filter(status='DONE').count()
        in_progress_tasks = tasks.filter(status='IN_PROGRESS').count()
        blocked_tasks = tasks.filter(status='BLOCKED').count()
        
        days_remaining = (sprint.end_date - timezone.now().date()).days
        sprint_duration = (sprint.end_date - sprint.start_date).days
        progress_ratio = 1 - (days_remaining / sprint_duration) if sprint_duration > 0 else 1
        
        completion_rate = completed_tasks / total_tasks
        expected_completion = progress_ratio
        
        probability = (completion_rate / expected_completion * 100) if expected_completion > 0 else 0
        
        if blocked_tasks > 0:
            probability -= (blocked_tasks / total_tasks * 20)
        
        if in_progress_tasks > 0:
            avg_delay = ProjectIntelligenceService._calculate_avg_task_delay(sprint)
            if avg_delay > 2:
                probability -= min(avg_delay * 5, 30)
        
        return max(0, min(probability, 100))
    
    @staticmethod
    def _calculate_avg_task_delay(sprint):
        tasks = sprint.tasks.exclude(status='DONE')
        delay_sum = 0
        count = 0
        
        for task in tasks:
            if task.estimated_hours > 0 and task.actual_hours > task.estimated_hours:
                delay_sum += (task.actual_hours - task.estimated_hours) / 8
                count += 1
        
        return delay_sum / count if count > 0 else 0
    
    @staticmethod
    def calculate_project_risk_score(project):
        sprints = project.sprints.all()
        tasks = project.tasks.all()
        
        if tasks.count() == 0:
            return 0
        
        risk_score = 0
        
        blocked_tasks = tasks.filter(status='BLOCKED').count()
        total_tasks = tasks.count()
        blocked_ratio = blocked_tasks / total_tasks
        risk_score += blocked_ratio * 30
        
        overdue_tasks = 0
        for task in tasks.exclude(status='DONE'):
            if task.actual_hours > task.estimated_hours:
                overdue_tasks += 1
        
        overdue_ratio = overdue_tasks / total_tasks
        risk_score += overdue_ratio * 40
        
        stale_tasks = tasks.filter(
            last_updated__lt=timezone.now() - timedelta(days=5)
        ).exclude(status='DONE').count()
        stale_ratio = stale_tasks / total_tasks
        risk_score += stale_ratio * 30
        
        return min(risk_score, 100)
    
    @staticmethod
    def detect_workload_issues(user=None):
        overloaded_users = []
        
        users_to_check = [user] if user else User.objects.filter(role='EMPLOYEE')
        
        for emp in users_to_check:
            active_tasks = emp.assigned_tasks.filter(
                status__in=['TODO', 'IN_PROGRESS', 'BLOCKED']
            ).count()
            
            if active_tasks > 5:
                overloaded_users.append({
                    'user_id': emp.id,
                    'username': emp.username,
                    'active_tasks': active_tasks,
                    'overload_level': 'CRITICAL' if active_tasks > 8 else 'HIGH' if active_tasks > 6 else 'MEDIUM'
                })
        
        return overloaded_users
    
    @staticmethod
    def detect_blockers(project):
        alerts = []
        tasks = project.tasks.filter(status='BLOCKED')
        
        for task in tasks:
            days_blocked = (timezone.now() - task.last_updated).days
            
            if days_blocked > 3:
                severity = 'CRITICAL' if days_blocked > 7 else 'HIGH'
                message = f"Task '{task.title}' has been blocked for {days_blocked} days"
                
                alert, created = RiskAlert.objects.get_or_create(
                    project=project,
                    message=message,
                    defaults={'severity': severity}
                )
                
                if created:
                    alerts.append(alert)
        
        bug_keywords = {}
        commits = CommitLog.objects.filter(task__project=project)
        
        for commit in commits:
            words = commit.commit_message.lower().split()
            for word in words:
                if word in ['bug', 'error', 'fix', 'issue']:
                    bug_keywords[word] = bug_keywords.get(word, 0) + 1
        
        for keyword, count in bug_keywords.items():
            if count > 10:
                message = f"Keyword '{keyword}' repeated {count} times - possible systemic issue"
                alert, created = RiskAlert.objects.get_or_create(
                    project=project,
                    message=message,
                    defaults={'severity': 'MEDIUM'}
                )
                
                if created:
                    alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def analyze_sentiment(text):
        negative_keywords = ['stuck', 'urgent', 'delay', 'frustrated', 'issue', 'problem', 'blocked', 'crisis']
        positive_keywords = ['completed', 'done', 'success', 'finished', 'resolved', 'fixed']
        
        text_lower = text.lower()
        
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        
        sentiment_score = 50 + (positive_count * 10) - (negative_count * 10)
        sentiment_score = max(0, min(sentiment_score, 100))
        
        if sentiment_score < 30:
            sentiment = 'NEGATIVE'
        elif sentiment_score < 70:
            sentiment = 'NEUTRAL'
        else:
            sentiment = 'POSITIVE'
        
        return {
            'score': sentiment_score,
            'sentiment': sentiment,
            'negative_flags': negative_count,
            'positive_flags': positive_count
        }
    
    @staticmethod
    def calculate_performance_score(user):
        tasks = user.assigned_tasks.all()
        
        if tasks.count() == 0:
            return 50
        
        score = 0
        
        completed_tasks = tasks.filter(status='DONE')
        completion_rate = completed_tasks.count() / tasks.count()
        score += completion_rate * 40
        
        on_time_count = 0
        for task in completed_tasks:
            if task.actual_hours <= task.estimated_hours:
                on_time_count += 1
        
        on_time_rate = on_time_count / completed_tasks.count() if completed_tasks.count() > 0 else 0
        score += on_time_rate * 30
        
        blocked_tasks = tasks.filter(status='BLOCKED').count()
        blocked_penalty = (blocked_tasks / tasks.count()) * 20
        score -= blocked_penalty
        
        recent_tasks = tasks.filter(
            last_updated__gte=timezone.now() - timedelta(days=14)
        )
        
        if recent_tasks.count() > 0:
            consistency_score = min(recent_tasks.count() / 5, 1) * 30
            score += consistency_score
        
        return max(0, min(score, 100))
    
    @staticmethod
    def generate_manager_dashboard(manager):
        projects = manager.managed_projects.all()
        
        dashboard_data = {
            'projects': [],
            'overall_health': 0,
            'total_risk_alerts': 0,
            'overloaded_employees': [],
        }
        
        total_health = 0
        
        for project in projects:
            risk_score = ProjectIntelligenceService.calculate_project_risk_score(project)
            health_score = 100 - risk_score
            total_health += health_score
            
            sprints = project.sprints.all()
            sprint_data = []
            
            for sprint in sprints:
                completion_prob = ProjectIntelligenceService.calculate_sprint_completion_probability(sprint)
                sprint.completion_probability = completion_prob
                sprint.save()
                
                sprint_data.append({
                    'sprint_number': sprint.sprint_number,
                    'completion_probability': round(completion_prob, 2),
                    'start_date': sprint.start_date,
                    'end_date': sprint.end_date,
                })
            
            alerts = project.risk_alerts.filter(is_resolved=False)
            dashboard_data['total_risk_alerts'] += alerts.count()
            
            project_employees = User.objects.filter(
                assigned_tasks__project=project
            ).distinct()
            
            predicted_delays = []
            for task in project.tasks.exclude(status='DONE'):
                delay_info = ProjectIntelligenceService.calculate_delay_prediction(task)
                if delay_info['delay_score'] > 50:
                    predicted_delays.append(delay_info)
            
            # Get all tasks for the project
            tasks_data = []
            for task in project.tasks.all():
                tasks_data.append({
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'status': task.status,
                    'priority': task.priority,
                    'estimated_hours': task.estimated_hours,
                    'actual_hours': task.actual_hours,
                    'assigned_to': task.assigned_to.id if task.assigned_to else None,
                    'assigned_to_name': task.assigned_to.username if task.assigned_to else None,
                })
            
            # Get recent commits for this project
            recent_commits = []
            for c in project.commit_logs.order_by('-commit_time')[:10]:
                recent_commits.append({
                    'id': c.id,
                    'sha': c.commit_sha,
                    'short_sha': c.commit_sha[:7] if c.commit_sha else '',
                    'message': c.commit_message,
                    'author': c.commit_author,
                    'branch': c.branch,
                    'files_changed': c.files_changed,
                    'lines_added': c.lines_added,
                    'lines_deleted': c.lines_deleted,
                    'is_meaningful': c.is_meaningful,
                    'trivial_reason': c.trivial_reason,
                    'github_url': c.github_url,
                    'commit_time': c.commit_time.isoformat(),
                    'task_id': c.task_id,
                    'task_title': c.task.title if c.task else None,
                })

            dashboard_data['projects'].append({
                'id': project.id,
                'name': project.name,
                'health_score': round(health_score, 2),
                'risk_score': round(risk_score, 2),
                'sprints': sprint_data,
                'tasks': tasks_data,
                'active_alerts': list(alerts.values('id', 'message', 'severity', 'created_at')),
                'predicted_delays': predicted_delays[:5],
                'github_repo_url': project.github_repo_url,
                'github_repo_owner': project.github_repo_owner,
                'github_repo_name': project.github_repo_name,
                'last_commit_sync': project.last_commit_sync.isoformat() if project.last_commit_sync else None,
                'recent_commits': recent_commits,
            })
        
        dashboard_data['overall_health'] = round(total_health / projects.count(), 2) if projects.count() > 0 else 0
        
        overload_data = ProjectIntelligenceService.detect_workload_issues()
        dashboard_data['overloaded_employees'] = overload_data
        
        return dashboard_data
    
    @staticmethod
    def generate_employee_dashboard(employee):
        assigned_tasks = employee.assigned_tasks.all()
        
        active_tasks = assigned_tasks.filter(status__in=['TODO', 'IN_PROGRESS', 'BLOCKED'])
        completed_tasks = assigned_tasks.filter(status='DONE')
        
        performance_score = ProjectIntelligenceService.calculate_performance_score(employee)
        
        workload_status = 'NORMAL'
        if active_tasks.count() > 8:
            workload_status = 'CRITICAL'
        elif active_tasks.count() > 6:
            workload_status = 'HIGH'
        elif active_tasks.count() > 4:
            workload_status = 'ELEVATED'
        
        current_sprints = Sprint.objects.filter(
            tasks__assigned_to=employee,
            end_date__gte=timezone.now().date()
        ).distinct()
        
        sprint_info = []
        for sprint in current_sprints:
            sprint_info.append({
                'id': sprint.id,
                'project_name': sprint.project.name,
                'sprint_number': sprint.sprint_number,
                'end_date': sprint.end_date,
                'completion_probability': round(sprint.completion_probability, 2),
            })
        
        task_breakdown = {
            'TODO': active_tasks.filter(status='TODO').count(),
            'IN_PROGRESS': active_tasks.filter(status='IN_PROGRESS').count(),
            'BLOCKED': active_tasks.filter(status='BLOCKED').count(),
            'DONE': completed_tasks.count(),
        }
        
        return {
            'performance_score': round(performance_score, 2),
            'workload_status': workload_status,
            'active_tasks_count': active_tasks.count(),
            'completed_tasks_count': completed_tasks.count(),
            'task_breakdown': task_breakdown,
            'current_sprints': sprint_info,
            'assigned_tasks': [{
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'estimated_hours': task.estimated_hours,
                'actual_hours': task.actual_hours,
                'project_name': task.project.name,
            } for task in active_tasks],
        }
