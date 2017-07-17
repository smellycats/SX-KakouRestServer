# -*- coding: utf-8 -*-
import json
from functools import wraps
import shutil

import arrow
import requests
from flask import g, request, make_response, jsonify, abort
from flask_restful import reqparse, abort, Resource
from passlib.hash import sha256_crypt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import func

from . import db, app, auth, cache, limiter, logger, access_logger
from models import *
import helper


def verify_addr(f):
    """IP地址白名单"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not app.config['WHITE_LIST_OPEN'] or \
           request.remote_addr in set(['127.0.0.1', 'localhost']) or \
           request.remote_addr in app.config['WHITE_LIST']:
            pass
        else:
            return jsonify({
                'status': '403.6',
                'message': u'禁止访问:客户端的 IP 地址被拒绝'}), 403
        return f(*args, **kwargs)
    return decorated_function


@auth.verify_password
def verify_pw(username, password):
    user = Users.query.filter_by(username=username).first()
    if user:
        g.uid = user.id
        g.scope = set(user.scope.split(','))
        return sha256_crypt.verify(password, user.password)
    return False


def verify_scope(scope):
    def scope(f):
        """权限范围验证装饰器"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'all' in g.scope or scope in g.scope:
                return f(*args, **kwargs)
            else:
                abort(405)
        return decorated_function
    return scope


@app.route('/')
@limiter.limit("5000/hour")
def index_get():
    result = {
        'user_url': 'http://%suser{/user_id}' % (request.url_root),
        'scope_url': 'http://%sscope' % (request.url_root),
	'maxid_url': 'http://%smaxid' % (request.url_root),
	'stat_url': 'http://%sstat?q={}' % (request.url_root),
        'cltx_url': 'http://%scltx?q={}' % (request.url_root),
        'bkcp_url': 'http://%sbkcp?q={}' % (request.url_root)
    }
    header = {'Cache-Control': 'public, max-age=60, s-maxage=60'}
    return jsonify(result), 200, header
    

@app.route('/user/<int:user_id>', methods=['GET'])
@limiter.limit('5000/hour')
@auth.login_required
def user_get(user_id):
    user = Users.query.filter_by(id=user_id, banned=0).first()
    if user is None:
        abort(404)
    result = {
        'id': user.id,
        'username': user.username,
        'scope': user.scope,
        'date_created': user.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        'date_modified': user.date_modified.strftime('%Y-%m-%d %H:%M:%S'),
        'banned': user.banned
    }
    return jsonify(result), 200

@app.route('/user', methods=['GET'])
@limiter.limit('5000/hour')
@auth.login_required
def user_list_get():
    try:
        limit = int(request.args.get('per_page', 20))
        offset = (int(request.args.get('page', 1)) - 1) * limit
        s = db.session.query(Users)
        q = request.args.get('q', None)
        if q is not None:
            s = s.filter(Users.username.like("%{0}%".format(q)))
        user = s.limit(limit).offset(offset).all()
        total = s.count()
        items = []
        for i in user:
            items.append({
                'id': i.id,
                'username': i.username,
                'scope': i.scope,
                'date_created': i.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                'date_modified': i.date_modified.strftime('%Y-%m-%d %H:%M:%S'),
                'banned': i.banned})
    except Exception as e:
        logger.exception(e)
    return jsonify({'total_count': total, 'items': items}), 200


@app.route('/user/<int:user_id>', methods=['POST', 'PUT'])
@limiter.limit('5000/hour')
@auth.login_required
def user_put(user_id):
    if not request.json:
        return jsonify({'message': 'Problems parsing JSON'}), 415
    user = Users.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    if request.json.get('scope', None) is not None:
        # 所有权限范围
        all_scope = set()
        for i in Scope.query.all():
            all_scope.add(i.name)
        # 授予的权限范围
        request_scope = set(request.json.get('scope', u'null').split(','))
        # 求交集后的权限
        u_scope = ','.join(all_scope & request_scope)
        user.scope = u_scope
    if request.json.get('password', None) is not None:
        user.password = sha256_crypt.encrypt(
            request.json['password'], rounds=app.config['ROUNDS'])
    if request.json.get('banned', None) is not None:
        user.banned = request.json['banned']
    user.date_modified = arrow.now('PRC').datetime.replace(tzinfo=None)
    db.session.commit()

    return jsonify(), 204


