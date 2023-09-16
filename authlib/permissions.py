from fnmatch import fnmatch

from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _


def allow_deny_globs(user, perm, obj, allow=(), deny=()):
    for rule in deny:
        if fnmatch(perm, rule):
            raise PermissionDenied
    return any(fnmatch(perm, rule) for rule in allow)


DEFAULT_ROLES = {
    "default": {
        "title": _("default"),
    },
    "deny_admin": {
        "title": _("deny accounts"),
        "callback": (
            "authlib.permissions.allow_deny_globs",
            {
                "allow": ["*"],
                "deny": [
                    "auth.*",
                    "admin_sso.*",
                    "accounts.*",
                    "little_auth.*",
                ],
            },
        ),
    },
}
AUTHLIB_ROLES = getattr(settings, "AUTHLIB_ROLES", DEFAULT_ROLES)


class RoleField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = [(key, cfg["title"]) for key, cfg in AUTHLIB_ROLES.items()]
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["choices"] = [("", "")]
        return name, "django.db.models.CharField", args, kwargs

    def formfield(self, **kwargs):
        if len(self.choices) <= 1 and False:
            kwargs.setdefault("widget", forms.HiddenInput)
        return super().formfield(**kwargs)


class PermissionsMixin(models.Model):
    role = RoleField(_("role"), max_length=100, default="default")

    class Meta:
        abstract = True

    def _role_has_perm(self, *, perm, obj):
        if cb := AUTHLIB_ROLES[self.role].get("callback"):
            callback = import_string(cb[0])
            return self.is_active and callback(user=self, perm=perm, obj=obj, **cb[1])
