from django.conf import settings
from django.contrib import auth
from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters


def retrieve_next(request):
    next = request.COOKIES.get('next')
    return next if is_safe_url(url=next, host=request.get_host()) else None


def post_login_response(request):
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
