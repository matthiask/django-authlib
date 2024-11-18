from django.conf import settings
from django.core.cache import cache
from requests_oauthlib import OAuth1Session


class TwitterOAuthClient:
    authorization_base_url = "https://api.twitter.com/oauth/authenticate"
    client_id = settings.TWITTER_CLIENT_ID
    client_secret = settings.TWITTER_CLIENT_SECRET
    access_token_url = "https://api.twitter.com/oauth/access_token"
    request_token_url = "https://api.twitter.com/oauth/request_token"

    def __init__(self, request):
        self._request = request

    def get_authentication_url(self):
        oauth = OAuth1Session(self.client_id, client_secret=self.client_secret)
        token = oauth.fetch_request_token(self.request_token_url)
        cache.set("oa-token-{}".format(token["oauth_token"]), token, timeout=3600)
        self._request.session["oa_token"] = token["oauth_token"]

        authorization_url = oauth.authorization_url(self.authorization_base_url)

        return authorization_url

    def get_user_data(self):
        oauth = OAuth1Session(self.client_id, client_secret=self.client_secret)
        oauth_response = oauth.parse_authorization_response(
            self._request.build_absolute_uri(self._request.get_full_path())
        )
        verifier = oauth_response.get("oauth_verifier")

        oa_token = self._request.session.pop("oa_token", None)
        if not oa_token:
            return {}

        resource_owner = cache.get(f"oa-token-{oa_token}")
        if not resource_owner:
            return {}

        oauth = OAuth1Session(
            self.client_id,
            client_secret=self.client_secret,
            resource_owner_key=resource_owner.get("oauth_token"),
            resource_owner_secret=resource_owner.get("oauth_token_secret"),
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(self.access_token_url)

        resource_owner_key = oauth_tokens.get("oauth_token")
        resource_owner_secret = oauth_tokens.get("oauth_token_secret")

        oauth = OAuth1Session(
            self.client_id,
            client_secret=self.client_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
        )

        data = oauth.get(
            "https://api.twitter.com/1.1/account/verify_credentials.json"
            "?include_email=true"
        ).json()

        return {"email": data.get("email"), "full_name": data.get("name")}
