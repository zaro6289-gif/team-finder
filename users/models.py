from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator

from .services import generate_avatar

NAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256


class Skill(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH, unique=True, verbose_name="Название"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


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
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name="Имя")
    surname = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Аватар"
    )
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^(\+7|8)\d{10}$",
                message="Номер должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX",
            )
        ],
        verbose_name="Телефон",
    )
    github_url = models.URLField(blank=True, null=True, verbose_name="GitHub")
    about = models.TextField(
        max_length=ABOUT_MAX_LENGTH, blank=True, verbose_name="О себе"
    )
    skills = models.ManyToManyField(
        Skill, related_name="users", blank=True, verbose_name="Навыки"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    objects = UserManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

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
