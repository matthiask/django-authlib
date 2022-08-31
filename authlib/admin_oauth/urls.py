from django.urls import path

from authlib.admin_oauth.views import admin_oauth


urlpatterns = [path("admin/__oauth__/", admin_oauth, name="admin_oauth")]
