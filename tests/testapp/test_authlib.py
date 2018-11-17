import requests_mock
from contextlib import contextmanager

from django.test import Client, TestCase
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


class Test(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser("admin@example.com", "blabla")
        deactivate_all()

    def login(self):
        client = Client()
        client.force_login(self.user)
        return client

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
        User.objects.create_superuser("bla@example.org", "blabla")

        client = Client()
        with google_oauth_data({"email": "bla@example.org", "email_verified": True}):
            response = client.get("/admin/__oauth__/?code=bla")
        self.assertRedirects(response, "/admin/")

        # We are authenticated
        self.assertEqual(client.get("/admin/little_auth/").status_code, 200)

    def test_admin_oauth_nomatch(self):
        User.objects.create_superuser("bla@example.org", "blabla")

        client = Client()
        with google_oauth_data({"email": "blaa@example.org", "email_verified": True}):
            response = client.get("/admin/__oauth__/?code=bla")

        # We are not authenticated
        self.assertRedirects(response, "/admin/login/")

        messages = [str(m) for m in response.wsgi_request._messages]
        self.assertEqual(
            messages, ["No matching staff users for email address 'blaa@example.org'"]
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
