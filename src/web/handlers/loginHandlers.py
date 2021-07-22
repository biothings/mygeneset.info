import json
import hashlib
from urllib.parse import urlparse

from biothings.web.handlers import BaseAPIHandler, BiothingHandler
from authlib.integrations.requests_client import OAuth2Session

from tornado.httputil import url_concat
from tornado.web import RequestHandler
from tornado.web import Finish, HTTPError

class BaseAuthHandler(BaseAPIHandler, RequestHandler):
    """
    Contains base Auth handler functionalities.
    """
    COOKIE_EXPIRATION = 15

    def _set_new_user_cookie(self, user):
        """
        Sets a new secret cookie for the successfully authenticated user.
        Arguments:
            user (auth.models.User): Successfully authenticated user.
        """
        cookie_expires_after = "COOKIE_EXPIRATION"
        self.set_secure_cookie(
            "_pk", str(user.id), expires_days=cookie_expires_after
        )


class GitHubAuthHandler(BaseAuthHandler):
    """
    Handles the user authentication process using Github.
    """

    GITHUB_CALLBACK_PATH = "/login"

    def get(self):
        """Redirect to github login page."""
        client_id = self.web_settings.GITHUB_CLIENT_ID
        client_secret = self.web_settings.GITHUB_CLIENT_SECRET
        auth_base_url = "https://github.com/login/oauth/authorize"

        github = OAuth2Session(client_id, client_secret)
        auth_url, state = github.create_authorization_url(auth_base_url)
        self.redirect(auth_url)

    def post(self):
        client_id = self.web_settings.GITHUB_CLIENT_ID
        client_secret = self.web_settings.GITHUB_CLIENT_SECRET
        token_url = "https://github.com/login/oauth/access_token"

        state = self.get_query_argument("state")
        state_md5_hash = hashlib.md5(state.encode('UTF-8')).hexdigest()
        if state_mdd5_hash:

            github = OAuth2Session(client_id)
            try:
                github.fetch_token(
                    token_url,
                    client_secret=client_secret,
                    authorization_response=self.request.full_url()
                )
            except Exception:
                self.render(
                    f"{APP_NAME}/login.html",
                    auth_error="Failed to sign in. Please try again!"
                )
                return

            github_user_response = github.get('https://api.github.com/user')

            if github_user_response.status_code != requests.codes.OK:
                self.render(
                    f"{APP_NAME}/login.html",
                    auth_error="Failed to sign in. Please try again!"
                )
                return
            else:
                github_user = github_user_response.json()
                user = self._update_or_create_user(
                    identity_provider=UserIdentityProvider.GITHUB,
                    identity_provider_user_id=str(github_user["id"]),
                    username=github_user["login"],
                    full_name=github_user["name"]
                )

                self._set_new_user_cookie(user)

                self.redirect(url_concat(self.request.protocol + "://" + self.request.host +
                              self.GITHUB_CALLBACK_PATH, {"next": self.get_argument('next', '/')}))
        else:
            self.render(
                f"{APP_NAME}/login.html",
                auth_error="Bad/Not Allowed sign in attempt. Please try again!"
            )

class ORCIDAuthHandler(BaseAuthHandler):
    """
    Handles the user authentication process using Github.
    """

    def post(self):
        """Redirect to orcid login page."""
        client_id = self.web_settings.ORCID_CLIENT_ID
        auth_base_url = "https://orcid.org/oauth/authorize"

        """
        orcid = OAuth2Session(client_id)
        auth_url, state = orcid.authorization_url(auth_base_url)
        state_md5_hash = hashlib.md5(state.encode('UTF-8')).hexdigest()
        self.redirect(auth_url)
        """
        redirect_uri = url_concat(self.request.protocol + "://" + self.request.host,
                                  {"next": self.get_argument('next', '/')})
        self.redirect(
            f"{auth_base_url}?"
            f"client_id={client_id}&"
            f"response_type=code&"
            f"scope=/authenticate&"
            f"redirect_uri="
            f"http://localhost:8000?next=/"
	)



class LogoutHandler(BaseAuthHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))
