from django.urls import re_path

from authlib.admin_oauth.views import admin_oauth


urlpatterns = [re_path(r"^admin/__oauth__/$", admin_oauth, name="admin_oauth")]
