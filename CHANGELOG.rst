==========
Change log
==========

`Next version`_
===============

- Fixed a few problems around inactive users where authlib would either
  handle them incorrectly or reveal that inactive users exist.


`0.8`_ (2018-11-17)
===================

- **BACKWARDS INCOMPATIBLE** Replaced the email registration
  functionality of referencing users with arbitrary payloads. This
  allows not only verifying the email address but also additional data
  which may or may not be related to the user in question. On the other
  hand the comparison of ``last_login`` timestamps is gone, which means
  that links may be reused as long as less than ``max_age`` seconds have
  passed. This makes it even more important to keep ``max_age`` small.
  The change mostly affects the functions in ``authlib.email``.


`0.7`_ (2018-11-04)
===================

- Fixed a race condition when creating new users by using
  ``get_or_create`` instead of some homegrown ``exists`` and
  ``create`` trickery.
- Changed all locations to pass ``new_user`` as keyword argument to
  ``post_login_response``.
- Changed the ``admin/login.html`` template in ``authlib.admin_oauth``
  to make the SSO button a bit more prominent. Also, replaced "SSO" with
  "Google" because that is all that is supported right now.
- Added the possibility to use callables in ``ADMIN_OAUTH_PATTERNS``
  instead of hard-coded staff email addresses.
- Extracted the confirmation code generation from
  ``get_confirmation_url`` as ``get_confirmation_code``.
- Fixed usage of deprecated Google OAuth2 scopes.
- Added compatibility with Python 2.
- Extracted the post login redirect cookie setting into a new
  ``set_next_cookie`` decorator.
- Dropped compatibility shims for Django<1.11.
- Changed the ``EmailBackend`` to use ``_default_manager`` instead of
  assuming that the default manager is called ``objects``.
- Fixed an edge case bug where ``render_to_mail`` would crash when
  encountering an empty text for the subject and body.
- Enforced keyword-only usage of the views and functions in
  ``authlib.views`` where it is appropriate.
- Removed the default messages emitted when creating a new user and when
  logging out.
- Added a ``post_logout_response`` callable and argument to
  ``authlib.views.logout`` to customize messages and redirects after
  logging an user out.
- Added a ``email_login`` callable and argument to the ``oauth2`` and
  ``email_registration`` view to customize the creation, authentication
  and login of users.
- Changed the ``EmailRegistrationForm`` to save the request as
  ``self.request``, not ``self._request``. Made use of this for moving
  the email sending to the form class as well, further shortening the
  view.


`0.6`_ (2017-12-04)
===================

- Fixed usage of a few deprecated APIs.
- Modified ``little_auth.User`` to fall back to an obfuscated email
  address if the full name is empty.
- Made it possible to override the default max age of three hours for
  magic links sent by email.
- Fixed a problem where the ``little_auth`` migrations were depending on
  the latest ``django.contrib.auth`` migration instead of the first
  migration without good reason.


`0.5`_ (2017-05-17)
===================

- Moved from ``ADMIN_OAUTH_DOMAINS`` to ``ADMIN_OAUTH_PATTERNS`` to
  allow regular expression searching.
- Finally started adding tests.
- Added django-authlib_ documentation to Read the Docs.


`0.4`_ (2017-05-11)
===================

- Added some documentation to the README.
- Google client: Removed the deprecated profile scope, and switched to
  online access only (we do not need offline access).
- Added the ``authlib.admin_oauth`` app for a minimal Google OAuth2
  authentication solution for Django's administration interface.
- Added the ``authlib.little_auth`` app containing a minimal user model
  with email as username for a quick and dirty ``auth.User``
  replacement.
- Allow overriding the view name used in
  ``authlib.email.get_confirmation_url``.


`0.3`_ (2016-12-08)
===================

- Fixed the redirect URL generation of the Facebook and Google client.
- Changed the name of the post login redirect cookie from ``next`` to
  ``authlib-next`` to hopefully prevent clashes.
- Authentication providers may also return ``None`` as email address;
  handle this case gracefully by showing an error message instead of
  crashing.
- Pass full URLs, not only paths to the OAuth2 libraries because
  otherwise, secure redirect URLs aren't recognized as such.


`0.2`_ (2016-11-22)
===================

- Added views for registration and logging in and out.
- Added a base user model and an authentication backend for
  authenticating using email addresses only.


`0.1`_ (2016-11-21)
===================

- Initial release containing helpers for authentication using an email
  address, either verified by sending a magic link or retrieved from
  Facebook, Google or Twitter.

.. _django-authlib: https://django-authlib.readthedocs.io/

.. _0.1: https://github.com/matthiask/django-authlib/commit/0e4a81c11
.. _0.2: https://github.com/matthiask/django-authlib/compare/0.1...0.2
.. _0.3: https://github.com/matthiask/django-authlib/compare/0.2...0.3
.. _0.4: https://github.com/matthiask/django-authlib/compare/0.3...0.4
.. _0.5: https://github.com/matthiask/django-authlib/compare/0.4...0.5
.. _0.6: https://github.com/matthiask/django-authlib/compare/0.5...0.6
.. _0.7: https://github.com/matthiask/django-authlib/compare/0.6...0.7
.. _0.8: https://github.com/matthiask/django-authlib/compare/0.7...0.8
.. _Next version: https://github.com/matthiask/django-authlib/compare/0.8...master
