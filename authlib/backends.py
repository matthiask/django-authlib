from django.contrib.auth import get_user_model


def _by_email(email):
    User = get_user_model()
    try:
        return User._default_manager.get(email=email, is_active=True)
    except User.DoesNotExist:
        pass


class EmailBackend(object):
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User._default_manager.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, email):
        return _by_email(email)
