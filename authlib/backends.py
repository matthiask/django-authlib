from django.contrib.auth import get_user_model
from django.db.models import ObjectDoesNotExist


class EmailBackend(object):
    def _get_user(self, **kwargs):
        try:
            return get_user_model()._default_manager.get(is_active=True, **kwargs)
        except ObjectDoesNotExist:
            return None

    def get_user(self, user_id):
        return self._get_user(pk=user_id)

    def authenticate(self, request, email):
        return self._get_user(email=email)
