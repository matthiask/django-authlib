from django.conf import settings

from requests_oauthlib import OAuth2Session

from .base import OAuthClient


class FacebookOAuth2Client(OAuthClient):
    authorization_base_url = 'https://www.facebook.com/dialog/oauth'
    token_url = 'https://graph.facebook.com/oauth/access_token'
    scope = ['email']
    client_id = settings.FACEBOOK_CLIENT_ID
    client_secret = settings.FACEBOOK_CLIENT_SECRET

    def __init__(self, request):
        self._request = request
        self._session = OAuth2Session(
            self.client_id,
            scope=self.scope,
            redirect_uri=request.build_absolute_uri('.'),
        )

    def get_authentication_url(self):
        authorization_url, self._state = self._session.authorization_url(
            self.authorization_base_url,
            access_type='online',  # Only right now.
            # approval_prompt='force',  # Maybe not, later.
        )

        return authorization_url

    def get_user_data(self):
        self._session.fetch_token(
            self.token_url,
            client_secret=self.client_secret,
            authorization_response=self._request.build_absolute_uri(
                self._request.get_full_path()),
        )
        data = self._session.get(
            'https://graph.facebook.com/v2.8/me',
            params={'fields': 'email,name'},
        ).json()

        return {
            'email': data.get('email'),
            'full_name': data.get('name'),
        }
