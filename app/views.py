# -*- coding: utf-8 -*-
import json
from functools import wraps
import shutil
import cStringIO

import arrow
import requests
from flask import g, request, make_response, jsonify, abort
from flask_restful import reqparse, abort, Resource
from passlib.hash import sha256_crypt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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


def verify_token(f):
    """token验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if app.config['TOKEN_OPEN']:
            g.uid = helper.ip2num(request.remote_addr)
            g.scope = set(['all'])
        else:
            if not request.headers.get('Access-Token'):
                return jsonify({'status': '401.6',
                                'message': 'missing token header'}), 401
            token_result = verify_auth_token(request.headers['Access-Token'],
                                             app.config['SECRET_KEY'])
            if not token_result:
                return jsonify({'status': '401.7',
                                'message': 'invalid token'}), 401
            elif token_result == 'expired':
                return jsonify({'status': '401.8',
                                'message': 'token expired'}), 401
            g.uid = token_result['uid']
            g.scope = set(token_result['scope'])

        return f(*args, **kwargs)
    return decorated_function


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
#@auth.login_required
def index_get():
    result = {
        'user_url': 'http://%suser{/user_id}' % (request.url_root),
        'scope_url': 'http://%sscope' % (request.url_root),
        # 'token_url': 'http://%stoken' % (request.url_root),
	'kkdd_url': 'http://%skkdd{/kkdd_id}' % (request.url_root),
	'maxid_url': 'http://%smaxid' % (request.url_root),
	'stat_url': 'http://%sstat{/st}{/et}{/kkdd_id}' % (request.url_root),
        'kakou_url': 'http://%skakou{/start_id}{/end_id}' % (request.url_root)
    }
    header = {'Cache-Control': 'public, max-age=60, s-maxage=60'}
    return jsonify(result), 200, header
    

@app.route('/user', methods=['OPTIONS'])
@limiter.limit('5000/hour')
def user_options():
    return jsonify(), 200

@app.route('/user/<int:user_id>', methods=['GET'])
@limiter.limit('5000/hour')
@auth.login_required
def user_get(user_id):
    user = Users.query.filter_by(id=user_id, banned=0).first()
    if user:
        result = {
            'id': user.id,
            'username': user.username,
            'scope': user.scope,
            'date_created': str(user.date_created),
            'date_modified': str(user.date_modified),
            'banned': user.banned
        }
        return jsonify(result), 200
    else:
        abort(404)

@app.route('/user/<int:user_id>', methods=['POST', 'PATCH'])
@limiter.limit('5000/hour')
@auth.login_required
def user_patch(user_id):
    if not request.json:
        return jsonify({'message': 'Problems parsing JSON'}), 415
    if not request.json.get('scope', None):
        error = {
            'resource': 'user',
            'field': 'scope',
            'code': 'missing_field'
        }
        return jsonify({'message': 'Validation Failed', 'errors': error}), 422
    # 所有权限范围
    all_scope = set()
    for i in Scope.query.all():
        all_scope.add(i.name)
    # 授予的权限范围
    request_scope = set(request.json.get('scope', u'null').split(','))
    # 求交集后的权限
    u_scope = ','.join(all_scope & request_scope)

    db.session.query(Users).filter_by(id=user_id).update(
        {'scope': u_scope, 'date_modified': arrow.now().datetime})
    db.session.commit()

    user = Users.query.filter_by(id=user_id).first()

    return jsonify({
        'id': user.id,
        'username': user.username,
        'scope': user.scope,
        'date_created': str(user.date_created),
        'date_modified': str(user.date_modified),
        'banned': user.banned
    }), 201

@app.route('/user', methods=['POST'])
@limiter.limit('5000/hour')
#@auth.login_required
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
    print password_hash
    return
    # 所有权限范围
    all_scope = set()
    for i in Scope.query.all():
        all_scope.add(i.name)
    # 授予的权限范围
    request_scope = set(request.json.get('scope', u'null').split(','))
    # 求交集后的权限
    u_scope = ','.join(all_scope & request_scope)
    u = Users(username=request.json['username'], password=password_hash,
              scope=u_scope, banned=0)
    db.session.add(u)
    db.session.commit()
    result = {
        'id': u.id,
        'username': u.username,
        'scope': u.scope,
        'date_created': str(u.date_created),
        'date_modified': str(u.date_modified),
        'banned': u.banned
    }
    return jsonify(result), 201

@app.route('/scope', methods=['OPTIONS'])
@limiter.limit('5000/hour')
def scope_options():
    return jsonify(), 200

@app.route('/scope', methods=['GET'])
@limiter.limit('5000/hour')
def scope_get():
    items = map(helper.row2dict, Scope.query.all())
    return jsonify({'total_count': len(items), 'items': items}), 200

    
@app.route('/token', methods=['OPTIONS'])
@limiter.limit('5000/hour')
def token_options():
    return jsonify(), 200

@app.route('/token', methods=['POST'])
@limiter.limit('5/minute')
def token_post():
    try:
        if request.json is None:
            return jsonify({'message': 'Problems parsing JSON'}), 415
        if not request.json.get('username', None):
            error = {
                'resource': 'Token',
                'field': 'username',
                'code': 'missing_field'
            }
            return jsonify({'message': 'Validation Failed', 'errors': error}), 422
        if not request.json.get('password', None):
            error = {'resource': 'Token', 'field': 'password',
                     'code': 'missing_field'}
            return jsonify({'message': 'Validation Failed', 'errors': error}), 422
        user = Users.query.filter_by(username=request.json.get('username'),
                                     banned=0).first()
        if not user:
            return jsonify({'message': 'username or password error'}), 422
        if not sha256_crypt.verify(request.json.get('password'), user.password):
            return jsonify({'message': 'username or password error'}), 422

        s = Serializer(app.config['SECRET_KEY'],
                       expires_in=app.config['EXPIRES'])
        token = s.dumps({'uid': user.id, 'scope': user.scope.split(',')})
    except Exception as e:
        print e

    return jsonify({
        'uid': user.id,
        'access_token': token,
        'token_type': 'self',
        'scope': user.scope,
        'expires_in': app.config['EXPIRES']
    }), 201


def get_kkdd_by_name(name):
    k = Kkdd.query.filter_by(kkdd_name=name).first()
    if k is None:
	return None
    return k.kkdd_id

def get_kkdd_by_id(kkdd_id):
    k = Kkdd.query.filter_by(kkdd_id=kkdd_id).first()
    if k is None:
	return None
    return k.kkdd_name

@app.route('/kkdd', methods=['GET'])
@limiter.limit('60/minute')
@auth.login_required
def kkdd_get():
    try:
	items = []
	k = Kkdd.query.filter_by().all()
	for i in k:
	    items.append({'id': i.kkdd_id, 'name': i.kkdd_name,
			  'fxbh_list': json.loads(i.fxbh_list), 'banned': i.banned})
	return jsonify({'items': items, 'total_count': len(items)})
    except Exception as e:
	logger.error(e)


@app.route('/kkdd/<string:kkdd_id>', methods=['GET'])
@limiter.limit('60/minute')
@auth.login_required
def kkdd2_get(kkdd_id):
    try:
	items = []
	k = db.session.query(Kkdd).filter(Kkdd.kkdd_id.like('{0}%'.format(kkdd_id))).all()
	for i in k:
	    items.append({'id': i.kkdd_id, 'name': i.kkdd_name,
			  'fxbh_list': json.loads(i.fxbh_list), 'banned': i.banned})
	return jsonify({'items': items, 'total_count': len(items)})
    except Exception as e:
	logger.error(e)


@app.route('/kakou/<int:start_id>/<int:end_id>', methods=['GET'])
@limiter.limit('60/minute')
@auth.login_required
def kakou_get(start_id, end_id):
    try:
	items = []
        c = db.session.query(Cltx).filter(Cltx.id>=start_id, Cltx.id<=end_id).all()
        for i in c:
	    item = {}
	    item['id'] = i.id
	    item['hphm'] = i.hphm
	    item['jgsj'] = str(i.jgsj)
	    item['hpys'] = i.hpys
	    item['hpys_id'] = app.config['HPYS_ID'].get(i.hpys, 4)
	    item['hpys_code'] = app.config['HPYS_CODE'].get(i.hpys, 'QT')
	    item['kkdd'] = i.wzdd
	    item['kkdd_id'] = get_kkdd_by_name(i.wzdd)
	    item['fxbh'] = i.fxbh
	    item['fxbh_code'] = app.config['FXBH_CODE'].get(i.fxbh, 'QT')
	    item['cdbh'] = int(i.cdbh)
	    item['clsd'] = int(i.clsd)
            item['hpzl'] = i.hpzl
	    item['kkbh'] = i.kkbh
	    item['clbj'] = i.clbj
	    item['imgurl'] = 'http://{0}/{1}/{2}'.format(app.config['IMG_IP'].get(i.tpwz, '10.47.187.166'), i.qmtp, i.tjtp.replace('\\', '/').encode('utf8'))
	    items.append(item)

	return jsonify({'items': items, 'total_count': len(items)})	    
    except Exception as e:
	logger.error(e)


@app.route('/maxid', methods=['GET'])
@limiter.limit('60/minute')
@auth.login_required
def maxid_get():
    try:
	sql = ("select max(id) from cltx")
        q = db.get_engine(app, bind='kakou').execute(sql)
	result = {'maxid': q.fetchone()[0]}
	return jsonify(result), 200
    except Exception as e:
	logger.error(e)


@app.route('/stat', methods=['GET'])
@limiter.limit('60/minute')
@auth.login_required
def stat_get():
    try:
	try:
	    if request.args.get('q', None) is not None:
		q = json.loads(request.args.get('q', None))
	except Exception as e:
	    return jsonify({}), 400
	t = arrow.now()
	st = q.get('st', t.replace(hours=-2).format('YYYY-MM-DD HH:mm:ss'))
	et = q.get('et', t.format('YYYY-MM-DD HH:mm:ss'))
	sql = u"select count(*) from cltx where jgsj >= to_date('{0}', 'yyyy-mm-dd hh24:mi:ss') and jgsj <= to_date('{1}', 'yyyy-mm-dd hh24:mi:ss')".format(st, et)
	
	# 卡口地点
	kkdd_name = get_kkdd_by_id(q.get('kkbh', ''))
	if kkdd_name is None:
	    return jsonify({}), 400
	else:
	    sql += u" and wzdd='%s'" % kkdd_name
	# 方向
	if q.get('fxbh', None) is not None:
	    if app.config['CODE2FXBH'].get(q['fxbh'], None) is not None:
		sql += u" and fxbh='%s'" % app.config['CODE2FXBH'].get(q['fxbh'], None)
	q = db.get_engine(app, bind='kakou').execute(sql)
	result = {'count': q.fetchone()[0]}
	return jsonify(result), 200 
    except Exception as e:
	logger.error(e)


@app.route('/bkcp', methods=['GET'])
@limiter.limit('60/minute')
@auth.login_required
def bkcp_get():
    try:
	items = []
	b = Bkcp.query.filter_by(clbj='T').all()
	for i in b:
	    item = {}
	    item['hphm'] = i.hphm
	    item['lk'] = i.lk
	    if i.mobiles is None or i.mobiles == '':
		item['mobiles'] = []
	    else:
	        item['mobiles'] = map(lambda x: x.strip(), i.mobiles.split(','))
	    item['memo'] = i.memo
	    items.append(item)
	result = {'total_count': len(items), 'items': items}
	return jsonify(result), 200 
    except Exception as e:
	logger.error(e)


@app.route('/bkcp/<string:hphm>', methods=['GET'])
@limiter.limit('60/minute')
@auth.login_required
def bkcp_by_hphm_get(hphm):
    try:
	b = Bkcp.query.filter_by(hphm=hphm).first()
	if b is None:
	    return jsonify({}), 404
	else:
	    item = {}
	    item['hphm'] = b.hphm
	    item['lk'] = b.lk
	    if b.mobiles is None or b.mobiles == '':
	        item['mobiles'] = []
	    else:
	        item['mobiles'] = map(lambda x: x.strip(), b.mobiles.split(','))
	    item['memo'] = b.memo

	    return jsonify(item), 200 
    except Exception as e:
	logger.error(e)
