# -*- coding: utf-8 -*-
import arrow

from . import db


class Users(db.Model):
    """用户"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True)
    password = db.Column(db.String(128))
    scope = db.Column(db.String(128), default='')
    date_created = db.Column(db.DateTime, default=arrow.now().datetime)
    date_modified = db.Column(db.DateTime, default=arrow.now().datetime)
    banned = db.Column(db.Integer, default=0)

    def __init__(self, username, password, scope='', banned=0,
                 date_created=None, date_modified=None):
        self.username = username
        self.password = password
        self.scope = scope
        now = arrow.now().datetime
        if not date_created:
            self.date_created = now
        if not date_modified:
            self.date_modified = now
        self.banned = banned

    def __repr__(self):
        return '<Users %r>' % self.id


class Scope(db.Model):
    """权限范围"""
    __tablename__ = 'scope'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Scope %r>' % self.id

class Kkdd(db.Model):
    """卡口地点"""
    __tablename__ = 'kkdd'
    id = db.Column(db.Integer, primary_key=True)
    kkdd_id = db.Column(db.String(256))
    kkdd_name = db.Column(db.String(256))
    fxbh_list = db.Column(db.String(256))
    ps = db.Column(db.String(256))
    banned = db.Column(db.Integer, default=0)

    def __init__(self, kkdd_id, kkdd_name, fxbh_list, ps, banned=0):
	self.kkdd_id = kkdd_id
	self.kkdd_name = kkdd_name
	self.fxbh_list = fxbh_list
	self.ps = ps
	self.banned = banned

    def __repr__(self):
        return '<Kkdd %r>' % self.id


class Cltx(db.Model):
    """用户cltx表id关联"""
    __tablename__ = 'cltx'
    __bind_key__ = 'kakou'
    id = db.Column(db.Integer, primary_key=True)
    fxbh = db.Column(db.String(16))
    hphm = db.Column(db.String(30))
    hpzl = db.Column(db.String(8))
    hpys = db.Column(db.String(16))
    jgsj = db.Column(db.DateTime)
    clsd = db.Column(db.Integer)
    cllx = db.Column(db.String(16))
    tjtp = db.Column(db.String(200))
    qmtp = db.Column(db.String(100))
    hptp = db.Column(db.String(100))
    jllx = db.Column(db.String(8))
    clbj = db.Column(db.String(8))
    hdgg = db.Column(db.String(8))
    qbgg = db.Column(db.String(8))
    cfgg = db.Column(db.String(8))
    cldd = db.Column(db.String(100))
    wzdd = db.Column(db.String(200))
    memo = db.Column(db.String(256))
    clxs = db.Column(db.Integer)
    cdbh = db.Column(db.String(20))
    tpwz = db.Column(db.String(64))
    scbz = db.Column(db.String(2))
    tztp = db.Column(db.String(250))
    kkbh = db.Column(db.String(16))

    def __init__(self, fxbh, hphm, hpzl, hpys, jgsj, clsd, cllx, tjtp,
		 qmtp, hptp, jllx, clbj, hdgg, qbgg, cfgg, cldd, wzdd,
		 memo, clxs, cdbh, tpwz, scbz, tztp, kkbh):
        self.fxbh = fxbh
        self.hphm = hphm
	self.hpzl = hpzl
	self.hpys = hpys
        self.jgsj = jgsj
	self.clsd = clsd
	self.cllx = cllx
	self.tjtp = tjtp
	self.qmtp = qmtp
	self.hptp = hptp
	self.jllx = jllx
	self.clbj = clbj
	self.hdgg = hdgg
	self.qbgg = qbgg
	self.cfgg = cfgg
	self.cldd = cldd
	self.wzdd = wzdd
	self.memo = memo
	self.clxs = clxs
	self.cdbh = cdbh
	self.tpwz = tpwz
	self.scbz = scbz
	self.tztp = tztp
	self.kkbh = kkbh

    def __repr__(self):
        return '<Cltx %r>' % self.id


class Bkcp(db.Model):
    """布控车牌"""
    __tablename__ = 'bkcp'
    __bind_key__ = 'kakou'
    id = db.Column(db.Integer, primary_key=True)
    bcdw = db.Column(db.String(60))
    bcxw = db.Column(db.String(50))
    bcsj = db.Column(db.String(32))
    hphm = db.Column(db.String(32))
    cllx = db.Column(db.String(16))
    hpys = db.Column(db.String(16))
    clbj = db.Column(db.String(8))
    lxman = db.Column(db.String(32))
    memo = db.Column(db.String(256))
    lxdh = db.Column(db.String(32))
    ckbj = db.Column(db.String(8))
    lk = db.Column(db.String(8))
    mobiles = db.Column(db.String(512))

    def __init__(self, bcdw, bcxw, bcsj, hphm, cllx, hpys,
		 clbj, lxman, memo, lxdh, ckbj, lk, mobiles):
	self.bcdw = bcdw
	self.bcxw = bcxw
	self.bcsj = bcsj
	self.hphm = hphm
	self.cllx = cllx
	self.hpys = hpys
	self.clbj = clbj
	self.lxman = lxman
	self.memo = memo
	self.lxdh = lxdh
	self.ckbj = ckbj
	self.lk = lk
	self.mobiles = mobiles

    def __repr__(self):
        return '<Bkcp %r>' % self.id