@app.route('/user', methods=['POST'])
@limiter.limit('5000/hour')
@auth.login_required
def user_post():
    if not request.json:
        return jsonify({'message': 'Problems parsing JSON'}), 415
    if not request.json.get('username', None):
        error = {
            'resource': 'user',
            'field': 'username',
            'code': 'missing_field'
        }
        return jsonify({'message': 'Validation Failed', 'errors': error}), 422
    if not request.json.get('password', None):
        error = {
            'resource': 'user',
            'field': 'password',
            'code': 'missing_field'
        }
        return jsonify({'message': 'Validation Failed', 'errors': error}), 422
    if not request.json.get('scope', None):
        error = {
            'resource': 'user',
            'field': 'scope',
            'code': 'missing_field'
        }
        return jsonify({'message': 'Validation Failed', 'errors': error}), 422
    
    user = Users.query.filter_by(username=request.json['username'],
                                 banned=0).first()
    if user:
        return jsonify({'message': 'username is already esist'}), 422

    password_hash = sha256_crypt.encrypt(
        request.json['password'], rounds=app.config['ROUNDS'])
    # 所有权限范围
    all_scope = set()
    for i in Scope.query.all():
        all_scope.add(i.name)
    # 授予的权限范围
    request_scope = set(request.json.get('scope', u'null').split(','))
    # 求交集后的权限
    u_scope = ','.join(all_scope & request_scope)
    t = arrow.now('PRC').datetime.replace(tzinfo=None)
    u = Users(username=request.json['username'], password=password_hash,
              date_created=t, date_modified=t, scope=u_scope, banned=0)
    db.session.add(u)
    db.session.commit()
    result = {
        'id': u.id,
        'username': u.username,
        'scope': u.scope,
        'date_created': u.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        'date_modified': u.date_modified.strftime('%Y-%m-%d %H:%M:%S'),
        'banned': u.banned
    }
    return jsonify(result), 201


@app.route('/scope', methods=['GET'])
@limiter.limit('5000/hour')
@auth.login_required
def scope_list_get():
    items = map(helper.row2dict, Scope.query.all())
    return jsonify({'total_count': len(items), 'items': items}), 200

@cache.memoize(60)
def get_kkdd_by_name(name):
    k = Kkdd.query.filter_by(kkdd_name=name).first()
    if k is None:
	return None
    return k.kkdd_id

@cache.memoize(60)
def get_kkdd_by_id(kkdd_id):
    k = Kkdd.query.filter_by(kkdd_id=kkdd_id).first()
    if k is None:
	return None
    return k.kkdd_name

@cache.memoize(2)
def get_maxid():
    q = db.session.query(func.max(Cltx.id)).first()
    return q[0]

@cache.memoize(60*10)
def get_cltx_by_id(id):
    i = Cltx.query.filter_by(id=id).first()
    if i is None:
	return None
    if i.hphm is None or i.hphm == '':
	hphm = '-'
    else:
	hphm = i.hphm
    try:
	imgurl = 'http://{0}/{1}/{2}'.format(app.config['IMG_IP'].get(i.tpwz, ''), i.qmtp, i.tjtp.replace('\\', '/'))
    except Exception as e:
	logger.exception(e)
	imgurl = ''
    item = {
	'id': i.id,
	'hphm': hphm,
	'jgsj': i.jgsj.strftime('%Y-%m-%d %H:%M:%S'),
	'hpys': i.hpys,
	'hpys_id': app.config['HPYS2CODE'].get(i.hpys, {'id': 9, 'code': 'QT'})['id'],
	'hpys_code': app.config['HPYS2CODE'].get(i.hpys, {'id': 9, 'code': 'QT'})['code'],
	'kkdd': i.wzdd,
	'kkdd_id': get_kkdd_by_name(i.wzdd),
	'fxbh': i.fxbh,
	'fxbh_code': app.config['FXBH2CODE'].get(i.fxbh, 'QT'),
	'cdbh': int(i.cdbh),
	'clsd': int(i.clsd),
	'hpzl': i.hpzl,
	'kkbh': i.kkbh,
	'clbj': i.clbj,
	'imgurl': imgurl
    }
    return item


@app.route('/maxid', methods=['GET'])
@limiter.limit('6000/minute')
#@auth.login_required
def maxid_get():
    try:
	return jsonify({'maxid': get_maxid()}), 200
    except Exception as e:
	logger.error(e)


@app.route('/cltx/<int:id>', methods=['GET'])
@limiter.limit('6000/minute')
#@auth.login_required
def cltx_get(id):
    try:
	item = get_cltx_by_id(id)
	if item is None:
	    abort(404)
    except Exception as e:
	logger.exception(e)
    return jsonify(item), 200


