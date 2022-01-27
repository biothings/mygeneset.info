import json

from biothings.web.auth.authn import BioThingsAuthenticationProviderInterface


class UserCookieAuthProvider(BioThingsAuthenticationProviderInterface):
    WWW_AUTHENTICATE_HEADER = 'None'

    def __init__(self, handler, cookie_name='user'):
        super(UserCookieAuthProvider, self).__init__(handler)
        self.cookie_name = cookie_name

    def get_current_user(self):
        user = self.handler.get_secure_cookie(self.cookie_name)
        if not user:
            return None
        return json.loads(user.decode())
