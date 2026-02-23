from django.contrib.auth.models import (
    AbstractBaseUser, 
    PermissionsMixin, 
    BaseUserManager
)

from django.db import models
from django.utils import timezone

from django.core.validators import (
    MinValueValidator, 
    MaxValueValidator,
)

from gmp.usuarios.constants import (
    MAX_LENGTH_NOME,
    MAX_LENGTH_ROLE,
    MAX_LENGTH_QUEIXA,
    MAX_LENGTH_TELEFONE,
    MAX_LENGTH_ORIGEM,
    IDADE_MINIMA,
    IDADE_MAXIMA,
    UPLOAD_FOTO_PERFIL_PATH,
    LABEL_PACIENTE,
    LABEL_MEDICO,
    LABEL_SUPERADM,
    LABEL_QUEIXA_DEPRESSAO,
    LABEL_QUEIXA_ANSIEDADE,
    LABEL_QUEIXA_TAG,
    LABEL_QUEIXA_TOC,
    LABEL_QUEIXA_BIPOLARIDADE,
    LABEL_QUEIXA_ESQUIZOFRENIA,
    LABEL_QUEIXA_OUTROS,
    MSG_VALUE_ERROR_INFORME_EMAIL,
    MSG_VALUE_ERROR_SENHA_OBRIGATORIA,
    MSG_VALUE_ERROR_SUPERUSER_IS_STAFF,
    MSG_VALUE_ERROR_SUPERUSER_IS_SUPERUSER
)


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError(MSG_VALUE_ERROR_INFORME_EMAIL)

        if not password:
            raise ValueError(MSG_VALUE_ERROR_SENHA_OBRIGATORIA)

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
            raise ValueError(MSG_VALUE_ERROR_SUPERUSER_IS_STAFF)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(MSG_VALUE_ERROR_SUPERUSER_IS_SUPERUSER)

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
        (ROLE_PACIENTE, LABEL_PACIENTE),
        (ROLE_MEDICO, LABEL_MEDICO),
        (ROLE_SUPERADM, LABEL_SUPERADM),
    ]

    QUEIXA_DEPRESSAO = 'depressao'
    QUEIXA_ANSIEDADE = 'ansiedade'
    QUEIXA_TAG = 'tag'
    QUEIXA_TOC = 'toc'
    QUEIXA_BIPOLARIDADE = 'bipolaridade'
    QUEIXA_ESQUIZOFRENIA = 'esquizofrenia'
    QUEIXA_OUTROS = 'outros'

    QUEIXA_CHOICES = [
        (QUEIXA_DEPRESSAO, LABEL_QUEIXA_DEPRESSAO),
        (QUEIXA_ANSIEDADE, LABEL_QUEIXA_ANSIEDADE),
        (QUEIXA_TAG, LABEL_QUEIXA_TAG),
        (QUEIXA_TOC, LABEL_QUEIXA_TOC),
        (QUEIXA_BIPOLARIDADE, LABEL_QUEIXA_BIPOLARIDADE),
        (QUEIXA_ESQUIZOFRENIA, LABEL_QUEIXA_ESQUIZOFRENIA),
        (QUEIXA_OUTROS, LABEL_QUEIXA_OUTROS),
    ]

    nome = models.CharField(max_length=MAX_LENGTH_NOME, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    idade = models.PositiveIntegerField(validators=[MinValueValidator(IDADE_MINIMA), MaxValueValidator(IDADE_MAXIMA)], blank=True, null=True)
    queixa = models.CharField(max_length=MAX_LENGTH_QUEIXA, choices=QUEIXA_CHOICES, default=QUEIXA_DEPRESSAO, db_index=True)
    role = models.CharField(max_length=MAX_LENGTH_ROLE, choices=ROLE_CHOICES, default=ROLE_PACIENTE, db_index=True)
    telefone = models.CharField(max_length=MAX_LENGTH_TELEFONE, blank=True, null=True)
    origem = models.CharField(max_length=MAX_LENGTH_ORIGEM, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to=UPLOAD_FOTO_PERFIL_PATH, blank=True, null=True)

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

