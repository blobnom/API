import os
import time
import urllib

from tornado.web import RequestHandler
from PIL import Image, ImageFont, ImageDraw
from osutools.utils import Mods
from osutools.oppai import Oppai

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
		self.set_status(200)

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

class UserRecentScoreHandler(RequestHandler):
	def initialize(self, client):
		self.api = client

	def get(self, username):
		if username == "":
			self.set_status(502)
			self.write({"error": "Please provide a username"})

		u = self.api.fetch_user(username=username)
		if u is None:
			self.set_status(404)
			self.write({"error": "User not found: %s" % username})
			return

		scores = u.fetch_recent(limit=1)
		if scores is None:
			self.set_status(404)
			self.write({"error": "No scores found"})
			return

		self.build_image(u, scores[0])
		image = self.get_image(scores[0])

		self.set_header("Content-Type", "image/png")
		self.set_status(200)

		self.write(image)
		self.finish()

	def build_image(self, u, score):
		map = score.fetch_map()

		pp = "{:,.2f}pp".format(score.pp)
		points = "Score: {:,}".format(score.score)
		combo = "Combo: {:,}".format(score.max_combo)
		accuracy = "Accuracy: {:.2f}%".format(score.accuracy_dec * 100)
		mods = "Mods: {}".format(score.mods)
		title = "{} [{}]".format(map.song_title, map.difficulty_name)
		artist = "{}".format(map.artist)
		player = "{}".format(u.username)

		pp_95 = "95%: {:,.2f}pp".format(
			Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=95))
		pp_97 = "97%: {:,.2f}pp".format(
			Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=97))
		pp_98 = "98%: {:,.2f}pp".format(
			Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=98))
		pp_99 = "99%: {:,.2f}pp".format(
			Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=99))
		pp_100 = "100%: {:,.2f}pp".format(
			Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=100))

		# get beatmap background
		try:
			urllib.request.urlretrieve(f"https://assets.ppy.sh/beatmaps/{str(map.mapset_id)}/covers/cover.jpg",
									   f"static/backgrounds/{map.mapset_id}.png")
		except urllib.error.HTTPError:
			tmp = Image.new("RGB", (1080, 250), (255, 255, 255))
			tmp.save(f"static/backgrounds/{map.mapset_id}.png")
		urllib.request.urlretrieve(f"https://a.ppy.sh/{str(u.id)}?{time.time()}",
								   f"static/avatars/{u.id}.png")

		bg = Image.open(f"static/backgrounds/{map.mapset_id}.png")
		bg = bg.resize((1080, 250))
		avatar = Image.open(f"static/avatars/{u.id}.png")
		avatar = avatar.resize((128, 128))
		rank = Image.open("static/ranks/{}.png".format(score.rank))
		rank = rank.resize((156, 156))
		card = Image.new('RGBA', (1080, 540), (255, 255, 255, 255))
		card.paste(bg, (0, 0))
		card.paste(avatar, (927, 329))
		card.paste(rank, (75, 350), rank)

		fnt = ImageFont.truetype("static/fonts/arial.ttf", 24)
		fnt_sml = ImageFont.truetype("static/fonts/arial.ttf", 12)
		fnt_big = ImageFont.truetype("static/fonts/arial.ttf", 40)
		d = ImageDraw.Draw(card)

		d.text((5, 255), text=title, font=fnt_big, fill=(0, 0, 0))
		d.text((5, 300), text=artist, font=fnt, fill=(0, 0, 0))
		# beatmap creator
		d.text((931, 486), text=player, font=fnt_sml, fill=(0, 0, 0))
		d.text((931, 457), text="Played by", font=fnt, fill=(0, 0, 0))

		# score stats
		d.text((310, 358), text=points, font=fnt, fill=(0, 0, 0))
		d.text((310, 387), text=combo, font=fnt, fill=(0, 0, 0))
		d.text((310, 416), text=accuracy, font=fnt, fill=(0, 0, 0))
		d.text((310, 445), text=mods, font=fnt, fill=(0, 0, 0))
		d.text((310, 474), text=pp, font=fnt, fill=(0, 0, 0))

		# beatmap pp
		d.text((605, 358), text=pp_95, font=fnt, fill=(0, 0, 0))
		d.text((605, 387), text=pp_97, font=fnt, fill=(0, 0, 0))
		d.text((605, 416), text=pp_98, font=fnt, fill=(0, 0, 0))
		d.text((605, 445), text=pp_99, font=fnt, fill=(0, 0, 0))
		d.text((605, 474), text=pp_100, font=fnt, fill=(0, 0, 0))
		card.save(f"static/scores_recent/{score.user_id}.png")

	def get_image(self, score):
		with open(f"static/scores_recent/{score.user_id}.png", "rb") as f:
			return f.read()

