from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.utils import timezone
import json

from .models import Project, Task
from django.contrib.auth.models import User

# ---------------- PROJECTS ----------------
@login_required
@csrf_exempt
@require_http_methods(["GET", "POST"])
def projects(request):
    if request.method == "GET":
        projects = Project.objects.filter(owner=request.user)
        search = request.GET.get('search')
        if search:
            projects = projects.filter(name__icontains=search)
        data = [{"id": p.id, "name": p.name, "description": p.description} for p in projects]
        return JsonResponse({"projects": data}, status=200)

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        if not name:
            return JsonResponse({"error": "Project name is required"}, status=400)
        try:
            project = Project.objects.create(name=name, description=description, owner=request.user)
        except IntegrityError:
            return JsonResponse({"error": "Project already exists"}, status=400)
        return JsonResponse({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "owner": project.owner.username
        }, status=201)

# ---------------- TASKS ----------------
@login_required
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def tasks(request, task_id=None):
    if request.method == "GET":
        # List all tasks for the user (owned projects or assigned)
        tasks = Task.objects.filter(project__owner=request.user) | Task.objects.filter(assignee=request.user)
        project_id = request.GET.get('project')
        if project_id:
            tasks = tasks.filter(project_id=project_id)
        data = [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "due_date": t.due_date,
                "project": t.project.name,
                "assignee": t.assignee.username if t.assignee else None
            } for t in tasks.distinct()
        ]
        return JsonResponse({"tasks": data}, status=200)

    if request.method == "POST":
        body = json.loads(request.body)
        title = body.get("title")
        project_id = body.get("project_id")
        description = body.get("description", "")
        priority = body.get("priority", 3)
        status = body.get("status", "todo")
        due_date = body.get("due_date")
        assignee_id = body.get("assignee_id")

        if not title or not project_id:
            return JsonResponse({"error": "Title and project_id are required"}, status=400)

        try:
            project = Project.objects.get(id=project_id, owner=request.user)
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project not found or not owned by you"}, status=404)

        assignee = None
        if assignee_id:
            try:
                assignee = User.objects.get(id=assignee_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "Assignee not found"}, status=404)

        task = Task(
            title=title,
            description=description,
            project=project,
            priority=priority,
            status=status,
            assignee=assignee
        )
        if due_date:
            task.due_date = due_date
        try:
            task.full_clean()
            task.save()
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

        return JsonResponse({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "project": task.project.name,
            "assignee": task.assignee.username if task.assignee else None
        }, status=201)

    # ---------------- UPDATE or DELETE ----------------
    if task_id:
        try:
            task = Task.objects.get(id=task_id, project__owner=request.user)
        except Task.DoesNotExist:
            return JsonResponse({"error": "Task not found"}, status=404)

        if request.method == "PUT":
            body = json.loads(request.body)
            for field in ["title", "description", "status", "priority", "due_date", "assignee_id"]:
                if field in body:
                    if field == "assignee_id":
                        if body[field]:
                            try:
                                task.assignee = User.objects.get(id=body[field])
                            except User.DoesNotExist:
                                return JsonResponse({"error": "Assignee not found"}, status=404)
                        else:
                            task.assignee = None
                    elif field == "due_date":
                        task.due_date = body[field]
                    else:
                        setattr(task, field, body[field])
            try:
                task.full_clean()
                task.save()
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)
            return JsonResponse({"success": "Task updated"}, status=200)

        if request.method == "DELETE":
            task.delete()
            return JsonResponse({"success": "Task deleted"}, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)
