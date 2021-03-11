from django.contrib import admin
from django.shortcuts import render
from django.urls import include, re_path
from testapp.views import custom_verification, custom_verification_code

from authlib import views
from authlib.facebook import FacebookOAuth2Client
from authlib.google import GoogleOAuth2Client
from authlib.twitter import TwitterOAuthClient


urlpatterns = [
    re_path(r"", include("authlib.admin_oauth.urls")),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^404/$", lambda request: render(request, "404.html")),
    re_path(r"^login/$", views.login, name="login"),
    re_path(
        r"^oauth/facebook/$",
        views.oauth2,
        {"client_class": FacebookOAuth2Client},
        name="accounts_oauth_facebook",
    ),
    re_path(
        r"^oauth/google/$",
        views.oauth2,
        {"client_class": GoogleOAuth2Client},
        name="accounts_oauth_google",
    ),
    re_path(
        r"^oauth/twitter/$",
        views.oauth2,
        {"client_class": TwitterOAuthClient},
        name="accounts_oauth_twitter",
    ),
    re_path(r"^email/$", views.email_registration, name="email_registration"),
    re_path(
        r"^email/(?P<code>[^/]+)/$",
        views.email_registration,
        name="email_registration_confirm",
    ),
    re_path(r"^logout/$", views.logout, name="logout"),
    re_path(r"^custom/$", custom_verification),
    re_path(
        r"^custom/(?P<code>[^/]+)/$",
        custom_verification_code,
        name="custom_verification_code",
    ),
]
