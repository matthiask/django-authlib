from django.db import models
from django.utils.translation import gettext_lazy as _

from authlib.base_user import BaseUser
from authlib.roles import RoleField


def _obfuscate(email):
    user, _sep, domain = email.partition("@")
    keep = 3
    return (
        "{}{}@***.{}".format(
            user[:keep],
            "***" if len(user) > keep else "",
            domain.rsplit(".", 1)[-1],
        )
        if domain
        else f"{user[:3]}***"
    )


class User(BaseUser):
    full_name = models.CharField(_("full name"), max_length=200)
    role = RoleField()

    class Meta(BaseUser.Meta):
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name or _obfuscate(self.email)

    def get_full_name(self):
        return self.__str__()

    def get_short_name(self):
        return self.__str__()
