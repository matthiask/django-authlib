from django.conf.urls import include, url
from django.contrib import admin
from django.shortcuts import render


urlpatterns = [
    url(r'', include('authlib.admin_oauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^404/$', lambda request: render(request, '404.html')),
]
