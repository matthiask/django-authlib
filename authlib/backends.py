from django import VERSION
from django.contrib.auth import get_user_model


def _by_email(email):
    User = get_user_model()
    try:
        return User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        pass


class EmailBackend(object):
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    if VERSION < (1, 11):

        def authenticate(self, email):
            return _by_email(email)

    else:

        def authenticate(self, request, email):
            return _by_email(email)
