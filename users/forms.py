from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Skill
from .validators import normalize_phone


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "name", "surname", "phone", "password1", "password2")

    def clean_phone(self):
        return normalize_phone(self.cleaned_data.get("phone"))


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class EditProfileForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "skills-select"}),
        label="Навыки",
    )

    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url", "skills")

    def clean_phone(self):
        return normalize_phone(self.cleaned_data.get("phone"))
