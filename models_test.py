# -*- coding: utf-8 -*-
import arrow

from app import db, app
from app.models import *
from app.helper import *


def test_scope_get():
    scope = Scope.query.all()
    for i in scope:
        print i.name

def test_user_get():
    user = Users.query.filter_by(username='admin', banned=0).first()
    print user.scope
    
def test_traffic_get():
    r = Traffic.query.first()
    #help(r)
    print type(r.pass_time)
    #print r.crossing_id

def test_traffic_add():
    t_list = []
    for i in range(3):
        t = Traffic(crossing_id='441302123', lane_no=1, direction_index='IN',
                    plate_no=u'粤L12345', plate_type='',
                    pass_time='2015-12-13 01:23:45', plate_color='0')
        db.session.add(t)
        t_list.append(t)
    db.session.commit()
    r = [{'pass_id': r.pass_id} for r in t_list]
    print r

def test_uci_add():
    t = UserCltxId(user_id=1, city='hcq', cltx_id=123)
    db.session.add(t)
    db.session.commit()

def test_uci_get():
    u = UserCltxId.query.filter_by(user_id=22, city='hcq').first()
    u.cltx_id = 456
    db.session.commit()

def test_cltx():
    sql = ("select max(id) from cltx")
    query = db.get_engine(app, bind='kakou').execute(sql)
    r = query.fetchone()
    print r
    query.close()

def test_cltx2():
    c = db.session.query(Cltx).filter(Cltx.id>=495610805,Cltx.id<=495610808).all()
    for i in c:
	print (i.hphm,)
    #print (c.fxbh, c.hphm, c.jgsj)

def test_kkdd():
    k = Kkdd.query.filter_by(kkdd_id='441302001', banned=0).first()
    print k.kkdd_id

def test_kkdd2():
    k = Kkdd.query.filter_by().all()
    print k

def test_kkdd3():
    k = db.session.query(Kkdd).filter(Kkdd.kkdd_id.like('441302%')).all()
    print k

def test_stat():
    sql = "select count(*) from cltx where jgsj >= to_date('2016-06-19 00:00:00', 'yyyy-mm-dd hh24:mi:ss') and jgsj <= to_date('2016-06-19 00:05:00', 'yyyy-mm-dd hh24:mi:ss') and wzdd='\xe4\xba\xa4\xe8\xad\xa6\xe6\x94\xaf\xe9\x98\x9f\xe5\x8d\xa1\xe5\x8f\xa3'"
    sql2 = "select * from cltx where jgsj >= to_date('2016-06-19 00:00:00', 'yyyy-mm-dd hh24:mi:ss') and jgsj <= to_date('2016-06-19 00:05:00', 'yyyy-mm-dd hh24:mi:ss')"
    query = db.get_engine(app, bind='kakou').execute(sql2)
    r = query.fetchone()
    print (r[3].decode('gbk'),r[0])

def test_cltx3():
    c = Cltx.query.filter_by(id=498187590).first()
    print (c.hphm,)

if __name__ == '__main__':
    #hpys_test()
    #hbc_add()
    #test_scope_get()
    #test_user_get()
    #test_hbc_get()
    #test_hbc_add()
    #test_hbcimg_get()
    #test_kkdd()
    #test_traffic_get()
    #test_traffic_add()
    #test_uci_add()
    #test_uci_get()
    #test_cltx()
    #test_kkdd()
    #test_kkdd2()
    #test_kkdd3()
    #test_stat()
    test_cltx3()


