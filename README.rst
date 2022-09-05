================================================
django-authlib - Authentication utils for Django
================================================

.. image:: https://github.com/matthiask/django-authlib/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/matthiask/django-authlib/
    :alt: CI Status

.. image:: https://readthedocs.org/projects/django-authlib/badge/?version=latest
    :target: https://django-authlib.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

authlib is a collection of authentication utilities for implementing
passwordless authentication. This is achieved by either sending
cryptographically signed links by email, or by fetching the email
address from third party providers such as Google, Facebook and Twitter.
After all, what's the point in additionally requiring a password for
authentication when the password can be easily resetted on most websites
when an attacker has access to the email address?


Goals
=====

- Stay small, simple and extensible.
- Offer tools and utilities instead of imposing a framework on you.


Usage
=====

- Install ``django-authlib`` using pip into your virtualenv.
- Add ``authlib.backends.EmailBackend`` to ``AUTHENTICATION_BAcKENDS``.
- Adding ``authlib`` to ``INSTALLED_APPS`` is optional and only useful
  if you want to use the bundled translation files. There are no
  required database tables or anything of the sort.
- Have a user model which has a email field named ``email`` as username.
  For convenience a base user model and manager are available in the
  ``authlib.base_user`` module, ``BaseUser`` and ``BaseUserManager``.
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

.. note::
    If you want to use OAuth2 providers in development mode (without HTTPS) you
    could add the following lines to your ``settings.py``:

    .. code-block:: python

        if DEBUG:
            # NEVER set this variable in production environments!
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    This is required because of the strictness of
    `oauthlib <https://pypi.org/project/oauthlib/>`__ which only wants HTTPS
    URLs (and rightly so).


Use of bundled views
====================

The following URL patterns are an example for using the bundled views.
For now you'll have to dig into the code (it's not much, at the time of
writing ``django-authlib``'s Python code is less than 500 lines):

.. code-block:: python

    from django.conf.urls import url
    from authlib import views
    from authlib.facebook import FacebookOAuth2Client
    from authlib.google import GoogleOAuth2Client
    from authlib.twitter import TwitterOAuthClient

    urlpatterns = [
        url(
            r"^login/$",
            views.login,
            name="login",
        ),
        url(
            r"^oauth/facebook/$",
            views.oauth2,
            {
                "client_class": FacebookOAuth2Client,
            },
            name="accounts_oauth_facebook",
        ),
        url(
            r"^oauth/google/$",
            views.oauth2,
            {
                "client_class": GoogleOAuth2Client,
            },
            name="accounts_oauth_google",
        ),
        url(
            r"^oauth/twitter/$",
            views.oauth2,
            {
                "client_class": TwitterOAuthClient,
            },
            name="accounts_oauth_twitter",
        ),
        url(
            r"^email/$",
            views.email_registration,
            name="email_registration",
        ),
        url(
            r"^email/(?P<code>[^/]+)/$",
            views.email_registration,
            name="email_registration_confirm",
        ),
        url(
            r"^logout/$",
            views.logout,
            name="logout",
        ),
    ]


Admin OAuth2
============

The ``authlib.admin_oauth`` app allows using Google OAuth2 to allow all
users with the same email domain to authenticate for Django's
administration interface. You have to use authlib's authentication
backend (``EmailBackend``) for this.

Installation is as follows:

- Follow the steps in the "Usage" section above.
- Add ``authlib.admin_oauth`` to your ``INSTALLED_APPS`` before
  ``django.contrib.admin``, so that our login template is picked up.
- Add ``GOOGLE_CLIENT_ID`` and ``GOOGLE_CLIENT_SECRET`` to your settings
  as described above.
- Add a ``ADMIN_OAUTH_PATTERNS`` setting. The first item is the domain,
  the second the email address of a staff account. If no matching staff
  account exists, authentication fails:

.. code-block:: python

    ADMIN_OAUTH_PATTERNS = [
        (r"@example\.com$", "admin@example.com"),
    ]

- Add an entry to your URLconf:

.. code-block:: python

    urlpatterns = [
        url(r"", include("authlib.admin_oauth.urls")),
        # ...
    ]

- Add ``https://yourdomain.com/admin/__oauth__/`` as a valid redirect
  URI in your Google developers console.

Please note that the ``authlib.admin_oauth.urls`` module assumes that the admin
site is registered at ``/admin/``. If this is not the case you can integrate
the view yourself under a different URL.

It is also allowed to use a callable instead of the email address in the
``ADMIN_OAUTH_PATTERNS`` setting; the callable is passed the result of matching
the regex. If a resulting email address does not exist, authentication (of
course) fails:

.. code-block:: python

    ADMIN_OAUTH_PATTERNS = [
        (r"^.*@example\.org$", lambda match: match[0]),
    ]

If a pattern succeeds but no matching user with staff access is found
processing continues with the next pattern. This means that you can
authenticate users with their individual accounts (if they have one) and
fall back to an account for everyone having a Google email address on
your domain:

.. code-block:: python

    ADMIN_OAUTH_PATTERNS = [
        (r"^.*@example\.org$", lambda match: match[0]),
        (r"@example\.com$", "admin@example.com"),
    ]

You could also remove the fallback line; in this case users can only
authenticate if they have a personal staff account.

Little Auth
===========

The ``authlib.little_auth`` app contains a basic user model with email
as username that can be used if you do not want to write your own user
model but still profit from authlib's authentication support.

Usage is as follows:

- Add ``authlib.little_auth`` to your ``INSTALLED_APPS``
- Set ``AUTH_USER_MODEL = "little_auth.User"``
- Optionally also follow any of the steps above.

Email Registration
==================

For email registration to work, two templates are needed:

* ``registration/email_registration_email.txt``
* ``registration/email_registration.html``


A starting point would be:

``email_registration_email.txt``:

.. code-block:: text


    Subject (1st line)

    Body (3rd line onwards)
    {{ url }}
    ...


``email_registration.html``:

.. code-block:: html


    {% if messages %}
    <ul class="messages">
        {% for message in messages %}
        <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>
            {% if message.level == DEFAULT_MESSAGE_LEVELS.ERROR %}Important: {% endif %}
            {{ message }}
        </li>
        {% endfor %}
    </ul>
    {% endif %}

    {% if form.errors and not form.non_field_errors %}
    <p class="errornote">
        {% if form.errors.items|length == 1 %}
        {% translate "Please correct the error below." %}
        {% else %}
        {% translate "Please correct the errors below." %}
        {% endif %}
    </p>
    {% endif %}

    {% if form.non_field_errors %}
    {% for error in form.non_field_errors %}
    <p class="errornote">
        {{ error }}
    </p>
    {% endfor %}
    {% endif %}

    <form action='{% url "email_registration" %}' method="post" >
        {% csrf_token %}
        <table>
            {{ form }}
        </table>
        <input type="submit" value="login">
    </form>

The above template is inspired from:

* `Messages Django documentation <https://docs.djangoproject.com/en/dev/ref/contrib/messages/#displaying-messages>`_
* `Django login template <https://github.com/django/django/blob/67d0c4644acfd7707be4a31e8976f865509b09ac/django/contrib/admin/templates/admin/login.html#L21-L44>`_

More details are documented in `the relevant module <https://github.com/matthiask/django-authlib/blob/main/authlib/email.py>`_.
