import os

from tornado.options import define, options
from tornado.web import RequestHandler

from biothings.web.launcher import main

from config import FRONTEND_PATH

#FRONTEND_PATH = "/home/ravila/Projects/mygeneset.info-website"
ASSETS_PATH = os.path.join(FRONTEND_PATH, 'dist/')
define("webapp", default=False, help="Run server with frontend webapp.")


class WebAppHandler(RequestHandler):
    def get(self):
        self.render(os.path.join(FRONTEND_PATH, 'dist/index.html'))


if __name__ == "__main__":
    options.parse_command_line()
    # Run with webapp
    if options.webapp:
        main([
            (r"/", WebAppHandler),
            (r"/css/(.*)", "tornado.web.StaticFileHandler", {
                "path": os.path.join(ASSETS_PATH, "css")}),
            (r"/js/(.*)", "tornado.web.StaticFileHandler", {
                "path": os.path.join(ASSETS_PATH, "js")}),
            (r"/img/(.*)", "tornado.web.StaticFileHandler", {
                "path": os.path.join(ASSETS_PATH, "img")})
        ])
    else:
        # Run only backend
        main()