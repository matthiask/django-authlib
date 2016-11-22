from django.contrib.auth import get_user_model


class EmailBackend(object):
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, email):
        User = get_user_model()
        try:
            return User.objects.get(
                email=email,
                is_active=True,
            )
        except User.DoesNotExist:
            pass