class UserTopScoreHandler(RequestHandler):
	def initialize(self, client):
		self.api = client

	def get(self, username):
		if username == "":
			self.set_status(502)
			self.write({"error": "Please provide a username"})

		u = self.api.fetch_user(username=username)
		if u is None:
			self.set_status(404)
			self.write({"error": "User not found: %s" % username})
			return

		scores = u.fetch_best(limit=1)
		if scores is None:
			self.set_status(404)
			self.write({"error": "No scores found"})
			return

		self.build_image(u, scores[0])
		image = self.get_image(scores[0])

		self.set_header("Content-Type", "image/png")
		self.set_status(200)

		self.write(image)
		self.finish()

	def build_image(self, u, score):
		map = score.fetch_map()

		pp = "{:,.2f}pp".format(score.pp)
		points = "Score: {:,}".format(score.score)
		combo = "Combo: {:,}".format(score.max_combo)
		accuracy = "Accuracy: {:.2f}%".format(score.accuracy_dec * 100)
		mods = "Mods: {}".format(score.mods)
		title = "{} [{}]".format(map.song_title, map.difficulty_name)
		artist = "{}".format(map.artist)
		player = "{}".format(u.username)

		pp_95 = "95%: {:,.2f}pp".format(
			Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=95))
		pp_97 = "97%: {:,.2f}pp".format(
			Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=97))
		pp_98 = "98%: {:,.2f}pp".format(
			Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=98))
		pp_99 = "99%: {:,.2f}pp".format(
			Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=99))
		pp_100 = "100%: {:,.2f}pp".format(
			Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=100))

		# get beatmap background
		try:
			urllib.request.urlretrieve(f"https://assets.ppy.sh/beatmaps/{str(map.mapset_id)}/covers/cover.jpg",
									   f"static/backgrounds/{map.mapset_id}.png")
		except urllib.error.HTTPError:
			tmp = Image.new("RGB", (1080, 250), (255, 255, 255))
			tmp.save(f"static/backgrounds/{map.mapset_id}.png")
		urllib.request.urlretrieve(f"https://a.ppy.sh/{str(u.id)}?{time.time()}",
								   f"static/avatars/{u.id}.png")

		bg = Image.open(f"static/backgrounds/{map.mapset_id}.png")
		bg = bg.resize((1080, 250))
		avatar = Image.open(f"static/avatars/{u.id}.png")
		avatar = avatar.resize((128, 128))
		rank = Image.open("static/ranks/{}.png".format(score.rank))
		rank = rank.resize((156, 156))
		card = Image.new('RGBA', (1080, 540), (255, 255, 255, 255))
		card.paste(bg, (0, 0))
		card.paste(avatar, (927, 329))
		card.paste(rank, (75, 350), rank)

		fnt = ImageFont.truetype("static/fonts/arial.ttf", 24)
		fnt_sml = ImageFont.truetype("static/fonts/arial.ttf", 12)
		fnt_big = ImageFont.truetype("static/fonts/arial.ttf", 40)
		d = ImageDraw.Draw(card)

		d.text((5, 255), text=title, font=fnt_big, fill=(0, 0, 0))
		d.text((5, 300), text=artist, font=fnt, fill=(0, 0, 0))
		# beatmap creator
		d.text((931, 486), text=player, font=fnt_sml, fill=(0, 0, 0))
		d.text((931, 457), text="Played by", font=fnt, fill=(0, 0, 0))

		# score stats
		d.text((310, 358), text=points, font=fnt, fill=(0, 0, 0))
		d.text((310, 387), text=combo, font=fnt, fill=(0, 0, 0))
		d.text((310, 416), text=accuracy, font=fnt, fill=(0, 0, 0))
		d.text((310, 445), text=mods, font=fnt, fill=(0, 0, 0))
		d.text((310, 474), text=pp, font=fnt, fill=(0, 0, 0))

		# beatmap pp
		d.text((605, 358), text=pp_95, font=fnt, fill=(0, 0, 0))
		d.text((605, 387), text=pp_97, font=fnt, fill=(0, 0, 0))
		d.text((605, 416), text=pp_98, font=fnt, fill=(0, 0, 0))
		d.text((605, 445), text=pp_99, font=fnt, fill=(0, 0, 0))
		d.text((605, 474), text=pp_100, font=fnt, fill=(0, 0, 0))
		card.save(f"static/scores_top/{score.user_id}.png")

	def get_image(self, score):
		with open(f"static/scores_top/{score.user_id}.png", "rb") as f:
			return f.read()
