# -*- coding: utf-8 -*-
from . import app, cache, logger
from models import *


@cache.memoize(60)
def get_kkdd_name_dict():
    d = {}
    for i in Kkdd.query.all():
    	d[i.kkdd_name] = i.kkdd_id
    return d

@cache.memoize(60)
def get_kkdd_id_dict():
    d = {}
    for i in Kkdd.query.all():
    	d[i.kkdd_id] = i.kkdd_name
    return d

def build_kkdd_id(i):
    if app.config.get('KKBH2KKDD', None) is None:
    	return get_kkdd_name_dict().get(i.wzdd, None)
    else:
	return app.config['KKBH2KKDD'].get(i.kkbh, None)

def build_hphm(i):
    if i.hphm is None or i.hphm == '':
	return '-'
    else:
	return i.hphm

def build_url(i):
    """Éú³ÉurlµØÖ·"""
    try:
        imgurl = 'http://{0}/{1}/{2}'.format(app.config['IMG_IP'].get(i.tpwz, ''), i.qmtp, i.tjtp.replace('\\', '/'))
    except Exception as e:
	logger.error(i)
	logger.exception(e)
	imgurl = ''
    return imgurl