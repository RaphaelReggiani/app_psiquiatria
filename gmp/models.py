from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, role='paciente', **extra_fields):
        if not email:
            raise ValueError("Informe um e-mail.")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(
            email=email,
            password=password,
            role='superadm',
            **extra_fields
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ('paciente', 'Paciente'),
        ('medico', 'Médico'),
        ('superadm', 'Super Administrador'),
    ]

    nome = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='paciente')

    telefone = models.CharField(max_length=20, blank=True, null=True)
    origem = models.CharField(max_length=50, blank=True)
    foto_perfil = models.ImageField(upload_to='foto_perfil/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if self.role == 'superadm':
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"
