from django.db import models
from django.conf import settings


class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Открыт"
        CLOSED = "closed", "Закрыт"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="participated_projects", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=6, choices=Status.choices, default=Status.OPEN)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]