@app.route('/cltx', methods=['GET'])
@limiter.limit('6000/minute')
#@auth.login_required
def cltx_list_get():
    try:
	q = request.args.get('q', None)
	if q is None:
	    abort(400)
	try:
	    args = json.loads(q)
	except Exception as e:
	    logger.error(e)
	    abort(400)
	
	limit = int(args.get('per_page', 20))
	offset = (int(args.get('page', 1)) - 1) * limit
	s = db.session.query(Cltx)
	if args.get('startid', None) is not None:
	    s = s.filter(Cltx.id >= args['startid'])
	if args.get('endid', None) is not None:
	    s = s.filter(Cltx.id <= args['endid'])
	if args.get('st', None) is not None:
	    s = s.filter(Cltx.jgsj >= arrow.get(args['st']).datetime.replace(tzinfo=None))
	if args.get('et', None) is not None:
	    s = s.filter(Cltx.jgsj <= arrow.get(args['et']).datetime.replace(tzinfo=None))
	if args.get('kkdd', None) is not None:
	    kkdd_name = get_kkdd_by_id(args['kkdd'])
	    s = s.filter(Cltx.wzdd == kkdd_name)
	if args.get('hphm', None) is not None:
	    s = s.filter(Cltx.hphm == args['hphm'])
	    if args.get('st', None) is None:
		s = s.filter(Cltx.jgsj >= arrow.now('PRC').replace(days=-1).datetime.replace(tzinfo=None))
	
	total = s.count()
	items = []
	for i in s.limit(limit).offset(offset).all():
	    if i.hphm is None or i.hphm == '':
		hphm = '-'
	    else:
		hphm = i.hphm
	    try:
	        imgurl = 'http://{0}/{1}/{2}'.format(app.config['IMG_IP'].get(i.tpwz, ''), i.qmtp, i.tjtp.replace('\\', '/'))
	    except Exception as e:
		logger.exception(e)
		imgurl = ''
	    items.append({
		'id': i.id,
		'hphm': hphm,
		'jgsj': i.jgsj.strftime('%Y-%m-%d %H:%M:%S'),
		'hpys': i.hpys,
		'hpys_id': app.config['HPYS2CODE'].get(i.hpys, {'id': 9, 'code': 'QT'})['id'],
		'hpys_code': app.config['HPYS2CODE'].get(i.hpys, {'id': 9, 'code': 'QT'})['code'],
		'kkdd': i.wzdd,
	        'kkdd_id': get_kkdd_by_name(i.wzdd),
	    	'fxbh': i.fxbh,
	    	'fxbh_code': app.config['FXBH2CODE'].get(i.fxbh, 'QT'),
	    	'cdbh': int(i.cdbh),
	    	'clsd': int(i.clsd),
                'hpzl': i.hpzl,
	        'kkbh': i.kkbh,
	        'clbj': i.clbj,
	        'imgurl': imgurl
	    })
    except Exception as e:
	logger.exception(e)
    return jsonify({'total_count': total, 'items': items}), 200


@app.route('/stat', methods=['GET'])
@limiter.limit('6000/minute')
#@auth.login_required
def stat_get():
    try:
	q = request.args.get('q', None)
	if q is None:
	    abort(400)
	try:
	    args = json.loads(q)
	except Exception as e:
	    logger.error(e)
	    abort(400)
	
	s = db.session.query(Cltx)
	if args.get('st', None) is not None:
	    s = s.filter(Cltx.jgsj >= arrow.get(args['st']).datetime.replace(tzinfo=None))
	if args.get('et', None) is not None:
	    s = s.filter(Cltx.jgsj <= arrow.get(args['et']).datetime.replace(tzinfo=None))
	if args.get('kkdd', None) is not None:
	    kkdd_name = get_kkdd_by_id(args['kkdd'])
	    s = s.filter(Cltx.wzdd == kkdd_name)
	
	total = s.count()
    except Exception as e:
	logger.exception(e)
    return jsonify({'count': total}), 200


@app.route('/bkcp', methods=['GET'])
@limiter.limit('3000/minute')
#@auth.login_required
def bkcp_list_get():
    try:
	q = request.args.get('q', None)
	if q is None:
	    abort(400)
	try:
	    args = json.loads(q)
	except Exception as e:
	    logger.error(e)
	    abort(400)
	
	limit = int(args.get('per_page', 20))
	offset = (int(args.get('page', 1)) - 1) * limit
	s = db.session.query(Bkcp)
	if args.get('hphm', None) is None:
	    s = s.filter(Bkcp.clbj == 'T')
	else:
	    s = s.filter(Bkcp.hphm == args['hphm'])
	
	total = s.count()
	items = []
	for i in s.limit(limit).offset(offset).all():
	    if i.mobiles is None or i.mobiles == '':
		mobiles = []
	    else:
	        mobiles = map(lambda x: x.strip(), i.mobiles.split(','))
	    items.append({
		'hphm': i.hphm,
		'lk': i.lk,
		'mobiles': mobiles,
		'memo': i.memo
	    })
    except Exception as e:
	logger.exception(e)
    return jsonify({'total_count': total, 'items': items}), 200

