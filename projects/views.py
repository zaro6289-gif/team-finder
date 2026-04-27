from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project

PROJECTS_PER_PAGE = 12


def project_list(request):
    projects = Project.objects.select_related("owner").prefetch_related("participants")
    paginator = Paginator(projects, PROJECTS_PER_PAGE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    return render(request, "projects/project_list.html", {"projects": page_obj})


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        id=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    if request.method != "POST":
        form = ProjectForm()
        return render(
            request, "projects/create-project.html", {"form": form, "is_edit": False}
        )

    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        messages.success(request, "Проект успешно создан!")
        return redirect("projects:detail", project_id=project.id)

    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        messages.error(request, "Вы не можете редактировать этот проект")
        return redirect("projects:detail", project_id=project_id)

    if request.method != "POST":
        form = ProjectForm(instance=project)
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": True, "project": project},
        )

    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        messages.success(request, "Проект успешно обновлен!")
        return redirect("projects:detail", project_id=project.id)

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True, "project": project},
    )


@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user in project.participants.all():
        project.participants.remove(request.user)
        is_participating = False
    else:
        project.participants.add(request.user)
        is_participating = True

    return JsonResponse(
        {
            "is_participating": is_participating,
            "participants_count": project.participants.count(),
        }
    )


@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if project.status != Project.Status.OPEN:
        return JsonResponse(
            {"status": "error", "message": "Проект уже завершён"}, status=400
        )

    project.status = Project.Status.CLOSED
    project.save()
    return JsonResponse({"status": "ok", "project_status": "closed"})
