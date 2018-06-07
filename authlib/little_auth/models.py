from django.db import models
from django.utils.translation import ugettext_lazy as _

from authlib.base import BaseUser


def _obfuscate(email):
    user, domain = email.rsplit("@", 1)
    return "%s%s@***.%s" % (
        user[:3],
        "***" if len(user) > 3 else "",
        domain.rsplit(".", 1)[-1],
    )


class User(BaseUser):
    full_name = models.CharField(_("full name"), max_length=200)

    class Meta(BaseUser.Meta):
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name or _obfuscate(self.email)

    def get_full_name(self):
        return self.__str__()

    def get_short_name(self):
        return self.__str__()
