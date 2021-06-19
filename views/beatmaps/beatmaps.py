import json

from flask import Blueprint, jsonify, redirect, send_file
from ..config import api_key
from PIL import Image, ImageDraw, ImageFont
from osutools.utils import Mods
from osutools.oppai import Oppai

import osutools, urllib.request, time

client = osutools.OsuClient(api_key)
beatmaps = Blueprint('beatmaps', __name__)

def convert_length(s):
    _, __ = divmod(int(s), 60)
    return '{}:{}'.format(_, str(__).zfill(2))

def ranking(n):
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

@beatmaps.route('/')
def endpoints():
    return redirect('/api')

@beatmaps.route('/<id>/card')
def beatmap_card(id):
    b = client.fetch_map(map_id=id)

    if b is None:
        return jsonify({ 'code': 404, 'error': 'Beatmap not found.' })

    title = '{} [{}]'.format(b.song_title, b.difficulty_name)
    artist = '{}'.format(b.artist)
    creator = '{}'.format(b.creator_name)
    length = 'Length: {}'.format(convert_length(b.length))
    bpm = 'BPM: {:.1f}'.format(b.bpm)
    max_combo = 'Combo: {:,}x'.format(b.max_combo)
    status = 'Status: {}'.format(ranking(b.approval.value))

    difficulty = 'Star Rating: {:.2f}'.format(b.star_rating)
    cs = 'Circle Size: {}'.format(b.circle_size)
    ar = 'Approach Rate: {}'.format(b.approach_rate)
    od = 'Overall Difficulty: {}'.format(b.overall_difficulty)
    hp = 'HP Drain: {}'.format(b.hp_drain)

    pp_95 = '95%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=Mods.NM.value, accuracy=95))
    pp_97 = '97%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=Mods.NM.value, accuracy=97))
    pp_98 = '98%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=Mods.NM.value, accuracy=98))
    pp_99 = '99%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=Mods.NM.value, accuracy=99))
    pp_100 = '100%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=Mods.NM.value, accuracy=100))

    # get beatmap background
    try:
        urllib.request.urlretrieve(f'https://assets.ppy.sh/beatmaps/{str(b.mapset_id)}/covers/cover.jpg', 'tmp/beatmap_background.png')
    except urllib.error.HTTPError:
        tmp = Image.new('RGB', (1080, 250), (255, 255, 255))
        tmp.save('tmp/beatmap_background.png')
    urllib.request.urlretrieve(f'https://a.ppy.sh/{str(b.creator_id)}?{time.time()}', 'tmp/beatmap_creator_avatar.png')

    bg = Image.open('tmp/beatmap_background.png')
    bg = bg.resize((1080, 250))
    avatar = Image.open('tmp/beatmap_creator_avatar.png')
    avatar = avatar.resize((128, 128))
    card = Image.new('RGB', (1080, 540), (255, 255, 255))
    card.paste(bg, (0, 0))
    card.paste(avatar, (927, 329))

    fnt = ImageFont.truetype('arial.ttf', 24)
    fnt_sml = ImageFont.truetype('arial.ttf', 12)
    fnt_big = ImageFont.truetype('arial.ttf', 40)
    d = ImageDraw.Draw(card)

    d.text((5, 255), text=title, font=fnt_big, fill=(0, 0, 0))
    d.text((5, 300), text=artist, font=fnt, fill=(0, 0, 0))

    # beatmap creator
    d.text((931, 486), text=creator, font=fnt_sml, fill=(0, 0, 0))
    d.text((931, 457), text='Mapped by', font=fnt, fill=(0, 0, 0))

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

    card.save('tmp/beatmap_card.png')

    return send_file('tmp/beatmap_card.png')