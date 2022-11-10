from django.db import models
from django.contrib.auth.models import AbstractUser


class User (AbstractUser):

    first_name = models.CharField(
        max_length=80,
        verbose_name="Fornavn"
    )

    last_name = models.CharField(
        max_length=80,
        verbose_name="Etternavn"
    )

    email = models.CharField(
        max_length=80,
        verbose_name="E-post",
        unique=True
    )

    allergies = models.CharField(
        max_length=100,
        verbose_name="Allergier",
        blank=True
    )

    starting_year = models.CharField(
        verbose_name="År startet",
        max_length=4
    )

    is_awaiting_approval = models.BooleanField(
        verbose_name="Avventer godkjenning",
        default=True
    )

    account_verified = models.BooleanField(
        verbose_name="Verifisert konto (e-post)",
        default=False
    )

    class Meta:
        permissions = (
            ("can_view_users", "Can view users awaiting checkup for registration"),
            ("can_change_users", "Can change user status during checkup for registration"),
        )