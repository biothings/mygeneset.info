from tornado.web import RequestHandler

class mockAppHandler(RequestHandler):
    def get(self):
            self.render("home.html")
