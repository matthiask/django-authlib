from functools import partial

from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import deactivate_all, gettext_lazy as _

from authlib.little_auth.models import User
from authlib.roles import allow_deny_globs


@override_settings(
    AUTHLIB_ROLES={
        "default": {
            "title": _("default"),
        },
        "deny_accounts": {
            "title": _("deny accounts"),
            "callback": partial(
                allow_deny_globs,
                allow={"*"},
                deny={
                    "auth.*",
                    "admin_sso.*",
                    "accounts.*",
                    "little_auth.*",
                },
            ),
        },
    }
)
class Test(TestCase):
    def setUp(self):
        deactivate_all()

    def test_roles(self):
        superuser = User.objects.create_superuser(
            "admin@example.com",
            "blabla",
        )
        staff_default = User.objects.create(
            email="staff1@example.com",
            is_staff=True,
            role="default",
        )
        staff_no_accounts = User.objects.create(
            email="staff2@example.com",
            is_staff=True,
            role="deny_accounts",
        )

        self.assertTrue(superuser.has_perm("little_auth.change_user"))
        self.assertFalse(staff_default.has_perm("little_auth.change_user"))
        self.assertFalse(staff_no_accounts.has_perm("little_auth.change_user"))

        self.assertTrue(superuser.has_perm("sessions.change_session"))
        self.assertFalse(staff_default.has_perm("sessions.change_session"))
        # Everything allowed except a particular list of apps
        self.assertTrue(staff_no_accounts.has_perm("sessions.change_session"))

        self.assertTrue(staff_default.get_all_permissions() <= set())
        self.assertTrue(
            staff_no_accounts.get_all_permissions()
            >= {
                "admin.add_logentry",
                "admin.change_logentry",
                "admin.delete_logentry",
                "admin.view_logentry",
                "contenttypes.add_contenttype",
                "contenttypes.change_contenttype",
                "contenttypes.delete_contenttype",
                "contenttypes.view_contenttype",
                "sessions.add_session",
                "sessions.change_session",
                "sessions.delete_session",
                "sessions.view_session",
            }
        )

    def test_unknown_role(self):
        unknown = User.objects.create(
            email="unknown@example.com",
            role="unknown",
        )
        self.assertFalse(unknown.has_perm("sessions.change_session"))
