from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from projects.models import Project

from .forms import EditProfileForm, LoginForm, RegisterForm
from .models import Skill, User

SKILLS_AUTOCOMPLETE_LIMIT = 10


def register(request):
    if request.method != "POST":
        form = RegisterForm()
        return render(request, "users/register.html", {"form": form})

    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("projects:list")

    return render(request, "users/register.html", {"form": form})


def user_login(request):
    if request.method != "POST":
        form = LoginForm()
        return render(request, "users/login.html", {"form": form})

    form = LoginForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect("projects:list")
        else:
            messages.error(request, "Неверный email или пароль")

    return render(request, "users/login.html", {"form": form})


@login_required
def user_logout(request):
    logout(request)
    return redirect("projects:list")


def user_detail(request, user_id):
    user_obj = get_object_or_404(
        User.objects.prefetch_related("skills", "owned_projects"), id=user_id
    )
    return render(request, "users/user-details.html", {"user": user_obj})


@login_required
def edit_profile(request):
    if request.method != "POST":
        form = EditProfileForm(instance=request.user)
        return render(
            request, "users/edit_profile.html", {"form": form, "user": request.user}
        )

    form = EditProfileForm(
        request.POST or None, request.FILES or None, instance=request.user
    )
    if form.is_valid():
        form.save()
        messages.success(request, "Профиль обновлен")
        return redirect("users:detail", user_id=request.user.id)

    return render(
        request, "users/edit_profile.html", {"form": form, "user": request.user}
    )


def user_list(request):
    users = User.objects.prefetch_related("skills")
    active_filter = request.GET.get("filter")
    active_skill = request.GET.get("skill")

    if request.user.is_authenticated:
        if active_filter == "owners-of-participating-projects":
            users = (
                User.objects.filter(owned_projects__participants=request.user)
                .distinct()
                .prefetch_related("skills")
            )
        elif active_filter == "participants-of-my-projects":
            my_projects = Project.objects.filter(owner=request.user)
            users = (
                User.objects.filter(participated_projects__in=my_projects)
                .distinct()
                .prefetch_related("skills")
            )

    if active_skill:
        users = users.filter(skills__name=active_skill)

    return render(
        request,
        "users/participants.html",
        {
            "participants": users,
            "active_filter": active_filter,
            "active_skill": active_skill,
            "all_skills": Skill.objects,
        },
    )


@login_required
def change_password(request):
    if request.method != "POST":
        return render(request, "users/change_password.html")

    new_password = request.POST.get("new_password1")
    if new_password:
        request.user.password = make_password(new_password)
        request.user.save()
        messages.success(request, "Пароль изменен")
        return redirect("users:detail", user_id=request.user.id)

    return render(request, "users/change_password.html")


def skill_autocomplete(request):
    q = request.GET.get("q", "")
    if len(q) < 1:
        return JsonResponse([], safe=False)
    skills = Skill.objects.filter(name__istartswith=q)[:SKILLS_AUTOCOMPLETE_LIMIT]
    data = [{"id": skill.id, "name": skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


@login_required
def add_user_skill(request, user_id):
    if request.user.id != user_id:
        return JsonResponse({"error": "Нет прав"}, status=403)

    user = get_object_or_404(User, id=user_id)
    skill_id = request.POST.get("skill_id")
    skill_name = request.POST.get("name")

    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    else:
        skill, created = Skill.objects.get_or_create(name=skill_name)

    if skill in user.skills.all():
        return JsonResponse({"added": False, "message": "Навык уже есть"})

    user.skills.add(skill)
    return JsonResponse(
        {
            "added": True,
            "skill_id": skill.id,
            "skill_name": skill.name,
            "created": skill_name is not None,
        }
    )


@login_required
def remove_user_skill(request, user_id, skill_id):
    if request.user.id != user_id:
        return JsonResponse({"error": "Нет прав"}, status=403)

    user = get_object_or_404(User, id=user_id)
    skill = get_object_or_404(Skill, id=skill_id)
    user.skills.remove(skill)
    return JsonResponse({"removed": True})
