from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from .managers import AccountManager


class Account(AbstractBaseUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    full_name = models.CharField(max_length=255)
    birthday = models.DateField()
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = AccountManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone", "full_name", "birthday"]

    class Meta:
        db_table = "accounts"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin
