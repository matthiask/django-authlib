from django.conf.urls import include, url
from django.contrib import admin
from django.shortcuts import render

from authlib import views
from authlib.facebook import FacebookOAuth2Client
from authlib.google import GoogleOAuth2Client
from authlib.twitter import TwitterOAuthClient


urlpatterns = [
    url(r'', include('authlib.admin_oauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^404/$', lambda request: render(request, '404.html')),

    url(
        r'^login/$',
        views.login,
        name='login',
    ),
    url(r'^oauth/facebook/$',
        views.oauth2,
        {
            'client_class': FacebookOAuth2Client,
        },
        name='accounts_oauth_facebook',
    ),
    url(r'^oauth/google/$',
        views.oauth2,
        {
            'client_class': GoogleOAuth2Client,
        },
        name='accounts_oauth_google',
    ),
    url(r'^oauth/twitter/$',
        views.oauth2,
        {
            'client_class': TwitterOAuthClient,
        },
        name='accounts_oauth_twitter',
    ),
    url(
        r'^email/$',
        views.email_registration,
        name='email_registration',
    ),
    url(
        r'^email/(?P<code>[^/]+)/$',
        views.email_registration,
        name='email_registration_confirm',
    ),
    url(
        r'^logout/$',
        views.logout,
        name='logout',
    ),
]
