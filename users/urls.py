from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.user_logout, name="logout"),
    path("<int:user_id>/", views.user_detail, name="detail"),
    path("list/", views.user_list, name="list"),
    path("edit-profile/", views.edit_profile, name="edit"),
    path("change-password/", views.change_password, name="change_password"),
    path("skills/autocomplete/", views.skill_autocomplete, name="skill_autocomplete"),
    path("<int:user_id>/skills/add/", views.add_user_skill, name="add_skill"),
    path(
        "<int:user_id>/skills/<int:skill_id>/remove/",
        views.remove_user_skill,
        name="remove_skill",
    ),
]
