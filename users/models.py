from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator
from .services import generate_avatar


class Skill(models.Model):
    name = models.CharField(max_length=124, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(
            email=email, name=name, surname=surname, phone=phone, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, name, surname, phone, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, name, surname, phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^(\+7|8)\d{10}$",
                message="Номер должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX",
            )
        ],
    )
    github_url = models.URLField(blank=True, null=True)
    about = models.TextField(max_length=256, blank=True)
    skills = models.ManyToManyField(Skill, related_name="users", blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.phone and self.phone.startswith("8"):
            self.phone = "+7" + self.phone[1:]

        if not self.avatar:
            self.avatar = generate_avatar(self.name, self.email)

        super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.name} {self.surname}"

    def __str__(self):
        return self.get_full_name()
