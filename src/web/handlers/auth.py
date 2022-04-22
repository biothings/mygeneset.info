import json
import logging

from biothings.web.auth.oauth_mixins import GithubOAuth2Mixin, OrcidOAuth2Mixin
from biothings.web.handlers import BaseAPIHandler
from tornado.httputil import url_concat


class ORCIDLoginHandler(BaseAPIHandler, OrcidOAuth2Mixin):
    SCOPES = ['/authenticate', 'openid']
    CALLBACK_PATH = "/login/orcid"

    async def get(self):
        CLIENT_ID = self.biothings.config.ORCID_CLIENT_ID
        CLIENT_SECRET = self.biothings.config.ORCID_CLIENT_SECRET
        redirect_uri = url_concat(self.biothings.config.WEB_HOST +
                                  self.CALLBACK_PATH,
                                  {"next": self.get_argument('next', '/')})
        code = self.get_argument('code', None)
        if code is None:
            logging.info('Redirecting to login...')
            self.authorize_redirect(
                redirect_uri=redirect_uri,
                client_id=CLIENT_ID,
                scope=self.SCOPES,
            )
        else:
            logging.info("got code, try to get token")
            token = await self.orcid_get_oauth2_token(client_id=CLIENT_ID,
                                                      client_secret=CLIENT_SECRET,
                                                      code=code)
            # user = await self.orcid_get_authenticated_user_oidc(token)
            user = await self.orcid_get_authenticated_user_record(token, token['orcid'])
            user = self._format_user_record(user)
            logging.info("Got user info: {}".format(user))
            if user:
                logging.info("Setting user cookie.")
                self.set_secure_cookie("user", user)
            else:
                logging.info("Failed to get user info.")
                self.clear_cookie("user")
            self.redirect(self.get_argument('next', '/'))

    def _format_user_record(self, user):
        user_data = {}
        user_data['username'] = user.get("orcid-identifier", {}).get("path")
        if not user_data['username']:
            return
        # Only first name is required when registering for ORCID
        first_name = user.get("person", {}).get("name", {}).get("given-names", {}).get("value")
        last_name = user.get("person", {}).get("name", {}).get("family-name", {}).get("value")
        user_data['name'] = first_name
        if last_name:
            user_data['name'] = first_name + " " + last_name
        # email
        email = user.get("person", {}).get("emails", {}).get("email")
        if email and len(email) >=1:
            user_data['email'] = email[0]['email']
        employment = user.get("activities-summary", {}).get("employments", {}).get("employment-summary")
        if employment and len(employment) >= 1:
            user_data['organization'] = employment[0]['organization']['name']
        user_data['provider'] = "ORCID"
        return json.dumps(user_data)


class GitHubLoginHandler(BaseAPIHandler, GithubOAuth2Mixin):
    SCOPES = []
    CALLBACK_PATH = "/login/github"

    async def get(self):
        CLIENT_ID = self.biothings.config.GITHUB_CLIENT_ID
        CLIENT_SECRET = self.biothings.config.GITHUB_CLIENT_SECRET
        code = self.get_argument('code', None)
        redirect_uri = url_concat(self.biothings.config.WEB_HOST +
                                  self.CALLBACK_PATH,
                                  {"next": self.get_argument('next', '/')})
        if code is None:
            logging.info('Redirecting to login...')
            self.authorize_redirect(
                redirect_uri=redirect_uri,
                client_id=CLIENT_ID,
                scope=self.SCOPES,
            )
        else:
            logging.info("got code, try to get token")
            token = await self.github_get_oauth2_token(client_id=CLIENT_ID,
                                                       client_secret=CLIENT_SECRET,
                                                       code=code)
            user = await self.github_get_authenticated_user(token['access_token'])
            user = self._format_user_record(user)
            logging.info("Got user info: {}".format(user))
            if user:
                logging.info("Setting user cookie.")
                self.set_secure_cookie("user", user)
            else:
                logging.info("Failed to get user info.")
                self.clear_cookie("user")
            self.redirect(self.get_argument('next', '/'))

    def _format_user_record(self, user):
        user_data = {}
        user_data['username'] = user.get('login')
        if not user_data['username']:
            return
        if user.get('name'):
            user_data['name'] = user['name']
        if user.get('email'):
            user_data['email'] = user['email']
        if user.get('avatar_url'):
            user_data['avatar_url'] = user['avatar_url']
        if user.get('company'):
            user_data['organization'] = user['company']
        user_data['provider'] = "GitHub"
        return json.dumps(user_data)
