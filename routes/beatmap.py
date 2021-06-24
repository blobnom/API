import os
import time
import urllib

from osutools.utils import Mods
from osutools.oppai import Oppai
from tornado.web import RequestHandler
from PIL import Image, ImageFont, ImageDraw

class BeatmapCardHandler(RequestHandler):
	def initialize(self, client):
		self.api = client

	def get(self, mapid=None):
		map = self.api.fetch_map(map_id=mapid)
		if map is None:
			self.set_status(404)
			self.write({"error": "Beatmap not found: %s" % mapid})
			return

		if not os.path.isfile(f"static/beatmap_cards/{map.beatmap_id}.png"):
			self.build_image(map)

		image = self.get_image(map)

		self.set_header("Content-Type", "image/png")
		self.set_status(200)

		self.write(image)
		self.finish()

	def build_image(self, map):
		title = "{} [{}]".format(map.song_title, map.difficulty_name)
		artist = "{}".format(map.artist)
		creator = "{}".format(map.creator_name)
		length = "Length: {}".format(self.convert_length(map.length))
		bpm = "BPM: {:.1f}".format(map.bpm)
		max_combo = "Combo: {:,}x".format(map.max_combo)
		status = "Status: {}".format(self.ranking(map.approval.value))

		difficulty = "Star Rating: {:.2f}".format(map.star_rating)
		cs = "Circle Size: {}".format(map.circle_size)
		ar = "Approach Rate: {}".format(map.approach_rate)
		od = "Overall Difficulty: {}".format(map.overall_difficulty)
		hp = "HP Drain: {}".format(map.hp_drain)

		pp_95 = "95%: {:,.2f}pp".format(Oppai.calculate_pp_from_url(map.download_url, mods=Mods.NM.value, accuracy=95))
		pp_97 = "97%: {:,.2f}pp".format(Oppai.calculate_pp_from_url(map.download_url, mods=Mods.NM.value, accuracy=97))
		pp_98 = "98%: {:,.2f}pp".format(Oppai.calculate_pp_from_url(map.download_url, mods=Mods.NM.value, accuracy=98))
		pp_99 = "99%: {:,.2f}pp".format(Oppai.calculate_pp_from_url(map.download_url, mods=Mods.NM.value, accuracy=99))
		pp_100 = "100%: {:,.2f}pp".format(Oppai.calculate_pp_from_url(map.download_url, mods=Mods.NM.value, accuracy=100))

		# get beatmap background
		try:
			urllib.request.urlretrieve(f"https://assets.ppy.sh/beatmaps/{str(map.mapset_id)}/covers/cover.jpg",
									   f"static/backgrounds/{map.mapset_id}.png")
		except urllib.error.HTTPError:
			tmp = Image.new("RGB", (1080, 250), (255, 255, 255))
			tmp.save(f"static/backgrounds/{map.mapset_id}.png")
		urllib.request.urlretrieve(f"https://a.ppy.sh/{str(map.creator_id)}?{time.time()}",
								   f"static/avatars/{map.creator_id}.png")

		bg = Image.open(f"static/backgrounds/{map.mapset_id}.png")
		bg = bg.resize((1080, 250))
		avatar = Image.open(f"static/avatars/{map.creator_id}.png")
		avatar = avatar.resize((128, 128))
		card = Image.new("RGB", (1080, 540), (255, 255, 255))
		card.paste(bg, (0, 0))
		card.paste(avatar, (927, 329))

		fnt = ImageFont.truetype("static/fonts/arial.ttf", 24)
		fnt_sml = ImageFont.truetype("static/fonts/arial.ttf", 12)
		fnt_big = ImageFont.truetype("static/fonts/arial.ttf", 40)
		d = ImageDraw.Draw(card)

		d.text((5, 255), text=title, font=fnt_big, fill=(0, 0, 0))
		d.text((5, 300), text=artist, font=fnt, fill=(0, 0, 0))

		# beatmap creator
		d.text((931, 486), text=creator, font=fnt_sml, fill=(0, 0, 0))
		d.text((931, 457), text="Mapped by", font=fnt, fill=(0, 0, 0))

		# difficulty stats
		d.text((5, 358), text=difficulty, font=fnt, fill=(0, 0, 0))
		d.text((5, 387), text=cs, font=fnt, fill=(0, 0, 0))
		d.text((5, 416), text=ar, font=fnt, fill=(0, 0, 0))
		d.text((5, 445), text=od, font=fnt, fill=(0, 0, 0))
		d.text((5, 474), text=hp, font=fnt, fill=(0, 0, 0))

		# beatmap stats
		d.text((310, 358), text=status, font=fnt, fill=(0, 0, 0))
		d.text((310, 387), text=length, font=fnt, fill=(0, 0, 0))
		d.text((310, 416), text=bpm, font=fnt, fill=(0, 0, 0))
		d.text((310, 445), text=max_combo, font=fnt, fill=(0, 0, 0))

		# beatmap pp
		d.text((605, 358), text=pp_95, font=fnt, fill=(0, 0, 0))
		d.text((605, 387), text=pp_97, font=fnt, fill=(0, 0, 0))
		d.text((605, 416), text=pp_98, font=fnt, fill=(0, 0, 0))
		d.text((605, 445), text=pp_99, font=fnt, fill=(0, 0, 0))
		d.text((605, 474), text=pp_100, font=fnt, fill=(0, 0, 0))

		card.save(f"static/beatmap_cards/{map.beatmap_id}.png")

	def get_image(self, map):
		with open(f"static/beatmap_cards/{map.beatmap_id}.png", "rb") as f:
			return f.read()

	def convert_length(self, s):
		_, __ = divmod(int(s), 60)
		return '{}:{}'.format(_, str(__).zfill(2))

	def ranking(self, n):
		if n == -2:
			return 'Graveyard'
		elif n == -1:
			return 'WIP'
		elif n == 0:
			return 'Pending'
		elif n == 1:
			return 'Ranked'
		elif n == 2:
			return 'Approved'
		elif n == 3:
			return 'Qualified'
		elif n == 4:
			return 'Loved'
		else:
			return 'Unknown'

