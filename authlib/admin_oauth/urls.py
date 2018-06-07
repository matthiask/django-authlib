from django.conf.urls import url

from authlib.admin_oauth.views import admin_oauth


urlpatterns = [url(r"^admin/__oauth__/$", admin_oauth, name="admin_oauth")]
