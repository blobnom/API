from flask import Blueprint, jsonify, redirect, send_file
from ..config import api_key
from ..const import country_url
from PIL import Image, ImageDraw, ImageFont
from osutools.oppai import Oppai
from osutools.utils import Mods

import osutools, urllib.request, time, json

client = osutools.OsuClient(api_key)
user = Blueprint('user', __name__)

@user.route('/')
def endpoints():
    return redirect('/api')

@user.route('/<username>/scores/recent')
def recent_score(username):
    u = client.fetch_user(username=username)

    if u is None:
        return jsonify({ 'code': 404, 'error': 'User not found.' })

    scores = u.fetch_recent(limit=1)

    if scores is None:
        return jsonify({'code': 502, 'error': 'No scores found.'})
    else:
        scores = scores[0]

    b = client.fetch_map(scores.map_id)

    pp = '{:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value,
        accuracy=scores.accuracy_dec*100, misses=scores.misses, max_combo=scores.max_combo))
    score = 'Score: {:,}'.format(scores.score)
    combo = f'Combo: {scores.max_combo:,}'
    accuracy = f'Accuracy: {scores.accuracy_dec * 100:.2f}%'
    mods = f'Mods: {scores.mods}'
    title = '{} [{}]'.format(b.song_title, b.difficulty_name)
    artist = '{}'.format(b.artist)
    player = '{}'.format(u.username)

    pp_95 = '95%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=95))
    pp_97 = '97%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=97))
    pp_98 = '98%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=98))
    pp_99 = '99%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=99))
    pp_100 = '100%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=100))

    # get beatmap background
    try:
        urllib.request.urlretrieve(f'https://assets.ppy.sh/beatmaps/{str(b.mapset_id)}/covers/cover.jpg',
                                   'tmp/score_beatmap_background.png')
    except urllib.error.HTTPError:
        tmp = Image.new('RGB', (1080, 250), (255, 255, 255))
        tmp.save('tmp/score_beatmap_background.png')
    urllib.request.urlretrieve(f'https://a.ppy.sh/{str(u.id)}?{time.time()}', 'tmp/score_user_avatar.png')

    bg = Image.open('tmp/score_beatmap_background.png')
    bg = bg.resize((1080, 250))
    avatar = Image.open('tmp/score_user_avatar.png')
    avatar = avatar.resize((128, 128))
    rank = Image.open('static/ranks/{}.png'.format(scores.rank))
    rank = rank.resize((156, 156))
    card = Image.new('RGBA', (1080, 540), (255, 255, 255, 255))
    card.paste(bg, (0, 0))
    card.paste(avatar, (927, 329))
    card.paste(rank, (75, 350), rank)

    fnt = ImageFont.truetype('arial.ttf', 24)
    fnt_sml = ImageFont.truetype('arial.ttf', 12)
    fnt_big = ImageFont.truetype('arial.ttf', 40)
    d = ImageDraw.Draw(card)

    d.text((5, 255), text=title, font=fnt_big, fill=(0, 0, 0))
    d.text((5, 300), text=artist, font=fnt, fill=(0, 0, 0))
    # beatmap creator
    d.text((931, 486), text=player, font=fnt_sml, fill=(0, 0, 0))
    d.text((931, 457), text='Played by', font=fnt, fill=(0, 0, 0))

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
    card.save('tmp/score_card.png')

    return send_file('tmp/score_card.png')

