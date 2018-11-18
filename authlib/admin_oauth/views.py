import re

from django.conf import settings
from django.contrib import auth, messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from authlib.google import GoogleOAuth2Client
from authlib.views import set_next_cookie, retrieve_next


ADMIN_OAUTH_PATTERNS = settings.ADMIN_OAUTH_PATTERNS


@never_cache
@set_next_cookie
def admin_oauth(request):
    client = GoogleOAuth2Client(request)

    if all(key not in request.GET for key in ("code", "oauth_token")):
        return redirect(client.get_authentication_url())

    user_data = client.get_user_data()
    email = user_data.get("email", "")

    if email:
        for pattern, user_mail in ADMIN_OAUTH_PATTERNS:
            match = re.search(pattern, email)
            if match:
                if callable(user_mail):
                    user_mail = user_mail(match)
                user = auth.authenticate(email=user_mail)
                if user and user.is_staff:
                    auth.login(request, user)
                    return redirect(retrieve_next(request) or "admin:index")

        messages.error(
            request, _("No matching staff users for email address '%s'") % email
        )
    else:
        messages.error(request, _("Could not determine your email address."))
    return redirect("admin:login")
