from tornado.web import RequestHandler

class XSRFToken(RequestHandler):
    def get(self):
            self.render("xsrf_form.html")
