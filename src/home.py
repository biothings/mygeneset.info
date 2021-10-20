from tornado.web import RequestHandler

class mockLogin(RequestHandler):
    def get(self):
            self.render("home.html")
