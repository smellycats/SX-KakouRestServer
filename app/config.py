# -*- coding: utf-8 -*-


class Config(object):
    # 密码 string
    SECRET_KEY = 'showmethemoney'
    # 服务器名称
    HEADER_SERVER = 'SX-KakouRestServer'
    # 加密次数 int
    ROUNDS = 123456
    # token生存周期，默认2小时 int
    EXPIRES = 7200
    # 数据库连接 string
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../kakou.db'
    # 数据库连接绑定 dict
    SQLALCHEMY_BINDS = {
        'kakou': 'oracle://kakou:test@test/kakou'
    }
    # 连接池大小 int
    # SQLALCHEMY_POOL_SIZE = 5
    # 用户权限范围 dict
    SCOPE_USER = {}
    # 白名单启用 bool
    WHITE_LIST_OPEN = True
    # 白名单列表 set
    WHITE_LIST = set()
    # 图片服务器IP
    IMG_IP = {
	'HZKK-DATASTOR01': '10.47.187.165:8092',
	'HZKK-DATASTOR02': '10.47.187.166:8082'
    }
    # 号牌颜色ID
    HPYS2CODE = {
	u'白牌': {'id': 0, 'code': 'WT'},
	u'黄牌': {'id': 1, 'code': 'YL'},
	u'蓝牌': {'id': 2, 'code': 'BU'},
	u'黑牌': {'id': 3, 'code': 'BK'},
	u'绿牌': {'id': 4, 'code': 'GN'},
        u'其他': {'id': 9, 'code': 'QT'}
    }
    # 方向代码
    FXBH2CODE = {
	u'进城': 'IN',
	u'出城': 'OT',
	u'由东往西': 'EW',
	u'由西往东': 'WE',
	u'由南往北': 'SN',
	u'由北往南': 'NS'
    }
    # 方向代码
    CODE2FXBH = {
	'IN': u'进城',
	'OT': u'出城',
	'EW': u'由东往西',
	'WE': u'由西往东',
	'SN': u'由南往北',
	'NS': u'由北往南'
    }


class Develop(Config):
    DEBUG = True


class Production(Config):
    DEBUG = False


class Testing(Config):
    TESTING = True