class BeatmapScoreHandler(RequestHandler):
	def initialize(self, client):
		self.api = client

	def get(self, mapid, username):
		if username == "":
			self.set_status(502)
			self.write({"error":"Please provide a username"})
			return

		index = 0
		if username[0] == "~" and len(username) > 1:
			index = username.split("~")[1]
			if index.isdigit():
				index = int(index)
			else:
				self.set_status(502)
				self.write({"error":"Please provide a number as play index"})
				return

		map = self.api.fetch_map(map_id=mapid)
		if map is None:
			self.set_status(404)
			self.write({"error": "Beatmap not found: %s" % mapid})
			return

		if index != 0:
			scores = map.fetch_scores()
			if scores is None or index > len(scores):
				self.set_status(502)
				self.write({"error":"No scores found"})
				return

			score = scores[index-1]
		else:
			scores = map.fetch_scores(username=username)
			if scores is None:
				self.set_status(502)
				self.write({"error":"No scores found"})
				return

			score = scores[0]

		if not os.path.isfile(f"static/beatmap_scores/{map.beatmap_id}:{score.user_id}:{score.timestamp}.png"):
			self.build_image(map, score)

		image = self.get_image(map, score)

		self.set_header("Content-Type", "image/png")
		self.set_status(200)

		self.write(image)
		self.finish()

	def build_image(self, map, score):
		u = score.fetch_user()
		
		pp = "{:,.2f}pp".format(score.pp)
		points = "Score: {:,}".format(score.score)
		combo = "Combo: {:,}".format(score.max_combo)
		accuracy = "Accuracy: {:.2f}%".format(score.accuracy_dec*100)
		mods = "Mods: {}".format(score.mods)
		title = "{} [{}]".format(map.song_title, map.difficulty_name)
		artist = "{}".format(map.artist)
		player = "{}".format(u.username)
		
		pp_95 = "95%: {:,.2f}pp".format(Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=95))
		pp_97 = "97%: {:,.2f}pp".format(Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=97))
		pp_98 = "98%: {:,.2f}pp".format(Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=98))
		pp_99 = "99%: {:,.2f}pp".format(Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=99))
		pp_100 = "100%: {:,.2f}pp".format(Oppai.calculate_pp_from_url(map.download_url, mods=score.mods.value, accuracy=100))
		
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
		d.text((310, 358), text=score, font=fnt, fill=(0, 0, 0))
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
		card.save(f"static/beatmap_scores/{map.beatmap_id}:{score.user_id}:{score.timestamp}.png")

	def get_image(self, map, score):
		with open(f"static/beatmap_scores/{map.beatmap_id}:{score.user_id}:{score.timestamp}.png") as f:
			return f.read()
