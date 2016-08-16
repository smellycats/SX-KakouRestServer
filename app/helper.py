# -*- coding: utf-8 -*-
u"""helper functions.

    SX-SMSServer.helper
    ~~~~~~~~~~~~~~
    
    辅助函数
    
    :copyright: (c) 2015 by Fire.
    :license: BSD, see LICENSE for more details.
"""

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature


def url_decode(query):
    u"""解析url路径返回请求参数字典."""
    d = {}
    params_list = query.split('&')
    for i in params_list:
        if i.find('=') >= 0:
            k, v = i.split('=', 1)
            d[k] = v
    return d


def q_decode(q):
    u"""分解'+'字符返回字典.

    例如: L12345+hpzl:02+kkdd:441302
    返回{
          'q': 'L12345',
          'hpzl': '02',
          'kkdd': '441302'
        }
    第一个'+'前的值用key: q表示.
    """
    d = {}
    q_list = q.split('+')
    d['q'] = q_list[0]
    for i in q_list[1:]:
        if i.find(':') >= 0:
            k, v = i.split(':', 1)
            d[k] = v
    return d


def verify_auth_token(token, key):
    u"""验证token是否正常.

    :param token: 令牌
    :param key: flask的SECRET_KEY值
    """
    s = Serializer(key)
    try:
        return s.loads(token)
    except SignatureExpired:
        # valid token, but expired
        return 'expired'
    except BadSignature:
        # invalid token
        return None


def row2dict(row):
    u"""输入sqlalchemy一行返回字典."""
    d = {}
    for col in row.__table__.columns:
        d[col.name] = getattr(row, col.name)
    return d

def ip2num(ip):
    u"""IP地址转整数."""
    return sum([256**j*int(i) for j,i in enumerate(ip.split('.')[::-1])])

def num2ip(num):
    u"""整数转IP地址."""
    return '.'.join([str(num/(256**i)%256) for i in range(3,-1,-1)])

