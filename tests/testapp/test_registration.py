import re
import time

from django.core import mail
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import timezone
from django.utils.http import urlunquote
try:
    from django.urls import reverse
except ImportError:  # pragma: no cover
    from django.core.urlresolvers import reverse

from authlib.little_auth.models import User
from authlib.email import get_signer, send_registration_mail


def _messages(response):
    return [m.message for m in response.context['messages']]



class RegistrationTest(TestCase):
    def test_registration(self):
        response = self.client.get('/email/')

        response = self.client.post('/email/', {
            'email': 'test@example.com',
        })
        self.assertRedirects(
            response,
            '/email/',
        )
        response = self.client.get('/email/')
        self.assertEqual(
            _messages(response),
            ['Please check your mailbox.'],
        )

        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        url = urlunquote(
            [line for line in body.splitlines() if 'testserver' in line][0])

        self.assertTrue('http://testserver/email/test@example.com:::' in url)

        response = self.client.get(url)
        self.assertRedirects(
            response,
            '/?login=1',
            fetch_redirect_response=False,
        )

    def test_existing_user(self):
        user = User.objects.create(
            email='test@example.com',
        )

        request = RequestFactory().get('/')
        send_registration_mail('test@example.com', request=request, user=user)

        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        url = urlunquote(
            [line for line in body.splitlines() if 'testserver' in line][0])

        self.assertTrue(re.match(
            r'http://testserver/email/test@example.com:\d+:\w+:',
            url))

        response = self.client.get(url)

        self.assertRedirects(
            response,
            '/?login=1',
            fetch_redirect_response=False,
        )

        user = User.objects.get()
        self.assertEqual(user.email, 'test@example.com')

        time.sleep(1.1)
        user.last_login = timezone.now()
        user.save()

        response = self.client.get(url, follow=True)
        self.assertEqual(
            _messages(response),
            ['The link has already been used.'])
        self.assertRedirects(response, '../')

        response = self.client.get(
            url.replace('/email/', '/er-quick/', 1),
            follow=True,
        )
        self.assertEqual(
            _messages(response),
            ['The link has already been used.'],
        )

        response = self.client.get(
            url.replace('com:', 'ch:', 1),
            follow=True,
        )
        self.assertEqual(
            _messages(response),
            [
                'Unable to verify the signature. Please request a new'
                ' registration link.'
            ])

        user.delete()
        response = self.client.get(url, follow=True)
        self.assertEqual(
            _messages(response),
            [
                'Unable to verify the signature. Please request a new'
                ' registration link.',
                'Something went wrong while decoding the'
                ' registration request. Please try again.'
            ])

    def test_crap(self):
        user = User.objects.create_user('test@example.com', 'pass')

        code = [
            user.email,
            str(user.id),
            # Intentionally forget the timestamp.
        ]

        url = reverse(
            'email_registration_confirm',
            kwargs={
                'code': get_signer().sign(u':'.join(code)),
            })

        response = self.client.get(url, follow=True)
        self.assertEqual(
            _messages(response),
            [
                'Something went wrong while decoding the'
                ' registration request. Please try again.'
            ])
