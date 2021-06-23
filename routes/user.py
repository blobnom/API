import time
import urllib

from tornado.web import RequestHandler
from PIL import Image, ImageFont, ImageDraw

class UserCardHandler(RequestHandler):
	def initialize(self, client):
		self.api = client
	
	def get(self, username=None):
		user = self.api.fetch_user(username=username)
		if user is None:
			self.set_status(404)
			self.write({"error": "User not found: %s" % username})
			return

		image = self.build_image(user)
		
		self.set_header("Content-Type", "image/png")
		self.write(image)
		self.finish()
	
	def build_image(self, user):
		pp = "{:,.0f}pp".format(user.pp)
		rank = "#{:,} ({}#{:,})".format(user.rank, user.country, user.country_rank)
		country = f"https://osu.ppy.sh/images/flags/{user.country}.png"
		accuracy = "Accuracy: {:.2f}%".format(user.accuracy)
		playcount = "Plays: {:,}".format(user.play_count)
		level = "Level: {:.0f}".format(user.level)

		ranked_score = "{:,}".format(user.ranked_score)
		total_score = "{:,}".format(user.total_score)

		# get player avatar
		urllib.request.urlretrieve(f"https://a.ppy.sh/{str(user.id)}?{time.time()}", f"static/avatars/{str(user.id)}.png")
		urllib.request.urlretrieve(country, f"static/flags/{user.country}.png")

		# make the card
		card = Image.new('RGB', (600, 300), (255, 255, 255))
		avatar = Image.open(f"static/avatars/{user.id}.png")
		avatar = avatar.resize((300, 300))
		c = Image.open(f"static/flags/{user.country}.png")
		c = c.resize((36, 26))

		fnt = ImageFont.truetype("static/fonts/arial.ttf", 24)
		d = ImageDraw.Draw(card)

		# draw user name, avatar and country flag
		card.paste(avatar, (0, 0))
		card.paste(c, (310, 5))
		d.text((351, 5), text=user.username, font=fnt, fill=(0, 0, 0))

		# draw stats
		d.text((310, 34), text=rank, font=fnt, fill=(0, 0, 0))
		d.text((310, 63), text=pp, font=fnt, fill=(0, 0, 0))
		d.text((310, 92), text=accuracy, font=fnt, fill=(0, 0, 0))
		d.text((310, 121), text=playcount, font=fnt, fill=(0, 0, 0))
		d.text((310, 150), text=level, font=fnt, fill=(0, 0, 0))

		d.text((310, 202), text="Ranked & Total Score:", font=fnt, fill=(0, 0, 0))
		d.text((310, 231), text=ranked_score, font=fnt, fill=(0, 0, 0))
		d.text((310, 260), text=total_score, font=fnt, fill=(0, 0, 0))

		# save the card temporarily
		card.save(f"static/user_cards/{user.id}.png")

		with open(f"static/user_cards/{user.id}.png", "rb") as f:
			return f.read()
