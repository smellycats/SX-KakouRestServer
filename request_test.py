# -*- coding: utf-8 -*-
import time
import datetime
import json

import arrow
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

IP = '127.0.0.1'
PORT = 5000

def send_get(url,headers = {'content-type': 'application/json'}):
    """POST请求"""
    r = requests.get(url, headers=headers,
                     auth=HTTPDigestAuth('kakou', 'pingworker'))

    return r

def auth_test(url):
    headers = {'Authorization': 'Digest kakou="pingworker"',
               'content-type': 'application/json'}
    r = requests.get(url, headers=headers)

    return r

def hbc_post():
    data = {
        'jgsj': str(datetime.datetime.now()),
        'hphm': '粤L12345',
        'kkdd_id': '441322004','hpys_id': 2,'fxbh_id': 4,'cdbh': 5,
        'imgurl': 'http://localhost/imgareaselect/imgs/1.jpg'#,'imgpath': u'c:\\123.jpg'
    }
    headers = {'content-type': 'application/json'}
    url = 'http://127.0.0.1:8098/v1/hbc'
    r = requests.post(url, headers=headers,data=json.dumps(data))

    return r

def hbc_get():
    #url = 'http://127.0.0.1:8098/hbc/2015-09-09 17:18:27/粤L54321/441322004'
    url = 'http://127.0.0.1:8098'
    headers = {'content-type': 'application/json'}
    return requests.get(url, headers=headers)

def ab_test():
    t1 = time.time()
    for i in range(50):
        r = hbc_get()
    print time.time()-t1

def token_test():
    #auth = HTTPBasicAuth('admin','gdsx27677221')
    headers = {'content-type': 'application/json'}
    url = 'http://%s:%s/token' % (IP, PORT)
    data = {'username': 'test1', 'password': 'kakoutest'}
    return requests.post(url, headers=headers, data=json.dumps(data))

def scope_get(token):
    url = 'http://localhost:8098/scope/'
    headers = {'content-type': 'application/json',
               'access_token': token}
    return requests.get(url, headers=headers)

def test_kakou_post():
    url = 'http://{0}:{1}/kakou'.format(IP, PORT)
    headers = {'content-type': 'application/json'}
    data = [
        {
            'jgsj': arrow.now().format('YYYY-MM-DD HH:mm:ss'),
            'hphm': '粤L70939',
            'kkdd_id': '441302004',
            'hpys_id': '0',
            'fxbh': 'IN',
            'cdbh':4,
            'img_path': 'http:///img/123.jpg'
        },
        {
            'jgsj': arrow.now().format('YYYY-MM-DD HH:mm:ss'),
            'hphm': '粤L12345',
            'kkdd_id': '441302004',
            'hpys_id': '0',
            'fxbh': 'IN',
            'cdbh': 4,
            'img_path': 'http:///img/123.jpg',
            'cllx': 'K41'
        }
    ]

    return requests.post(url, headers=headers, data=json.dumps(data))

def user_post():
    headers = {'content-type': 'application/json'}
    url = 'http://{0}:{1}/user'.format(IP, PORT)
    data = {'username': 'test', 'password': 'kakoutest',
            'scope': 'sms_post'}
    r = requests.post(url, headers=headers,data=json.dumps(data),
                      auth=HTTPBasicAuth('admin', 'sx2767722'))

    return r

def hcq_get():
    headers = {'content-type': 'application/json'}
    url = 'http://{0}:{1}/kakou/hcq'.format(IP, PORT)
    data = {'username': 'test', 'password': 'kakoutest',
            'scope': 'sms_post'}
    r = requests.get(url, headers=headers,
                     auth=HTTPBasicAuth('ecars', 'kakoutest'))

    return r

if __name__ == '__main__':  # pragma nocover
    token = 'eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ0Mjg2MDMwNywiaWF0IjoxNDQyODUzMTA3fQ.eyJzY29wZSI6WyJzY29wZV9nZXQiLCJoemhiY19nZXQiXSwidWlkIjoyM30.0TTL1Xp0Ft6nKRSQbqNZemlPDy7E9sL0vsVZteYYugA'
    #ab_test()
    #r = token_test()
    #r = auth_test(url)
    r = hcq_get()
    #r = test_hbc_post(token)
    print r.headers
    print r.status_code
    print r.text
