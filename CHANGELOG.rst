==========
Change log
==========

`Next version`_
===============

- Fixed usage of a few deprecated APIs.


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
.. _Next version: https://github.com/matthiask/django-authlib/compare/0.5...master
