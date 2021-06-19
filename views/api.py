from flask import Blueprint, escape
from .user.user import user
from .beatmaps.beatmaps import beatmaps

api = Blueprint('api', __name__)
api.register_blueprint(user, url_prefix='/user')
api.register_blueprint(beatmaps, url_prefix='/beatmaps')

@api.route('/')
def endpoints():
    return f'<p>GET /api/user/{escape("<username>")}/card<br>' \
        + f'GET /api/user/{escape("<username>")}/scores/map/{escape("<map-id>")}<br>' \
        + f'GET /api/user/{escape("<username>")}/scores/recent<br>' \
        + f'GET /api/user/{escape("<username>")}/scores/best<br>' \
        + f'GET /api/beatmaps/{escape("<map-id>")}/card</p>'
