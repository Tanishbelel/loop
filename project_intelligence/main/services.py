from datetime import timedelta
from django.utils import timezone
from django.db import models
from .models import Project, Sprint, Task, MicroTask, CommitLog, RiskAlert, User
import requests
import os
from .utils import GithubUtils
from dotenv import load_dotenv

load_dotenv()


# class ProjectIntelligenceService:
#
#     @staticmethod
#     def calculate_delay_prediction(task):
#         delay_score = 0
#         predicted_delay_days = 0
#
#         if task.actual_hours > task.estimated_hours:
#             overage = task.actual_hours - task.estimated_hours
#             delay_score += min(overage / task.estimated_hours * 50, 50) if task.estimated_hours > 0 else 30
#             predicted_delay_days += int(overage / 8)
#
#         if task.status == 'BLOCKED':
#             days_blocked = (timezone.now() - task.last_updated).days
#             if days_blocked > 3:
#                 delay_score += min(days_blocked * 10, 40)
#                 predicted_delay_days += days_blocked
#
#         days_since_update = (timezone.now() - task.last_updated).days
#         if days_since_update > 5 and task.status not in ['DONE', 'BLOCKED']:
#             delay_score += 20
#             predicted_delay_days += max(0, days_since_update - 5)
#
#         return {
#             'task_id': task.id,
#             'delay_score': min(delay_score, 100),
#             'predicted_delay_days': predicted_delay_days,
#             'risk_level': 'HIGH' if delay_score > 70 else 'MEDIUM' if delay_score > 40 else 'LOW'
#         }
#
#     @staticmethod
#     def calculate_sprint_completion_probability(sprint):
#         tasks = sprint.tasks.all()
#         total_tasks = tasks.count()
#
#         if total_tasks == 0:
#             return 0.0
#
#         completed_tasks = tasks.filter(status='DONE').count()
#         in_progress_tasks = tasks.filter(status='IN_PROGRESS').count()
#         blocked_tasks = tasks.filter(status='BLOCKED').count()
#
#         days_remaining = (sprint.end_date - timezone.now().date()).days
#         sprint_duration = (sprint.end_date - sprint.start_date).days
#         progress_ratio = 1 - (days_remaining / sprint_duration) if sprint_duration > 0 else 1
#
#         completion_rate = completed_tasks / total_tasks
#         expected_completion = progress_ratio
#
#         probability = (completion_rate / expected_completion * 100) if expected_completion > 0 else 0
#
#         if blocked_tasks > 0:
#             probability -= (blocked_tasks / total_tasks * 20)
#
#         if in_progress_tasks > 0:
#             avg_delay = ProjectIntelligenceService._calculate_avg_task_delay(sprint)
#             if avg_delay > 2:
#                 probability -= min(avg_delay * 5, 30)
#
#         return max(0, min(probability, 100))
#
#     @staticmethod
#     def _calculate_avg_task_delay(sprint):
#         tasks = sprint.tasks.exclude(status='DONE')
#         delay_sum = 0
#         count = 0
#
#         for task in tasks:
#             if task.estimated_hours > 0 and task.actual_hours > task.estimated_hours:
#                 delay_sum += (task.actual_hours - task.estimated_hours) / 8
#                 count += 1
#
#         return delay_sum / count if count > 0 else 0
#
#     @staticmethod
#     def calculate_project_risk_score(project):
#         sprints = project.sprints.all()
#         tasks = project.tasks.all()
#
#         if tasks.count() == 0:
#             return 0
#
#         risk_score = 0
#
#         blocked_tasks = tasks.filter(status='BLOCKED').count()
#         total_tasks = tasks.count()
#         blocked_ratio = blocked_tasks / total_tasks
#         risk_score += blocked_ratio * 30
#
#         overdue_tasks = 0
#         for task in tasks.exclude(status='DONE'):
#             if task.actual_hours > task.estimated_hours:
#                 overdue_tasks += 1
#
#         overdue_ratio = overdue_tasks / total_tasks
#         risk_score += overdue_ratio * 40
#
#         stale_tasks = tasks.filter(
#             last_updated__lt=timezone.now() - timedelta(days=5)
#         ).exclude(status='DONE').count()
#         stale_ratio = stale_tasks / total_tasks
#         risk_score += stale_ratio * 30
#
#         return min(risk_score, 100)
#
#     @staticmethod
#     def detect_workload_issues(user=None):
#         overloaded_users = []
#
#         users_to_check = [user] if user else User.objects.filter(role='EMPLOYEE')
#
#         for emp in users_to_check:
#             active_tasks = emp.assigned_tasks.filter(
#                 status__in=['TODO', 'IN_PROGRESS', 'BLOCKED']
#             ).count()
#
#             if active_tasks > 5:
#                 overloaded_users.append({
#                     'user_id': emp.id,
#                     'username': emp.username,
#                     'active_tasks': active_tasks,
#                     'overload_level': 'CRITICAL' if active_tasks > 8 else 'HIGH' if active_tasks > 6 else 'MEDIUM'
#                 })
#
#         return overloaded_users
#
#     @staticmethod
#     def detect_blockers(project):
#         alerts = []
#         tasks = project.tasks.filter(status='BLOCKED')
#
#         for task in tasks:
#             days_blocked = (timezone.now() - task.last_updated).days
#
#             if days_blocked > 3:
#                 severity = 'CRITICAL' if days_blocked > 7 else 'HIGH'
#                 message = f"Task '{task.title}' has been blocked for {days_blocked} days"
#
#                 alert, created = RiskAlert.objects.get_or_create(
#                     project=project,
#                     message=message,
#                     defaults={'severity': severity}
#                 )
#
#                 if created:
#                     alerts.append(alert)
#
#         bug_keywords = {}
#         commits = CommitLog.objects.filter(task__project=project)
#
#         for commit in commits:
#             words = commit.commit_message.lower().split()
#             for word in words:
#                 if word in ['bug', 'error', 'fix', 'issue']:
#                     bug_keywords[word] = bug_keywords.get(word, 0) + 1
#
#         for keyword, count in bug_keywords.items():
#             if count > 10:
#                 message = f"Keyword '{keyword}' repeated {count} times - possible systemic issue"
#                 alert, created = RiskAlert.objects.get_or_create(
#                     project=project,
#                     message=message,
#                     defaults={'severity': 'MEDIUM'}
#                 )
#
#                 if created:
#                     alerts.append(alert)
#
#         return alerts
#
#     @staticmethod
#     def analyze_sentiment(text):
#         negative_keywords = ['stuck', 'urgent', 'delay', 'frustrated', 'issue', 'problem', 'blocked', 'crisis']
#         positive_keywords = ['completed', 'done', 'success', 'finished', 'resolved', 'fixed']
#
#         text_lower = text.lower()
#
#         negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
#         positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
#
#         sentiment_score = 50 + (positive_count * 10) - (negative_count * 10)
#         sentiment_score = max(0, min(sentiment_score, 100))
#
#         if sentiment_score < 30:
#             sentiment = 'NEGATIVE'
#         elif sentiment_score < 70:
#             sentiment = 'NEUTRAL'
#         else:
#             sentiment = 'POSITIVE'
#
#         return {
#             'score': sentiment_score,
#             'sentiment': sentiment,
#             'negative_flags': negative_count,
#             'positive_flags': positive_count
#         }
#
#     @staticmethod
#     def calculate_performance_score(user):
#         tasks = user.assigned_tasks.all()
#
#         if tasks.count() == 0:
#             return 50
#
#         score = 0
#
#         completed_tasks = tasks.filter(status='DONE')
#         completion_rate = completed_tasks.count() / tasks.count()
#         score += completion_rate * 40
#
#         on_time_count = 0
#         for task in completed_tasks:
#             if task.actual_hours <= task.estimated_hours:
#                 on_time_count += 1
#
#         on_time_rate = on_time_count / completed_tasks.count() if completed_tasks.count() > 0 else 0
#         score += on_time_rate * 30
#
#         blocked_tasks = tasks.filter(status='BLOCKED').count()
#         blocked_penalty = (blocked_tasks / tasks.count()) * 20
#         score -= blocked_penalty
#
#         recent_tasks = tasks.filter(
#             last_updated__gte=timezone.now() - timedelta(days=14)
#         )
#
#         if recent_tasks.count() > 0:
#             consistency_score = min(recent_tasks.count() / 5, 1) * 30
#             score += consistency_score
#
#         return max(0, min(score, 100))
#
#     @staticmethod
#     def generate_manager_dashboard(manager):
#         projects = manager.managed_projects.all()
#
#         dashboard_data = {
#             'projects': [],
#             'overall_health': 0,
#             'total_risk_alerts': 0,
#             'overloaded_employees': [],
#         }
#
#         total_health = 0
#
#         for project in projects:
#             risk_score = ProjectIntelligenceService.calculate_project_risk_score(project)
#             health_score = 100 - risk_score
#             total_health += health_score
#
#             sprints = project.sprints.all()
#             sprint_data = []
#
#             for sprint in sprints:
#                 completion_prob = ProjectIntelligenceService.calculate_sprint_completion_probability(sprint)
#                 sprint.completion_probability = completion_prob
#                 sprint.save()
#
#                 sprint_data.append({
#                     'sprint_number': sprint.sprint_number,
#                     'completion_probability': round(completion_prob, 2),
#                     'start_date': sprint.start_date,
#                     'end_date': sprint.end_date,
#                 })
#
#             alerts = project.risk_alerts.filter(is_resolved=False)
#             dashboard_data['total_risk_alerts'] += alerts.count()
#
#             project_employees = User.objects.filter(
#                 assigned_tasks__project=project
#             ).distinct()
#
#             predicted_delays = []
#             for task in project.tasks.exclude(status='DONE'):
#                 delay_info = ProjectIntelligenceService.calculate_delay_prediction(task)
#                 if delay_info['delay_score'] > 50:
#                     predicted_delays.append(delay_info)
#
#             # Get all tasks for the project
#             tasks_data = []
#             for task in project.tasks.all():
#                 tasks_data.append({
#                     'id': task.id,
#                     'title': task.title,
#                     'description': task.description,
#                     'status': task.status,
#                     'priority': task.priority,
#                     'estimated_hours': task.estimated_hours,
#                     'actual_hours': task.actual_hours,
#                     'assigned_to': task.assigned_to.id if task.assigned_to else None,
#                     'assigned_to_name': task.assigned_to.username if task.assigned_to else None,
#                 })
#
#             dashboard_data['projects'].append({
#                 'id': project.id,
#                 'name': project.name,
#                 'health_score': round(health_score, 2),
#                 'risk_score': round(risk_score, 2),
#                 'sprints': sprint_data,
#                 'tasks': tasks_data,
#                 'active_alerts': list(alerts.values('id', 'message', 'severity', 'created_at')),
#                 'predicted_delays': predicted_delays[:5],
#             })
#
#         dashboard_data['overall_health'] = round(total_health / projects.count(), 2) if projects.count() > 0 else 0
#
#         overload_data = ProjectIntelligenceService.detect_workload_issues()
#         dashboard_data['overloaded_employees'] = overload_data
#
#         return dashboard_data
#
#     @staticmethod
#     def generate_employee_dashboard(employee):
#         assigned_tasks = employee.assigned_tasks.all()
#
#         active_tasks = assigned_tasks.filter(status__in=['TODO', 'IN_PROGRESS', 'BLOCKED'])
#         completed_tasks = assigned_tasks.filter(status='DONE')
#
#         performance_score = ProjectIntelligenceService.calculate_performance_score(employee)
#
#         workload_status = 'NORMAL'
#         if active_tasks.count() > 8:
#             workload_status = 'CRITICAL'
#         elif active_tasks.count() > 6:
#             workload_status = 'HIGH'
#         elif active_tasks.count() > 4:
#             workload_status = 'ELEVATED'
#
#         current_sprints = Sprint.objects.filter(
#             tasks__assigned_to=employee,
#             end_date__gte=timezone.now().date()
#         ).distinct()
#
#         sprint_info = []
#         for sprint in current_sprints:
#             sprint_info.append({
#                 'id': sprint.id,
#                 'project_name': sprint.project.name,
#                 'sprint_number': sprint.sprint_number,
#                 'end_date': sprint.end_date,
#                 'completion_probability': round(sprint.completion_probability, 2),
#             })
#
#         task_breakdown = {
#             'TODO': active_tasks.filter(status='TODO').count(),
#             'IN_PROGRESS': active_tasks.filter(status='IN_PROGRESS').count(),
#             'BLOCKED': active_tasks.filter(status='BLOCKED').count(),
#             'DONE': completed_tasks.count(),
#         }
#
#         return {
#             'performance_score': round(performance_score, 2),
#             'workload_status': workload_status,
#             'active_tasks_count': active_tasks.count(),
#             'completed_tasks_count': completed_tasks.count(),
#             'task_breakdown': task_breakdown,
#             'current_sprints': sprint_info,
#             'assigned_tasks': [{
#                 'id': task.id,
#                 'title': task.title,
#                 'description': task.description,
#                 'status': task.status,
#                 'priority': task.priority,
#                 'estimated_hours': task.estimated_hours,
#                 'actual_hours': task.actual_hours,
#                 'project_name': task.project.name,
#             } for task in active_tasks],
#         }


