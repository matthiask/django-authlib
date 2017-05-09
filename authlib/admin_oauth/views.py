from django.conf import settings
from django.contrib import auth, messages
from django.shortcuts import redirect
from django.utils.http import is_safe_url
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from authlib.google import GoogleOAuth2Client


REDIRECT_SESSION_KEY = 'admin-oauth-next'


def retrieve_next(request):
    next = request.session.pop(REDIRECT_SESSION_KEY, None)
    print('GOT', next, is_safe_url(url=next, host=request.get_host()))
    return next if is_safe_url(url=next, host=request.get_host()) else None


@never_cache
def admin_oauth(request):
    client = GoogleOAuth2Client(request)

    if request.GET.get('next'):
        request.session[REDIRECT_SESSION_KEY] = request.GET['next']

    if all(key not in request.GET for key in ('code', 'oauth_token')):
        return redirect(client.get_authentication_url())

    user_data = client.get_user_data()
    email = user_data.get('email', '')

    if email:
        for domain, user_mail in settings.ADMIN_OAUTH_DOMAINS:
            if email.endswith(domain):
                user = auth.authenticate(email=user_mail)
                if user and user.is_staff:
                    auth.login(request, user)
                    return redirect(retrieve_next(request) or 'admin:index')

    messages.error(
        request,
        _('No email address received or email domain unknown.'),
    )
    return redirect('admin:login')
