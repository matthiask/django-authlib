import requests_mock
from contextlib import contextmanager

from django.test import Client, TestCase
from django.utils.six.moves.urllib.parse import urlparse, parse_qsl
from django.utils.translation import deactivate_all

from authlib.facebook import FacebookOAuth2Client
from authlib.little_auth.models import User


@contextmanager
def google_oauth_data(data):
    with requests_mock.Mocker() as m:
        m.post(
            "https://www.googleapis.com/oauth2/v4/token", json={"access_token": "123"}
        )
        m.get("https://www.googleapis.com/oauth2/v3/userinfo", json=data)
        yield


@contextmanager
def google_oauth_authentication_url():
    with requests_mock.Mocker() as m:
        m.get("https://accounts.google.com/o/oauth2/v2/auth", {})
        yield


class Test(TestCase):
    def setUp(self):
        deactivate_all()
        self.user = User.objects.create_superuser("admin@example.com", "blabla")

    def test_admin_oauth(self):
        client = Client()

        response = client.get("/admin/login/?next=/admin/little_auth/")
        self.assertContains(
            response,
            '<a class="button"'
            ' href="/admin/__oauth__/?next=/admin/little_auth/">'
            "Log in using Google</a>",
        )

        response = client.get("/admin/__oauth__/?next=/admin/little_auth/")
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "https://accounts.google.com/o/oauth2/v2/auth?response_type=code"
            "&client_id=empty&redirect_uri=",
            response["Location"],
        )
        self.assertEqual(client.session["admin-oauth-next"], "/admin/little_auth/")

        with google_oauth_data({"email": "blaaa@example.com", "email_verified": True}):
            response = client.get("/admin/__oauth__/?code=bla")
        self.assertRedirects(response, "/admin/little_auth/")

        self.assertEqual(client.get("/admin/little_auth/").status_code, 200)

        client = Client()
        with google_oauth_data({"email": "blaaa@invalid.tld", "email_verified": True}):
            response = client.get("/admin/__oauth__/?code=bla")
        self.assertRedirects(response, "/admin/login/")

    def test_admin_oauth_no_data(self):
        client = Client()
        with google_oauth_data({}):
            response = client.get("/admin/__oauth__/?code=bla")

        self.assertRedirects(response, "/admin/login/")

        messages = [str(m) for m in response.wsgi_request._messages]
        self.assertEqual(messages, ["Could not determine your email address."])

    def test_admin_oauth_match(self):
        client = Client()
        with google_oauth_data({"email": "admin@example.com", "email_verified": True}):
            response = client.get("/admin/__oauth__/?code=bla")
        self.assertRedirects(response, "/admin/")

        # We are authenticated
        self.assertEqual(client.get("/admin/little_auth/").status_code, 200)

    def test_admin_oauth_nomatch(self):
        client = Client()
        with google_oauth_data({"email": "bla@example.org", "email_verified": True}):
            response = client.get("/admin/__oauth__/?code=bla")

        # We are not authenticated
        self.assertRedirects(response, "/admin/login/")

        messages = [str(m) for m in response.wsgi_request._messages]
        self.assertEqual(
            messages, ["No matching staff users for email address 'bla@example.org'"]
        )

    def test_authlib(self):
        self.assertEqual(
            set(User.objects.values_list("email", flat=True)), {"admin@example.com"}
        )

        client = Client()
        response = client.get("/login/?next=/?keep-this=1")
        for snip in [
            '<label for="id_username">Email:</label>',
            '<a href="/oauth/facebook/">Facebook</a>',
            '<a href="/oauth/google/">Google</a>',
            '<a href="/oauth/twitter/">Twitter</a>',
            '<a href="/email/">Magic link by Email</a>',
        ]:
            self.assertContains(response, snip)

        FacebookOAuth2Client.get_user_data = lambda self: {"email": "test@example.com"}
        response = client.get("/oauth/facebook/?code=bla")
        self.assertRedirects(response, "/?keep-this=1", fetch_redirect_response=False)

        self.assertEqual(
            set(User.objects.values_list("email", flat=True)),
            {"admin@example.com", "test@example.com"},
        )

    def test_str_and_email_obfuscate(self):
        user = User(email="just-testing@example.com")
        self.assertEqual(user.get_full_name(), "jus***@***.com")
        self.assertEqual(str(user), "jus***@***.com")


class OAuth2Test(TestCase):
    def test_oauth2_authorization_redirect(self):
        client = Client()

        response = client.get("/oauth/google/")
        self.assertEqual(response.status_code, 302)
        url = urlparse(response["Location"])
        params = dict(parse_qsl(url.query))
        self.assertEqual(params["response_type"], "code")
        self.assertEqual(params["redirect_uri"], "http://testserver/oauth/google/")
        self.assertEqual(params["scope"], "openid email profile")

    def test_oauth2_no_data(self):
        client = Client()

        with google_oauth_data({}):
            response = client.get("/oauth/google/?code=bla")
        self.assertRedirects(response, "/login/", fetch_redirect_response=False)
        messages = [str(m) for m in response.wsgi_request._messages]
        self.assertEqual(messages, ["Did not get an email address. Please try again."])

    def test_oauth2_success(self):
        client = Client()

        with google_oauth_data({"email": "test3@example.com", "email_verified": True}):
            response = client.get("/oauth/google/?code=bla")
        self.assertRedirects(response, "/?login=1", fetch_redirect_response=False)
        messages = [str(m) for m in response.wsgi_request._messages]
        self.assertEqual(messages, [])

        self.assertEqual(User.objects.get().email, "test3@example.com")

    def test_oauth2_inactive(self):
        User.objects.create(email="test4@example.com", is_active=False)
        client = Client()

        with google_oauth_data({"email": "test4@example.com", "email_verified": True}):
            response = client.get("/oauth/google/?code=bla")
        self.assertRedirects(response, "/login/", fetch_redirect_response=False)
        messages = [str(m) for m in response.wsgi_request._messages]
        self.assertEqual(
            messages, ["No active user with email address test4@example.com found."]
        )
