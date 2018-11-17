from django.http import HttpResponse
from django.shortcuts import render

from authlib.email import decode
from authlib.views import EmailRegistrationForm


def custom_verification(request):
    form = EmailRegistrationForm(
        request.POST if request.method == "POST" else None, request=request
    )
    if form.is_valid():
        form.send_mail(payload="hello:world:42", name="custom_verification_code")
    return render(request, "registration/email_registration.html", {"form": form})


def custom_verification_code(request, code):
    email, payload = decode(code, max_age=100)
    return HttpResponse("email:{} payload:{}".format(email, payload))
