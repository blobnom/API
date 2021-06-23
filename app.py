import os

from controllers.router import router
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

settings = dict(
	static_path=os.path.join(os.path.dirname(__file__), "static")
)

def make_app():
	return Application(router, **settings)

if __name__ == "__main__":
	app = make_app()
	app.listen(8888)
	print("Listening on 8888...")
	IOLoop.current().start()