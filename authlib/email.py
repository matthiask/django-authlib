import binascii
import contextlib

from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import TemplateDoesNotExist, render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _


# Assumes that this is a model with an unique `email` field.
User = get_user_model()


def render_to_mail(template, context, **kwargs):
    """
    Renders a mail and returns the resulting ``EmailMultiAlternatives``
    instance

    * ``template``: The base name of the text and HTML (optional) version of
      the mail.
    * ``context``: The context used to render the mail. This context instance
      should contain everything required.
    * Additional keyword arguments are passed to the ``EmailMultiAlternatives``
      instantiation. Use those to specify the ``to``, ``headers`` etc.
      arguments.

    Usage example::

        # Render the template myproject/hello_mail.txt (first non-empty line
        # contains the subject, third to last the body) and optionally the
        # template myproject/hello_mail.html containing the alternative HTML
        # representation.
        message = render_to_mail('myproject/hello_mail', {}, to=[email])
        message.send()
    """
    if not isinstance(template, (list, tuple)):
        template = [template]
    lines = iter(
        line.rstrip()
        for line in render_to_string(
            [f"{t}.txt" for t in template], context
        ).splitlines()
    )

    subject = ""
    try:
        while True:
            line = next(lines)
            if line:
                subject = line
                break
    except StopIteration:  # if lines is empty
        pass

    body = "\n".join(lines).strip("\n")
    message = EmailMultiAlternatives(subject=subject, body=body, **kwargs)

    with contextlib.suppress(TemplateDoesNotExist):
        message.attach_alternative(
            render_to_string([f"{t}.html" for t in template], context), "text/html"
        )

    return message


def get_signer(salt="email_registration"):
    """
    Returns the signer instance used to sign and unsign the registration
    link tokens
    """
    return signing.TimestampSigner(salt=salt)


def get_confirmation_code(email, *, payload=""):
    """
    Returns the code for the confirmation URL

    The payload should be a string already.
    """
    s = f"{email}:{payload}"
    return get_signer().sign(signing.b64_encode(s.encode("utf-8")).decode("utf-8"))


def get_confirmation_url(email, request, name="email_registration_confirm", **kwargs):
    """
    Returns the confirmation URL
    """
    return request.build_absolute_uri(
        reverse(name, kwargs={"code": get_confirmation_code(email, **kwargs)})
    )


def send_registration_mail(email, *, request, **kwargs):
    """send_registration_mail(email, *, request, **kwargs)
    Sends the registration mail

    * ``email``: The email address where the registration link should be
      sent to.
    * ``request``: A HTTP request instance, used to construct the complete
      URL (including protocol and domain) for the registration link.
    * Additional keyword arguments for ``get_confirmation_url`` respectively
      ``get_confirmation_code``.

    The mail is rendered using the following two templates:

    * ``registration/email_registration_email.txt``: The first line of this
      template will be the subject, the third to the last line the body of the
      email.
    * ``registration/email_registration_email.html``: The body of the HTML
      version of the mail. This template is **NOT** available by default and
      is not required either.
    """

    render_to_mail(
        "registration/email_registration_email",
        {"url": get_confirmation_url(email, request, **kwargs)},
        to=[email],
    ).send()


def decode(code, *, max_age):
    """decode(code, *, max_age)
    Decodes the code from the registration link and returns a tuple consisting
    of the verified email address and the payload which was passed through to
    ``get_confirmation_code``.

    The maximum age in seconds of the link has to be specified as ``max_age``.

    This method raises ``ValidationError`` exceptions when anything goes wrong
    when verifying the signature or the expiry timeout.
    """
    try:
        data = get_signer().unsign(code, max_age=max_age)
    except signing.SignatureExpired as exc:
        raise ValidationError(
            _("The link is expired. Please request another registration link."),
            code="email_registration_expired",
        ) from exc

    except signing.BadSignature as exc:
        raise ValidationError(
            _(
                "Unable to verify the signature. Please request a new"
                " registration link."
            ),
            code="email_registration_signature",
        ) from exc

    try:
        data = signing.b64_decode(data.encode("utf-8")).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        if ":" not in data:
            raise

    return data.split(":", 1)
