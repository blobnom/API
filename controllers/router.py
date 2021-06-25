from tornado.web import RequestHandler
from routes import beatmap, user
from osutools import OsuClient
from decouple import config

client = OsuClient(config('OSU_API_KEY'))

class MainHandler(RequestHandler):
	def get(self):
		self.write("<p>" \
		+ "GET /api/user/[username]card" + "<br>" \
		+ "GET /api/user/[username]/scores/recent" + "<br>" \
		+ "GET /api/user/[username]/scores/top" + "<br><br>" \
		+ "GET /api/beatmaps/[map-id]/scores/[username]|~[leaderboard-place]" + "<br>"\
		+ "GET /api/beatmaps/[map-id]/card" \
		+ "</p>")
		self.set_status(200)
		self.finish()

router = [
	(r"/", MainHandler),
	(r"/api/user/(.*)/card", user.UserCardHandler, dict(client=client)),
	(r"/api/user/(.*)/scores/top", user.UserTopScoreHandler, dict(client=client)),
	(r"/api/user/(.*)/scores/recent", user.UserRecentScoreHandler, dict(client=client)),
	(r"/api/beatmaps/(.*)/card", beatmap.BeatmapCardHandler, dict(client=client)),
	(r"/api/beatmaps/(.*)/scores/(.*)", beatmap.BeatmapScoreHandler, dict(client=client))
]