##################################
# Github Integration Services
###################################

class ProjectIntelligenceService:

    # =========================================================
    # Delay Prediction
    # =========================================================
    @staticmethod
    def calculate_delay_prediction(task):
        delay_score = 0
        predicted_delay_days = 0

        if task.estimated_hours > 0 and task.actual_hours > task.estimated_hours:
            overage = task.actual_hours - task.estimated_hours
            delay_score += min(overage / task.estimated_hours * 50, 50)
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
            "task_id": task.id,
            "delay_score": min(delay_score, 100),
            "predicted_delay_days": predicted_delay_days,
        }

    # =========================================================
    # Sprint Completion Probability
    # =========================================================
    @staticmethod
    def calculate_sprint_completion_probability(sprint):

        tasks = sprint.tasks.all()
        total_tasks = tasks.count()

        if total_tasks == 0:
            return 0

        completed_tasks = tasks.filter(status='DONE').count()
        blocked_tasks = tasks.filter(status='BLOCKED').count()

        days_remaining = (sprint.end_date - timezone.now().date()).days
        sprint_duration = (sprint.end_date - sprint.start_date).days or 1

        progress_ratio = 1 - (days_remaining / sprint_duration)
        completion_rate = completed_tasks / total_tasks

        probability = completion_rate / progress_ratio * 100 if progress_ratio > 0 else 0

        if blocked_tasks > 0:
            probability -= blocked_tasks / total_tasks * 20

        return max(0, min(probability, 100))

    # =========================================================
    # Project Risk Score
    # =========================================================
    @staticmethod
    def calculate_project_risk_score(project):

        # ✅ FIXED: project.tasks relation
        tasks = Task.objects.filter(project=project)

        if not tasks.exists():
            return 0

        total = tasks.count()

        blocked_ratio = tasks.filter(status='BLOCKED').count() / total

        overdue_ratio = tasks.filter(
            actual_hours__gt=models.F("estimated_hours")
        ).count() / total

        stale_ratio = tasks.filter(
            last_updated__lt=timezone.now() - timedelta(days=5)
        ).exclude(status='DONE').count() / total

        return min((blocked_ratio * 30 + overdue_ratio * 40 + stale_ratio * 30), 100)

    # =========================================================
    # Workload Detection
    # =========================================================
    @staticmethod
    def detect_workload_issues(user=None):

        users = [user] if user else User.objects.filter(role='EMPLOYEE')
        overloaded = []

        for emp in users:

            # ✅ FIXED: workload must be based on MicroTask.developer
            active_microtasks = MicroTask.objects.filter(
                developer=emp,
                status__in=['TODO', 'IN_PROGRESS', 'BLOCKED']
            ).count()

            if active_microtasks > 5:
                overloaded.append({
                    "user": emp.username,
                    "active_microtasks": active_microtasks,
                })

        return overloaded

    # =========================================================
    # Blocker Detection
    # =========================================================
    @staticmethod
    def detect_blockers(project):

        alerts = []

        # ✅ FIXED: correct relation
        tasks = Task.objects.filter(project=project, status='BLOCKED')

        for task in tasks:
            days_blocked = (timezone.now() - task.last_updated).days

            if days_blocked > 3:
                message = f"Task '{task.title}' blocked for {days_blocked} days"

                alert, created = RiskAlert.objects.get_or_create(
                    project=project,
                    message=message,
                    defaults={"severity": "HIGH"}
                )

                if created:
                    alerts.append(alert)

        # commit keyword analysis
        commits = CommitLog.objects.filter(task__project=project)

        keyword_count = {}
        for commit in commits:
            for word in commit.commit_message.lower().split():
                if word in ['bug', 'error', 'fix', 'issue']:
                    keyword_count[word] = keyword_count.get(word, 0) + 1

        for k, v in keyword_count.items():
            if v > 10:
                alert, created = RiskAlert.objects.get_or_create(
                    project=project,
                    message=f"Repeated keyword '{k}' seen {v} times",
                    defaults={"severity": "MEDIUM"}
                )
                if created:
                    alerts.append(alert)

        return alerts

    # =========================================================
    # Performance Score
    # =========================================================
    @staticmethod
    def calculate_performance_score(user):

        # ✅ FIXED: use MicroTasks not assigned_tasks
        mts = MicroTask.objects.filter(developer=user)

        if not mts.exists():
            return 50

        total = mts.count()
        done = mts.filter(status='DONE').count()

        completion_rate = done / total

        on_time = mts.filter(
            status='DONE',
            actual_minutes__lte=models.F("estimated_minutes")
        ).count()

        on_time_rate = on_time / done if done else 0

        blocked_penalty = mts.filter(status='BLOCKED').count() / total

        score = completion_rate * 50 + on_time_rate * 30 - blocked_penalty * 20
        return max(0, min(score * 100, 100))

    # =========================================================
    # Manager Dashboard
    # =========================================================
    @staticmethod
    def generate_manager_dashboard(manager):

        projects = Project.objects.filter(manager=manager)
        data = []

        for project in projects:

            risk = ProjectIntelligenceService.calculate_project_risk_score(project)

            # ✅ FIXED: sprints via phase
            sprints = Sprint.objects.filter(phase__project=project)

            sprint_data = [
                {"sprint": s.sprint_number, "end": s.end_date}
                for s in sprints
            ]

            # ✅ FIXED: employees via microtasks
            employees = User.objects.filter(
                micro_tasks__task__project=project
            ).distinct()

            data.append({
                "project": project.name,
                "risk": risk,
                "employees": employees.count(),
                "sprints": sprint_data,
            })

        return data

    # =========================================================
    # Employee Dashboard
    # =========================================================
    @staticmethod
    def generate_employee_dashboard(employee):

        # ✅ FIXED: use MicroTasks
        mts = MicroTask.objects.filter(developer=employee)

        active = mts.filter(status__in=['TODO', 'IN_PROGRESS', 'BLOCKED'])
        done = mts.filter(status='DONE')

        # ✅ FIXED: find sprints correctly
        sprints = Sprint.objects.filter(
            tasks__micro_tasks__developer=employee
        ).distinct()

        return {
            "active_microtasks": active.count(),
            "completed_microtasks": done.count(),
            "performance": ProjectIntelligenceService.calculate_performance_score(employee),
            "current_sprints": [
                {
                    "sprint": s.sprint_number,
                    "phase": s.phase.name,
                    "project": s.phase.project.name,
                }
                for s in sprints
            ]
        }

