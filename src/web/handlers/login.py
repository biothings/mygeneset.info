from biothings.web.auth.authn import BioThingsAuthnMixin
from biothings.web.handlers import BaseAPIHandler
from tornado.web import HTTPError

class UserInfoHandler(BioThingsAuthnMixin, BaseAPIHandler):
    """"Handler for /user_info endpoint."""
    def get(self):
        # Check for user cookie
        if self.current_user:
            self.write(self.current_user)
        else:
            # Check for WWW-authenticate header
            header = self.get_www_authenticate_header()
            if header:
                self.clear()
                self.set_header('WWW-Authenticate', header)
                self.set_status(401, "Unauthorized")
                # raising HTTPError will cause headers to be emptied
                self.finish()
            else:
                raise HTTPError(403)


class LogoutHandler(BaseAPIHandler):
    """"Handler for /logout endpoint."""
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))