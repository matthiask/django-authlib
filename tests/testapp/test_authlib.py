from django.test import Client, TestCase
from django.utils.translation import deactivate_all

from authlib.little_auth.models import User


def zero_management_form_data(prefix):
    return {
        '%s-TOTAL_FORMS' % prefix: 0,
        '%s-INITIAL_FORMS' % prefix: 0,
        '%s-MIN_NUM_FORMS' % prefix: 0,
        '%s-MAX_NUM_FORMS' % prefix: 1000,
    }


def merge_dicts(*dicts):
    res = {}
    for d in dicts:
        res.update(d)
    return res


class Test(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            'admin@example.com', 'blabla')
        deactivate_all()

    def login(self):
        client = Client()
        client.force_login(self.user)
        return client

    def test_admin_oauth(self):
        client = Client()

        response = client.get('/admin/login/?next=/admin/little_auth/')
        self.assertContains(
            response,
            '<a href="/admin/__oauth__/?next=/admin/little_auth/">'
            'Log in using SSO</a>'
        )

        response = client.get('/admin/__oauth__/?next=/admin/little_auth/')
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            'https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
            '&client_id=empty&redirect_uri=',
            response['Location'],
        )
        self.assertEqual(
            client.session['admin-oauth-next'],
            '/admin/little_auth/',
        )
