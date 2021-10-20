import json
import logging
from urllib.parse import urlencode

import tornado.gen
from biothings.web.handlers import BaseAPIHandler
from tornado.auth import AuthError, OAuth2Mixin
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat


def authenticated_user(func):
    """
    Decorator for UserGenesetHandler operations.
    Ends request of user is not logged in.
    """
    def _(self, *args, **kwargs):

        if not self.current_user:
            self.send_error(
                message='You must log in first.',
                status_code=401)
            return
        return func(self, *args, **kwargs)
    return _

class BaseAuthHandler(OAuth2Mixin, BaseAPIHandler):
    """
    Contains base Auth handler functionalities.
    """
    COOKIE_EXPIRATION = 15

    async def get_authenticated_user(self, redirect_uri, client_id, client_secret,
                               code, callback, login_method, extra_fields=None):
        """Fetch authorization code if use has logged into the OAuth service."""

        fields = set(["id", "login", "name", "email", "avatar_url"])
        if extra_fields:
            fields.update(extra_fields)

        # Exchange code for access token
        auth_body = {
                "redirect_uri": redirect_uri,
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "extra_params": extra_fields
                }
        if extra_fields:
            auth_body.update(extra_fields)
        http = AsyncHTTPClient()
        response = await http.fetch(self._OAUTH_ACCESS_TOKEN_URL,
                method="POST", body=urlencode(auth_body),
                headers={'Content-Type': 'application/x-www-form-urlencoded',
                         'Accept': 'application/json'})
        if response.error:
            raise AuthError("Auth error: {}".format(response.body))
        access_token = json.loads(response.body)['access_token']

        # Get user info from github
        if login_method == 'github':
            headers = {'Authorization': 'token {}'.format(access_token)}
            response = await http.fetch("https://api.github.com/user",
                                        method="GET", headers=headers)
            user = json.loads(response.body)
            user_fields  = ["login", "avatar_url", "name", "email", "company"]
            user_data = {key: user.get(key) for key in user_fields}
            return json.dumps(user_data)

        # Get user info from orcid
        elif login_method == 'orcid':
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            orcid = json.loads(response.body)['orcid']
            name = json.loads(response.body)['name']
            # This request returns the user email (not strictly necessary for now)
            response = await http.fetch("https://pub.orcid.org/v2.0/{}".format(orcid),
                                        method="GET", headers=headers)
            user = json.loads(response.body)
            email = user.get("person").get("emails").get("email")
            if len(email) >=1:
                email = email[0]['email']
            user_data = {"login": orcid, "name": name, "email": email}
            return json.dumps(user_data)

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return json.loads(user_json.decode('utf-8'))


class GitHubAuthHandler(BaseAuthHandler):
    """
    Handles the user authentication process using GitHub.
    """
    # Override settings from OAuth2Mixin
    _OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
    _USER_DATA_URL = "https://api.github.com/user"
    CALLBACK_PATH = "/login/github"
    SCOPE = "read:user"

    @tornado.gen.coroutine
    def get(self):
        # we can append next to the redirect uri, so the user gets the
        # correct URL on login
        redirect_uri = url_concat(self.request.protocol +
                                  "://" + self.request.host +
                                  self.CALLBACK_PATH,
                                  {"next": self.get_argument('next', '/')})

        # if we have a code, we have been authorized so we can log in
        if self.get_argument("code", False):
            logging.info('Got authentication code.')
            user = yield self.get_authenticated_user(
                redirect_uri=redirect_uri,
                client_id=self.biothings.config.GITHUB_CLIENT_ID,
                client_secret=self.biothings.config.GITHUB_CLIENT_SECRET,
                code=self.get_argument("code"),
                login_method="github",
                callback=lambda: None
            )
            if user:
                logging.info('logged in user from GitHub: %s', str(user))
                logging.info("Setting user cookie.")
                self.set_secure_cookie("user", user)
            else:
                logging.info("Failed to get user info.")
                self.clear_cookie("user")
            self.redirect(self.get_argument("next", "/"))
            return

        # otherwise we need to request an authorization code
        logging.info('Redirecting to login...')
        yield self.authorize_redirect(
            redirect_uri=redirect_uri,
            client_id=self.biothings.config.GITHUB_CLIENT_ID,
            extra_params={"scope": self.SCOPE, "foo": 1}
        )


class ORCIDAuthHandler(BaseAuthHandler):
    """
    Handles the user authentication process using ORCID.
    """

    # Override settings from OAuth2Mixin
    _OAUTH_AUTHORIZE_URL = "https://orcid.org/oauth/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://orcid.org/oauth/token"
    CALLBACK_PATH = "/login/orcid"
    SCOPE = "/authenticate"

    @tornado.gen.coroutine
    def get(self):
        # we can append next to the redirect uri, so the user gets the
        # correct URL on login
        redirect_uri = url_concat(self.request.protocol +
                                  "://" + self.request.host +
                                  self.CALLBACK_PATH,
                                  {"next": self.get_argument('next', '/')})


        # if we have a code, we have been authorized so we can log in
        if self.get_argument("code", False):
            user = yield self.get_authenticated_user(
                redirect_uri=redirect_uri,
                client_id=self.biothings.config.ORCID_CLIENT_ID,
                client_secret=self.biothings.config.ORCID_CLIENT_SECRET,
                code=self.get_argument("code"),
                extra_fields={'grant_type': 'authorization_code'},
                login_method="orcid",
                callback=lambda: None
            )
            if user:
                logging.info('logged in user from ORCID: %s', str(user))
                logging.info("Setting user cookie.")
                self.set_secure_cookie("user", user)
            else:
                self.clear_cookie("user")
            self.redirect(self.get_argument("next", "/"))
            return

        # otherwise we need to request an authorization code
        logging.info("Redirecting to login...")
        yield self.authorize_redirect(
            redirect_uri=redirect_uri,
            client_id=self.biothings.config.ORCID_CLIENT_ID,
            extra_params={"scope": self.SCOPE, "response_type": "code"}
        )


class UserInfoHandler(BaseAuthHandler):
    """Handler for /user endpoint."""
    def get(self):
        current_user = self.get_current_user() or {}
        for key in ['access_token', 'id']:
            if key in current_user:
                del current_user[key]
        self.finish(current_user)


class LogoutHandler(BaseAuthHandler):
    """"Handler for /logout endpoint."""
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))