@user.route('/<username>/scores/best')
def best_score(username):
    u = client.fetch_user(username=username)

    if u is None:
        return jsonify({ 'code': 404, 'error': 'User not found.' })

    scores = u.fetch_best(limit=1)

    if scores is None:
        return jsonify({'code': 502, 'error': 'No scores found.'})
    else:
        scores = scores[0]

    b = scores.fetch_map()

    pp = '{:,.2f}pp'.format(scores.pp)
    score = 'Score: {:,}'.format(scores.score)
    combo = f'Combo: {scores.max_combo:,}'
    accuracy = f'Accuracy: {scores.accuracy_dec * 100:.2f}%'
    mods = f'Mods: {scores.mods}'
    title = '{} [{}]'.format(b.song_title, b.difficulty_name)
    artist = '{}'.format(b.artist)
    player = '{}'.format(u.username)

    pp_95 = '95%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=95))
    pp_97 = '97%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=97))
    pp_98 = '98%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=98))
    pp_99 = '99%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=99))
    pp_100 = '100%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=100))

    # get beatmap background
    try:
        urllib.request.urlretrieve(f'https://assets.ppy.sh/beatmaps/{str(b.mapset_id)}/covers/cover.jpg',
                                   'tmp/score_beatmap_background.png')
    except urllib.error.HTTPError:
        tmp = Image.new('RGB', (1080, 250), (255, 255, 255))
        tmp.save('tmp/score_beatmap_background.png')
    urllib.request.urlretrieve(f'https://a.ppy.sh/{str(u.id)}?{time.time()}', 'tmp/score_user_avatar.png')

    bg = Image.open('tmp/score_beatmap_background.png')
    bg = bg.resize((1080, 250))
    avatar = Image.open('tmp/score_user_avatar.png')
    avatar = avatar.resize((128, 128))
    rank = Image.open('static/ranks/{}.png'.format(scores.rank))
    rank = rank.resize((156, 156))
    card = Image.new('RGBA', (1080, 540), (255, 255, 255, 255))
    card.paste(bg, (0, 0))
    card.paste(avatar, (927, 329))
    card.paste(rank, (75, 350), rank)

    fnt = ImageFont.truetype('arial.ttf', 24)
    fnt_sml = ImageFont.truetype('arial.ttf', 12)
    fnt_big = ImageFont.truetype('arial.ttf', 40)
    d = ImageDraw.Draw(card)

    d.text((5, 255), text=title, font=fnt_big, fill=(0, 0, 0))
    d.text((5, 300), text=artist, font=fnt, fill=(0, 0, 0))
    # beatmap creator
    d.text((931, 486), text=player, font=fnt_sml, fill=(0, 0, 0))
    d.text((931, 457), text='Played by', font=fnt, fill=(0, 0, 0))

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
    card.save('tmp/score_card.png')

    return send_file('tmp/score_card.png')

