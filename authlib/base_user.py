from django.contrib.auth import models as auth_models
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseUserManager(auth_models.BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Email missing")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class BaseUser(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField(_("email"), max_length=254, unique=True)
    is_active = models.BooleanField(_("is active"), default=True)
    is_staff = models.BooleanField(
        _("is staff"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = BaseUserManager()

    class Meta:
        abstract = True
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email
