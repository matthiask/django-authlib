from contextlib import contextmanager

from django.test import Client, TestCase
from django.utils.translation import deactivate_all

from authlib.admin_oauth import views as admin_oauth_views
from authlib.facebook import FacebookOAuth2Client
from authlib.little_auth.models import User


def mock_admin_oauth_client(user_data, module, client):
    class mock(object):
        def __init__(self, request):
            pass

        def get_user_data(self):
            return user_data

    @contextmanager
    def manager():
        orig = getattr(module, client)
        setattr(module, client, mock)
        yield
        setattr(module, client, orig)

    return manager()


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

        with mock_admin_oauth_client(
                user_data={'email': 'blaaa@example.com'},
                module=admin_oauth_views,
                client='GoogleOAuth2Client',
        ):
            response = client.get('/admin/__oauth__/?code=bla')
        self.assertRedirects(
            response,
            '/admin/little_auth/',
        )

        self.assertEqual(
            client.get('/admin/little_auth/').status_code,
            200,
        )

        client = Client()
        with mock_admin_oauth_client(
                user_data={'email': 'blaaa@invalid.tld'},
                module=admin_oauth_views,
                client='GoogleOAuth2Client',
        ):
            response = client.get('/admin/__oauth__/?code=bla')
        self.assertRedirects(
            response,
            '/admin/login/',
        )

    def test_authlib(self):
        self.assertEqual(
            set(User.objects.values_list('email', flat=True)),
            {'admin@example.com'},
        )

        client = Client()
        response = client.get('/login/?next=/?keep-this=1')
        for snip in [
            '<label for="id_username">Email:</label>',
            '<a href="/oauth/facebook/">Facebook</a>',
            '<a href="/oauth/google/">Google</a>',
            '<a href="/oauth/twitter/">Twitter</a>',
            '<a href="/email/">Magic link by Email</a>',
        ]:
            self.assertContains(
                response,
                snip,
            )

        FacebookOAuth2Client.get_user_data = lambda self: {
            'email': 'test@example.com',
        }
        response = client.get('/oauth/facebook/?code=bla')
        self.assertRedirects(
            response,
            '/?keep-this=1',
            fetch_redirect_response=False,
        )

        self.assertEqual(
            set(User.objects.values_list('email', flat=True)),
            {'admin@example.com', 'test@example.com'},
        )