@user.route('/<username>/scores/map/<id>')
def map_score(id, username):
    b = client.fetch_map(map_id=id)

    if b is None:
        return jsonify({ 'code': 502, 'error': 'Beatmap not found.' })

    scores = b.fetch_scores(username=username)

    if scores is None:
        return jsonify({ 'code': 502, 'error': 'No scores found.' })
    else:
        scores = scores[0]

    u = scores.fetch_user()

    pp = '{:,.2f}pp'.format(scores.pp)
    score = 'Score: {:,}'.format(scores.score)
    combo = f'Combo: {scores.max_combo:,}'
    accuracy = f'Accuracy: {scores.accuracy_dec*100:.2f}%'
    mods = f'Mods: {scores.mods}'
    title = '{} [{}]'.format(b.song_title, b.difficulty_name)
    artist = '{}'.format(b.artist)
    player = '{}'.format(u.username)

    pp_95 = '95%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=95))
    pp_97 = '97%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=97))
    pp_98 = '98%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=98))
    pp_99 = '99%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=99))
    pp_100 = '100%: {:,.2f}pp'.format(Oppai.calculate_pp_from_url(b.download_url, mods=scores.mods.value, accuracy=100))

    # get beatmap background
    try:
        urllib.request.urlretrieve(f'https://assets.ppy.sh/beatmaps/{str(b.mapset_id)}/covers/cover.jpg', 'tmp/score_beatmap_background.png')
    except urllib.error.HTTPError:
        tmp = Image.new('RGB', (1080, 250), (255, 255, 255))
        tmp.save('tmp/score_beatmap_background.png')
    urllib.request.urlretrieve(f'https://a.ppy.sh/{str(u.id)}?{time.time()}', 'tmp/score_user_avatar.png')

    bg = Image.open('tmp/score_beatmap_background.png')
    bg = bg.resize((1080, 250))
    avatar = Image.open('tmp/score_user_avatar.png')
    avatar = avatar.resize((128, 128))
    rank = Image.open('static/ranks/{}.png'.format(scores.rank))
    rank = rank.resize((156, 156))
    card = Image.new('RGBA', (1080, 540), (255, 255, 255, 255))
    card.paste(bg, (0, 0))
    card.paste(avatar, (927, 329))
    card.paste(rank, (75, 350), rank)

    fnt = ImageFont.truetype('arial.ttf', 24)
    fnt_sml = ImageFont.truetype('arial.ttf', 12)
    fnt_big = ImageFont.truetype('arial.ttf', 40)
    d = ImageDraw.Draw(card)

    d.text((5, 255), text=title, font=fnt_big, fill=(0, 0, 0))
    d.text((5, 300), text=artist, font=fnt, fill=(0, 0, 0))
    # beatmap creator
    d.text((931, 486), text=player, font=fnt_sml, fill=(0, 0, 0))
    d.text((931, 457), text='Played by', font=fnt, fill=(0, 0, 0))

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
    card.save('tmp/score_card.png')

    return send_file('tmp/score_card.png')

@user.route('/<username>/card')
def user_card(username):
    u = client.fetch_user(username=username)

    if u is None:
        return jsonify({ 'code': 404, 'error': 'User not found.' })

    pp = '{:,.0f}pp'.format(u.pp)
    rank = '#{:,} ({}#{:,})'.format(u.rank, u.country, u.country_rank)
    country = country_url(u.country)
    accuracy = 'Accuracy: {:.2f}%'.format(u.accuracy)
    playcount = 'Plays: {:,}'.format(u.play_count)
    level = 'Level: {:.0f}'.format(u.level)

    ranked_score = '{:,}'.format(u.ranked_score)
    total_score = '{:,}'.format(u.total_score)

    # get player avatar
    urllib.request.urlretrieve(f'https://a.ppy.sh/{str(u.id)}?{time.time()}', 'tmp/user_avatar.png')
    urllib.request.urlretrieve(country, 'tmp/user_country.png')

    # make the card
    card = Image.new('RGB', (600, 300), (255, 255, 255))
    avatar = Image.open('tmp/user_avatar.png')
    avatar = avatar.resize((300, 300))
    c = Image.open('tmp/user_country.png')
    c = c.resize((36, 26))

    fnt = ImageFont.truetype('arial.ttf', 24)
    d = ImageDraw.Draw(card)

    # draw user name, avatar and country flag
    card.paste(avatar, (0, 0))
    card.paste(c, (310, 5))
    d.text((351, 5), text=u.username, font=fnt, fill=(0, 0, 0))

    # draw stats
    d.text((310, 34), text=rank, font=fnt, fill=(0, 0, 0))
    d.text((310, 63), text=pp, font=fnt, fill=(0, 0, 0))
    d.text((310, 92), text=accuracy, font=fnt, fill=(0, 0, 0))
    d.text((310, 121), text=playcount, font=fnt, fill=(0, 0, 0))
    d.text((310, 150), text=level, font=fnt, fill=(0, 0, 0))

    d.text((310, 202), text='Ranked & Total Score:', font=fnt, fill=(0, 0, 0))
    d.text((310, 231), text=ranked_score, font=fnt, fill=(0, 0, 0))
    d.text((310, 260), text=total_score, font=fnt, fill=(0, 0, 0))

    # save the card temporarily
    card.save('tmp/user_card.png')

    return send_file('tmp/user_card.png')