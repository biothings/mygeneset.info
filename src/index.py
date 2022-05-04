import os

from tornado.options import define, options
from tornado.web import RequestHandler

from biothings.web.launcher import main

from config import FRONTEND_PATH

ASSETS_PATH = os.path.join(FRONTEND_PATH, 'dist/')
define("webapp", default=False, help="Run server with frontend webapp.")


class WebAppHandler(RequestHandler):
    def get(self):
        self.render(os.path.join(ASSETS_PATH, 'index.html'))


class NotFoundHandler(RequestHandler):
    def get(self):
        self.render(os.path.join(ASSETS_PATH, "404.html"))


if __name__ == "__main__":
    options.parse_command_line()
    # Run with webapp
    if options.webapp:
        main([
            (r"/", WebAppHandler),
            (r"/css/(.*)", "tornado.web.StaticFileHandler", {
                "path": os.path.join(ASSETS_PATH, "css")
            }),
            (r"/js/(.*)", "tornado.web.StaticFileHandler", {
                "path": os.path.join(ASSETS_PATH, "js")
            }),
            (r"/img/(.*)", "tornado.web.StaticFileHandler", {
                "path": os.path.join(ASSETS_PATH, "img")
            }),
            (r"/.*", NotFoundHandler)
        ])
    else:
        # Run only backend
        main()
