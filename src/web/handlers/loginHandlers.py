import json
import hashlib
import logging
import functools
import requests
from urllib.parse import urlparse, urlencode

from biothings.web.handlers import BaseAPIHandler
from tornado import gen, httpclient, ioloop
import tornado.gen
from tornado.httpclient import AsyncHTTPClient
from tornado.auth import OAuth2Mixin, AuthError
from tornado.httputil import url_concat
from tornado.web import RequestHandler


class BaseAuthHandler(BaseAPIHandler, OAuth2Mixin):
    """
    Contains base Auth handler functionalities.
    """
    COOKIE_EXPIRATION = 15

    def get_authenticated_user(self, redirect_uri, client_id, client_secret,
                               code, callback, extra_fields=None):
        """Fetch User info if he has already logged in to the OAuth service."""

        fields = set(["id", "login", "name", "email", "avatar_url"])
        if extra_fields:
            fields.update(extra_fields)

        # Exchange code for access token
        auth_body = {"client_id": client_id, "client_secret": client_secret, "code": code,
                     "redirect_uri": redirect_uri}
        if extra_fields:
            auth_body.update(extra_fields)

        response = requests.post(self._OAUTH_ACCESS_TOKEN_URL, data=auth_body,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded',
                                          'Accept': 'application/json'})
        print(response.request.url)
        print(response.request.body)
        print(response.json())
        """
        auth_body = urlencode({
                "redirect_uri": redirect_uri,
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "extra_params": extra_fields
                })
        """
        #http = AsyncHTTPClient()
        #request = httpclient.HTTPRequest(self._OAUTH_ACCESS_TOKEN_URL,
        #        method="POST", body=auth_body,
        #        headers={'Content-Type': 'application/x-www-form-urlencoded'})
        #response = await http.fetch(request)

        # Get user info
        headers = {'Authorization': 'token {}'.format(response.json()['access_token'])}
        user = requests.get("https://api.github.com/user", headers=headers)

        return json.dumps(user.json()).replace("</", "<\\/")


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
        print(self.web_settings.GITHUB_CLIENT_SECRET)
        if self.get_argument("code", False):
            logging.info('Got authentication code.')
            user = self.get_authenticated_user(
                redirect_uri=redirect_uri,
                client_id=self.web_settings.GITHUB_CLIENT_ID,
                client_secret=self.web_settings.GITHUB_CLIENT_SECRET,
                code=self.get_argument("code"),
                callback=lambda: None
            )
            if user:
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
            client_id=self.web_settings.GITHUB_CLIENT_ID,
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
                client_id=self.web_settings.ORCID_CLIENT_ID,
                client_secret=self.web_settings.ORCID_CLIENT_SECRET,
                code=self.get_argument("code"),
                extra_fields={'grant_type': 'authorization_code'},
                callback=lambda: None
            )
            if user:
                logging.info('logged in user from ORCID: %s', str(user))
                self.set_secure_cookie("user", self.json_encode(user))
            else:
                self.clear_cookie("user")
            self.redirect(self.get_argument("next", "/"))
            return

        # otherwise we need to request an authorization code
        logging.info("Redirecting to login...")
        self.authorize_redirect(
            redirect_uri=redirect_uri,
            client_id=self.web_settings.ORCID_CLIENT_ID,
            extra_params={"scope": self.SCOPE, "response_type": "code"}
        )


class UserInfoHandler(BaseAuthHandler):
    def get(self):
        current_user = self.get_current_user() or {}
        for key in ['access_token', 'id']:
            if key in current_user:
                del current_user[key]
        self.finish(current_user)


class LogoutHandler(BaseAuthHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))
