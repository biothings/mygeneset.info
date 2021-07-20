import json
import hashlib
import os

from biothings.web.handlers import BaseAPIHandler, BiothingHandler
from requests_oauthlib import OAuth2Session
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
    __client_id = os.environ.get("GITHUB_CLIENT_ID")
    __client_secret = os.environ.get("GITHUB_CLIENT_SECRET")

    def post(self):
        """Redirect to github login page."""

        auth_base_url = "https://github.com/login/oauth/authorize"
        github = OAuth2Session(self.__client_id)

        auth_url, state = github.authorization_url(auth_base_url)
        state_md5_hash = hashlib.md5(state.encode('UTF-8')).hexdigest()

        self.redirect(auth_url)

    def get(self):
        token_url = "https://github.com/login/oauth/access_token"
        state = self.get_query_argument("state")
        state_md5_hash = hashlib.md5(state.encode('UTF-8')).hexdigest()
        if state_mdd5_hash:

            github = OAuth2Session(self.__client_id)
            try:
                github.fetch_token(
                    token_url,
                    client_secret=self.__client_secret,
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

                self.redirect(self.reverse_url("user_detail", user.id))
        else:
            self.render(
                f"{APP_NAME}/login.html",
                auth_error="Bad/Not Allowed sign in attempt. Please try again!"
            )

class ORCIDAuthHandler(BaseAuthHandler):
    """
    Handles the user authentication process using Github.
    """
    __client_id = os.environ.get("GITHUB_CLIENT_ID")
    __client_secret = os.environ.get("GITHUB_CLIENT_SECRET")

