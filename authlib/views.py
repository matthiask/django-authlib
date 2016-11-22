from django.conf import settings
from django.contrib import auth, messages
from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import is_safe_url
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters


def retrieve_next(request):
    next = request.COOKIES.get('next')
    return next if is_safe_url(url=next, host=request.get_host()) else None


def post_login_response(request, new_user):
    return redirect(retrieve_next(request) or settings.LOGIN_REDIRECT_URL)


@never_cache
@sensitive_post_parameters()
def login(request, template_name='registration/login.html',
          authentication_form=AuthenticationForm,
          post_login_response=post_login_response):

    if request.method == 'POST':
        form = authentication_form(request, data=request.POST)

        if form.is_valid():
            auth.login(request, form.get_user())
            return post_login_response(request, new_user=False)
    else:
        form = authentication_form(request)

    response = render(request, template_name, {
        'form': form,
    })
    if request.GET.get('next'):
        response.set_cookie('next', request.GET['next'], max_age=600)
    return response


@never_cache
def oauth2(request, client_class, post_login_response=post_login_response):
    User = auth.get_user_model()
    client = client_class(request)

    if all(key not in request.GET for key in ('code', 'oauth_token')):
        return redirect(client.get_authentication_url())

    user_data = client.get_user_data()

    if user_data.get('email'):
        email = user_data.pop('email')
        new_user = False

        if not User.objects.filter(email=email).exists():
            User.objects.create(
                email=email,
                **user_data
            )
            messages.success(
                request,
                _('Welcome! Please fill in your details.'))
            new_user = True

        user = auth.authenticate(email=email)
        if user and user.is_active:
            auth.login(request, user)
        else:
            messages.error(
                request,
                _('No user with email address %s found.') % email)

        return post_login_response(request, new_user)

    return redirect('login')


@never_cache
def logout(request):
    auth.logout(request)
    messages.success(
        request,
        _('You have been signed out.'))
    return redirect('login')
