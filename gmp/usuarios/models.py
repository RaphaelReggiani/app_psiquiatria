from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError("Informe um e-mail.")

        if not password:
            raise ValueError("Senha é obrigatória.")

        email = self.normalize_email(email)

        if role is None:
            role = self.model.ROLE_PACIENTE

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

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser precisa ter is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser precisa ter is_superuser=True.")

        return self.create_user(
            email=email,
            password=password,
            role=CustomUser.ROLE_SUPERADM,
            **extra_fields
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):

    ROLE_PACIENTE = 'paciente'
    ROLE_MEDICO = 'medico'
    ROLE_SUPERADM = 'superadm'

    ROLE_CHOICES = [
        (ROLE_PACIENTE, 'Paciente'),
        (ROLE_MEDICO, 'Médico'),
        (ROLE_SUPERADM, 'Super Administrador'),
    ]

    QUEIXA_DEPRESSAO = 'depressao'
    QUEIXA_ANSIEDADE = 'ansiedade'
    QUEIXA_TAG = 'tag'
    QUEIXA_TOC = 'toc'
    QUEIXA_BIPOLARIDADE = 'bipolaridade'
    QUEIXA_ESQUIZOFRENIA = 'esquizofrenia'
    QUEIXA_OUTROS = 'outros'

    QUEIXA_CHOICES = [
        (QUEIXA_DEPRESSAO, 'Depressão'),
        (QUEIXA_ANSIEDADE, 'Ansiedade'),
        (QUEIXA_TAG, 'TAG'),
        (QUEIXA_TOC, 'TOC'),
        (QUEIXA_BIPOLARIDADE, 'Bipolaridade'),
        (QUEIXA_ESQUIZOFRENIA, 'Esquizofrenia'),
        (QUEIXA_OUTROS, 'Outros'),
    ]

    nome = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    idade = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(85)], blank=True, null=True)
    queixa = models.CharField(max_length=30, choices=QUEIXA_CHOICES, default=QUEIXA_DEPRESSAO, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PACIENTE, db_index=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    origem = models.CharField(max_length=50, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='foto_perfil/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):

        if self.email:
            self.email = CustomUser.objects.normalize_email(self.email).lower()

        if self.role == self.ROLE_SUPERADM:
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_superuser = False
            self.is_staff = False

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome if self.nome else self.email

