import os
import time
import jwt
import requests
from threading import Lock
from dotenv import load_dotenv
from django.db.models import Sum, Count
from .models import Project, Phase, Sprint, Task, MicroTask
load_dotenv()

class GithubUtils:
    """
    Utility class for GitHub App authentication
    """

    _token_cache = {}
    _lock = Lock()

    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID")
        pem_path = os.getenv("GITHUB_PRIVATE_KEY_PATH")

        with open(pem_path, "r") as f:
            self.private_key = f.read()

        if not self.app_id or not self.private_key:
            raise Exception("Missing GitHub App environment variables")

        self.private_key = self.private_key.replace("\\n", "\n")

    # ------------------------------
    # Generate JWT
    # ------------------------------
    def _generate_jwt(self):
        now = int(time.time())

        payload = {
            "iat": now - 60,  # allow small clock drift
            "exp": now + 540,  # must be <= 10 min
            "iss": self.app_id
        }

        return jwt.encode(payload, self.private_key, algorithm="RS256")

    # ------------------------------
    # Get Installation Token
    # ------------------------------
    def get_installation_token(self, installation_id: str):

        with self._lock:
            cached = self._token_cache.get(installation_id)

            if cached and cached["expires_at"] > time.time():
                return cached["token"]

            jwt_token = self._generate_jwt()

            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json"
            }

            url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

            response = requests.post(url, headers=headers)

            if response.status_code != 201:
                raise Exception(f"GitHub token error: {response.text}")

            data = response.json()

            token = data["token"]
            expires_at = time.time() + 3500  # ~1 hour minus buffer

            self._token_cache[installation_id] = {
                "token": token,
                "expires_at": expires_at
            }

            return token

class AnalyticsUtils:

    # =========================================================
    # 1️⃣ MicroTask Completion for a Task
    # =========================================================
    @staticmethod
    def microtask_completion(task: Task) -> float:
        mts = task.micro_tasks.all()

        total = sum(mt.estimated_minutes for mt in mts) or 1
        done = sum(mt.estimated_minutes for mt in mts if mt.status == "DONE")

        return round(done / total * 100, 2)

    # =========================================================
    # 2️⃣ Task Completion for a Sprint
    # =========================================================
    @staticmethod
    def sprint_task_completion(sprint: Sprint) -> float:
        tasks = sprint.tasks.all()

        if not tasks:
            return 0.0

        return round(
            sum(AnalyticsUtils.microtask_completion(t) for t in tasks) / len(tasks),
            2
        )

    # =========================================================
    # 3️⃣ Sprint Completion for a Phase
    # =========================================================
    @staticmethod
    def phase_sprint_completion(phase: Phase) -> float:
        sprints = phase.sprints.all()

        if not sprints:
            return 0.0

        return round(
            sum(AnalyticsUtils.sprint_task_completion(s) for s in sprints) / len(sprints),
            2
        )

    # =========================================================
    # 4️⃣ Phase Completion for a Project
    # =========================================================
    @staticmethod
    def project_phase_completion(project: Project) -> float:
        phases = project.phases.all()

        if not phases:
            return 0.0

        return round(
            sum(AnalyticsUtils.phase_sprint_completion(p) for p in phases) / len(phases),
            2
        )

    # =========================================================
    # 5️⃣ Project Metrics Summary
    # =========================================================
    @staticmethod
    def project_metrics(project: Project) -> dict:
        completion = AnalyticsUtils.project_phase_completion(project)

        total_tasks = project.tasks.count()
        done_tasks = project.tasks.filter(status="DONE").count()

        total_microtasks = MicroTask.objects.filter(task__project=project).count()
        done_microtasks = MicroTask.objects.filter(
            task__project=project,
            status="DONE"
        ).count()

        return {
            "project_id": project.id,
            "project_name": project.name,
            "completion_percent": completion,
            "total_tasks": total_tasks,
            "completed_tasks": done_tasks,
            "total_microtasks": total_microtasks,
            "completed_microtasks": done_microtasks,
        }

    # =========================================================
    # 6️⃣ Phase Metrics
    # =========================================================
    @staticmethod
    def phase_metrics(phase: Phase) -> dict:
        completion = AnalyticsUtils.phase_sprint_completion(phase)

        total_tasks = Task.objects.filter(sprint__phase=phase).count()
        done_tasks = Task.objects.filter(
            sprint__phase=phase,
            status="DONE"
        ).count()

        return {
            "phase": phase.name,
            "completion_percent": completion,
            "total_tasks": total_tasks,
            "completed_tasks": done_tasks,
        }

    # =========================================================
    # 7️⃣ Sprint Metrics
    # =========================================================
    @staticmethod
    def sprint_metrics(sprint: Sprint) -> dict:
        completion = AnalyticsUtils.sprint_task_completion(sprint)

        total_tasks = sprint.tasks.count()
        done_tasks = sprint.tasks.filter(status="DONE").count()

        return {
            "sprint": sprint.sprint_number,
            "completion_percent": completion,
            "total_tasks": total_tasks,
            "completed_tasks": done_tasks,
        }

    # =========================================================
    # 8️⃣ Employee Performance
    # =========================================================
    @staticmethod
    def employee_performance(user_id: int) -> dict:
        mts = MicroTask.objects.filter(developer_id=user_id)

        total = mts.count()
        done = mts.filter(status="DONE").count()

        total_minutes = mts.aggregate(total=Sum("estimated_minutes"))["total"] or 0
        done_minutes = mts.filter(status="DONE").aggregate(
            total=Sum("estimated_minutes")
        )["total"] or 0

        completion = (done_minutes / total_minutes * 100) if total_minutes else 0

        return {
            "total_microtasks": total,
            "completed_microtasks": done,
            "completion_percent": round(completion, 2),
            "total_minutes": total_minutes,
            "completed_minutes": done_minutes,
        }

    # =========================================================
    # 9️⃣ Manager Dashboard Metrics
    # =========================================================
    @staticmethod
    def manager_dashboard(manager) -> list:
        projects = Project.objects.filter(manager=manager)

        return [
            AnalyticsUtils.project_metrics(p)
            for p in projects
        ]
