from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Skill


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "name", "surname", "phone", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "skills")
    search_fields = ("email", "name", "surname", "phone")
    readonly_fields = ("created_at",)
    filter_horizontal = ("skills", "groups", "user_permissions")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личная информация",
            {
                "fields": (
                    "name",
                    "surname",
                    "avatar",
                    "phone",
                    "github_url",
                    "about",
                    "skills",
                )
            },
        ),
        ("Статусы", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Даты", {"fields": ("created_at",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "phone",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    ordering = ("email",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
