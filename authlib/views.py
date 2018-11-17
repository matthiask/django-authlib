from functools import wraps

from django import forms
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils.http import is_safe_url
from django.utils.inspect import func_supports_parameter
from django.utils.translation import ugettext as _, ugettext_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from authlib.email import decode, send_registration_mail
from authlib.utils import positional


REDIRECT_COOKIE_NAME = "authlib-next"


def set_next_cookie(view):
    @wraps(view)
    def fn(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        if request.GET.get("next"):
            response.set_cookie(REDIRECT_COOKIE_NAME, request.GET["next"], max_age=600)
        return response

    return fn


def retrieve_next(request):
    next = request.COOKIES.get(REDIRECT_COOKIE_NAME)
    if func_supports_parameter(is_safe_url, "allowed_hosts"):  # Django 1.11
        kw = {"allowed_hosts": {request.get_host()}}
    else:
        kw = {"host": request.get_host()}
    return next if is_safe_url(url=next, **kw) else None


@positional(1)
def post_login_response(request, new_user):
    response = redirect(retrieve_next(request) or settings.LOGIN_REDIRECT_URL)
    response.delete_cookie(REDIRECT_COOKIE_NAME)
    return response


def post_logout_response(request):
    return redirect("login")


@positional(1)
def email_login(request, email, **kwargs):
    """
    Given a request, an email and optionally some additional data, ensure that
    a user with the email address exists, and authenticate & login them right
    away if the user is active.

    Returns a tuple consisting of ``(user, created)`` upon success or ``(None,
    None)`` when authentication fails.
    """
    _u, created = auth.get_user_model()._default_manager.get_or_create(email=email)
    user = auth.authenticate(request, email=email)
    if user and user.is_active:  # The is_active check is possibly redundant.
        auth.login(request, user)
        return user, created
    return None, None


@never_cache
@sensitive_post_parameters()
@set_next_cookie
@positional(1)
def login(
    request,
    template_name="registration/login.html",
    authentication_form=AuthenticationForm,
    post_login_response=post_login_response,
):
    form = authentication_form(
        request, data=request.POST if request.method == "POST" else None
    )
    if form.is_valid():
        auth.login(request, form.get_user())
        return post_login_response(request, new_user=False)
    return render(request, template_name, {"form": form})


@never_cache
@positional(1)
def oauth2(
    request,
    client_class,
    post_login_response=post_login_response,
    email_login=email_login,
):
    client = client_class(request)

    if all(key not in request.GET for key in ("code", "oauth_token")):
        return redirect(client.get_authentication_url())

    user_data = client.get_user_data()
    email = user_data.pop("email", None)

    if email:
        user, created = email_login(request, email=email, user_data=user_data)
        if user:
            return post_login_response(request, new_user=created)
        messages.error(
            request, _("No active user with email address %s found.") % email
        )

    else:
        messages.error(request, _("Did not get an email address. Please try again."))

    return redirect("login")


class EmailRegistrationForm(forms.Form):
    email = forms.EmailField(label=ugettext_lazy("email"))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(EmailRegistrationForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            if self.request.user.is_authenticated and email != self.request.user.email:
                raise forms.ValidationError(
                    _(
                        "The email you entered (%(input)s) does not match the"
                        " email of the account you're logged in as currently"
                        " (%(current)s)."
                    )
                    % {"input": email, "current": self.request.user.email}
                )
        return email

    @positional(1)
    def send_mail(self, **kwargs):
        send_registration_mail(
            self.cleaned_data["email"], request=self.request, **kwargs
        )


@never_cache
@positional(1)
def email_registration(
    request,
    code=None,
    registration_form=EmailRegistrationForm,
    post_login_response=post_login_response,
    max_age=3600 * 3,
    email_login=email_login,
):
    if code is None:
        form = registration_form(
            request.POST if request.method == "POST" else None, request=request
        )
        if form.is_valid():
            form.send_mail()
            messages.success(request, _("Please check your mailbox."))
            return redirect(".")
        return render(request, "registration/email_registration.html", {"form": form})

    else:
        try:
            email, payload = decode(code, max_age=max_age)
        except ValidationError as exc:
            [messages.error(request, msg) for msg in exc.messages]
            return redirect("../")

        user, created = email_login(request, email=email)
        if user:
            return post_login_response(request, new_user=created)
        messages.error(
            request, _("No active user with email address %s found.") % email
        )
        return redirect("login")


@never_cache
@positional(1)
def logout(request, post_logout_response=post_logout_response):
    auth.logout(request)
    return post_logout_response(request)
