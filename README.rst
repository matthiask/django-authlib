================================================
django-authlib - Authentication utils for Django
================================================

authlib is a collection of authentication utilities for implementing
passwordless authentication. This is achieved by either sending
cryptographically signed links by email, or by fetching the email
address from third party providers such as Google, Facebook and Twitter.
After all, what's the point in additionally requiring a password for
authentication when the password can be easily resetted on most websites
when an attacker has access to the email address?


Usage
=====

- Install ``django-authlib`` using pip into your virtualenv.
- Add ``authlib.backends.EmailBackend`` to ``AUTHENTICATION_BAcKENDS``.
- Adding ``authlib`` to ``INSTALLED_APPS`` is optional and only useful
  if you want to use the bundled translation files. There are no
  required database tables or anything of the sort.
- Have a user model which has a email field named ``email`` as username.
  For convenience a base user model and manager are available in the
  ``authlib.base`` module, ``BaseUser`` and ``BaseUserManager``.
  The ``BaseUserManager`` is automatically available as ``objects`` when
  you extend the ``BaseUser``.
- Use the bundled views or write your own. The bundled views give
  feedback using ``django.contrib.messages``, so you may want to check
  that those messages are visible to the user.

The Google, Facebook and Twitter OAuth clients require the following
settings:

- ``GOOGLE_CLIENT_ID``
- ``GOOGLE_CLIENT_SECRET``
- ``FACEBOOK_CLIENT_ID``
- ``FACEBOOK_CLIENT_SECRET``
- ``TWITTER_CLIENT_ID``
- ``TWITTER_CLIENT_SECRET``

Note that you have to configure the Twitter app to allow email access,
this is not enabled by default.


Use of bundled views
====================

The following URL patterns are an example for using the bundled views.
For now you'll have to dig into the code (it's not much, at the time of
writing ``django-authlib``'s Python code is less than 500 lines)::

    from django.conf.urls import url
    from authlib import views
    from authlib.facebook import FacebookOAuth2Client
    from authlib.google import GoogleOAuth2Client
    lrom authlib.twitter import TwitterOAuthClient

    urlpatterns = [
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
