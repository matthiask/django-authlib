import re

from django.conf import settings
from django.contrib import auth, messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from authlib.google import GoogleOAuth2Client
from authlib.views import retrieve_next, set_next_cookie
from django.utils.module_loading import import_string

ADMIN_OAUTH_PATTERNS = settings.ADMIN_OAUTH_PATTERNS
ADMIN_OAUTH_LOGIN_HINT = "admin-oauth-login-hint"
ADMIN_OAUTH_CREATE_USER_IF_MISSING = getattr(settings, "ADMIN_OAUTH_CREATE_USER_IF_MISSING", False)
ADMIN_OAUTH_CREATE_USER_CALLBACK = getattr(settings, "ADMIN_OAUTH_CREATE_USER_CALLBACK", None)


@never_cache
@set_next_cookie
def admin_oauth(request):
    client = GoogleOAuth2Client(
        request, login_hint=request.COOKIES.get(ADMIN_OAUTH_LOGIN_HINT) or ""
    )

    if all(key not in request.GET for key in ("code", "oauth_token")):
        return redirect(client.get_authentication_url())

    try:
        user_data = client.get_user_data()
    except Exception as exc:
        messages.error(request, exc)
        messages.error(request, _("Error while fetching user data. Please try again."))
        return redirect("admin:login")

    email = user_data.get("email")
    if email:
        for pattern, user_mail in ADMIN_OAUTH_PATTERNS:
            match = re.search(pattern, email)
            if match:
                if callable(user_mail):
                    user_mail = user_mail(match)
                user = auth.authenticate(email=user_mail)
                if not user and ADMIN_OAUTH_CREATE_USER_IF_MISSING == True and ADMIN_OAUTH_CREATE_USER_CALLBACK is not None:
                    try:
                        create_user_method = import_string(ADMIN_OAUTH_CREATE_USER_CALLBACK)
                        user = create_user_method(request, email)
                    except ImportError as e:
                        messages.error(
                            request, _("Unable to import '%s' method") % ADMIN_OAUTH_CREATE_USER_CALLBACK
                        )
                    except Exception as e:
                        messages.error(
                            request, _("Unable to create user with provided '%s' method") % ADMIN_OAUTH_CREATE_USER_CALLBACK
                        )
                if user and user.is_staff:
                    auth.login(request, user)
                    response = redirect(retrieve_next(request) or "admin:index")
                    response.set_cookie(
                        ADMIN_OAUTH_LOGIN_HINT, email, expires=30 * 86400
                    )
                    return response

        messages.error(
            request, _("No matching staff users for email address '%s'") % email
        )
    else:
        messages.error(request, _("Could not determine your email address."))
    response = redirect("admin:login")
    response.delete_cookie(ADMIN_OAUTH_LOGIN_HINT)
    return response