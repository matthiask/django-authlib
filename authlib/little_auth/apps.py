from django.apps import AppConfig
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _


class LittleAuthConfig(AppConfig):
    name = "authlib.little_auth"
    verbose_name = capfirst(_("Authentication"))
