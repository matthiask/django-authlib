from django.db import models
from django.utils.translation import ugettext_lazy as _

from authlib.base import BaseUser


class User(BaseUser):
    full_name = models.CharField(
        _('full name'),
        max_length=200,
    )

    class Meta(BaseUser.Meta):
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name
