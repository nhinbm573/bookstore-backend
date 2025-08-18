from django.contrib.auth.models import BaseUserManager


class AccountManager(BaseUserManager):
    def _create_user(self, email, phone, full_name, birthday, password, **extra_fields):
        """
        Create and save a user with the given email, phone, full_name, birthday and password.
        """
        if not email:
            raise ValueError("The Email field must be set")

        is_google_user = extra_fields.get("is_google_user", False)

        if not is_google_user:
            if not phone:
                raise ValueError("The Phone field must be set")
            if not birthday:
                raise ValueError("The Birthday field must be set")

        if not full_name:
            raise ValueError("The Full Name field must be set")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            phone=phone,
            full_name=full_name,
            birthday=birthday,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email,
        phone=None,
        full_name=None,
        birthday=None,
        password=None,
        **extra_fields,
    ):
        """Create and save a regular User with the given details."""
        extra_fields.setdefault("is_active", False)
        extra_fields.setdefault("is_admin", False)

        if extra_fields.get("is_admin"):
            raise ValueError("Regular user cannot have is_admin=True")

        return self._create_user(
            email, phone, full_name, birthday, password, **extra_fields
        )

    def create_superuser(
        self,
        email,
        phone=None,
        full_name=None,
        birthday=None,
        password=None,
        **extra_fields,
    ):
        """Create and save a SuperUser with the given details."""
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_admin", True)

        if not extra_fields.get("is_active"):
            raise ValueError("Superuser must have is_active=True")
        if not extra_fields.get("is_admin"):
            raise ValueError("Superuser must have is_admin=True")

        return self._create_user(
            email, phone, full_name, birthday, password, **extra_fields
        )