class GithubAPIError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class GithubServices:
    """
    All GitHub repo + webhook services
    """

    def __init__(self, org_name: str, installation_id: str):
        self.installation_id = installation_id
        self.utils = GithubUtils()

        self.org = org_name
        self.webhook_url = os.getenv("GITHUB_WEBHOOK_URL")
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")

        if not self.org:
            raise Exception("Missing GITHUB_ORG env")

    # ------------------------------
    # Base Request
    # ------------------------------
    def _headers(self):
        token = self.utils.get_installation_token(self.installation_id)
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

    def _request(self, method, url, **kwargs):
        response = requests.request(method, url, headers=self._headers(), **kwargs)

        if not response.ok:
            try:
                msg = response.json().get("message", response.text)
            except Exception:
                msg = response.text

            raise GithubAPIError(response.status_code, msg)

        return response.json() if response.content else None

    # ====================================================
    # REPOSITORY SERVICES
    # ====================================================
    def create_repository(self, repo_name: str, private=True):
        url = f"https://api.github.com/orgs/{self.org}/repos"

        data = {
            "name": repo_name,
            "private": private,
            "auto_init": True
        }

        return self._request("POST", url, json=data)

    def list_repositories(self):
        url = f"https://api.github.com/orgs/{self.org}/repos"
        return self._request("GET", url)

    # ====================================================
    # WEBHOOK SERVICES
    # ====================================================
    def create_webhook(self, repo_name: str):
        url = f"https://api.github.com/repos/{self.org}/{repo_name}/hooks"

        data = {
            "name": "web",
            "active": True,
            "events": ["push", "pull_request", "issues"],
            "config": {
                "url": self.webhook_url,
                "content_type": "json",
                "secret": self.webhook_secret
            }
        }

        return self._request("POST", url, json=data)

        # --------------------------------------------------
        # ARCHIVE REPO (Soft Delete Step 1)
        # --------------------------------------------------

    def archive_repository(self, repo_name: str, owner: str = None):

        owner = owner or self.org
        url = f"https://api.github.com/repos/{owner}/{repo_name}"

        data = {"archived": True}

        response = self._request("PATCH", url, json=data)
        print(response)

        return response

        # --------------------------------------------------
        # DELETE REPO (Final Step)
        # --------------------------------------------------

    def delete_repository(self, repo_name: str, owner: str = None):
        owner = owner or self.org
        url = f"https://api.github.com/repos/{owner}/{repo_name}"

        response = self._request("DELETE", url)
        print(response)

        return response

        # --------------------------------------------------
        # SAFE DELETE FLOW
        # --------------------------------------------------

    def safe_delete_repository(self, repo_name: str, owner: str = None):
        """
        Archive first before deletion.
        """
        owner = owner or self.org

        # Step 1 archive
        self.archive_repository(repo_name, owner)

        return {
            "message": "Repository archived. Confirm delete to permanently remove."
        }

    # ====================================================
    # GENERIC API CALL
    # ====================================================
    def github_api(self, method: str, path: str, **kwargs):
        """
        Example:
        github_api("GET", "/repos/org/repo/commits")
        """
        url = f"https://api.github.com{path}"
        return self._request(method, url, **kwargs)
