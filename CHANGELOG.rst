==========
Change log
==========

`Next version`_
~~~~~~~~~~~~~~~

- Added some documentation to the README.
- Google client: Removed the deprecated profile scope, and switched to
  online access only (we do not need offline access).


`0.3`_ (2016-12-08)
~~~~~~~~~~~~~~~~~~~

- Fixed the redirect URL generation of the Facebook and Google client.
- Changed the name of the post login redirect cookie from ``next`` to
  ``authlib-next`` to hopefully prevent clashes.
- Authentication providers may also return ``None`` as email address;
  handle this case gracefully by showing an error message instead of
  crashing.
- Pass full URLs, not only paths to the OAuth2 libraries because
  otherwise, secure redirect URLs aren't recognized as such.


`0.2`_ (2016-11-22)
~~~~~~~~~~~~~~~~~~~

- Added views for registration and logging in and out.
- Added a base user model and an authentication backend for
  authenticating using email addresses only.


`0.1`_ (2016-11-21)
~~~~~~~~~~~~~~~~~~~

- Initial release containing helpers for authentication using an email
  address, either verified by sending a magic link or retrieved from
  Facebook, Google or Twitter.


.. _0.1: https://github.com/matthiask/django-authlib/commit/0e4a81c11
.. _0.2: https://github.com/matthiask/django-authlib/compare/0.1...0.2
.. _0.3: https://github.com/matthiask/django-authlib/compare/0.2...0.3
.. _Next version: https://github.com/matthiask/django-authlib/compare/0.3...master
