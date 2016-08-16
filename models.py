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


class Traffic(db.Model):
    """过车信息"""
    __bind_key__ = 'kakou'
    __tablename__ = 'traffic_vehicle_pass'
    pass_id = db.Column(db.Integer, primary_key=True)
    crossing_id = db.Column(db.Integer)
    lane_no = db.Column(db.Integer)
    direction_index = db.Column(db.Integer)
    plate_no = db.Column(db.String(20), default='-')
    plate_type = db.Column(db.String(10))
    pass_time = db.Column(db.DateTime)
    vehicle_speed = db.Column(db.Integer)
    vehicle_len = db.Column(db.Integer, default=0)
    plate_color = db.Column(db.String(10))
    vehicle_color = db.Column(db.String(10))
    vehicle_type = db.Column(db.String(10))
    vehicle_color_depth = db.Column(db.String(10))
    plate_state = db.Column(db.String(10), default='0')
    image_path = db.Column(db.String(256), default='')
    plate_image_path = db.Column(db.String(256), default='')
    tfs_id = db.Column(db.Integer, default=0)
    vehicle_state = db.Column(db.Integer, default=0)
    vehicle_info_level = db.Column(db.Integer, default=1)
    vehicle_logo = db.Column(db.Integer)
    vehicle_sublogo = db.Column(db.Integer)
    vehicle_model = db.Column(db.Integer)
    pilotsunvisor = db.Column(db.Integer, default=0)
    

    def __init__(self, crossing_id, lane_no, direction_index, plate_no,
                 plate_type, pass_time, vehicle_speed=0, vehicle_len=0,
                 plate_color='0', vehicle_color='Z', vehicle_type='X99',
                 vehicle_color_depth='',
                 plate_state='0', image_path='', plate_image_path='', tfs_id=0,
                 vehicle_state=0, vehicle_info_level=1, vehicle_logo=None,
                 vehicle_sublogo=None, vehicle_model=None, pilotsunvisor=0):
        self.crossing_id = crossing_id
        self.lane_no = lane_no
        self.direction_index = direction_index
        self.plate_no = plate_no
        self.plate_type = plate_type
        self.pass_time = pass_time
        self.vehicle_speed = vehicle_speed
        self.vehicle_len = vehicle_len
        self.plate_color = plate_color
        self.vehicle_color = vehicle_color
        self.vehicle_type = vehicle_type
        self.vehicle_color_depth = vehicle_color_depth
        self.plate_state = plate_state
        self.image_path = image_path
        self.plate_image_path = plate_image_path
        self.tfs_id = tfs_id
        self.vehicle_state = vehicle_state
        self.vehicle_info_level = vehicle_info_level
        self.vehicle_logo = vehicle_logo
        self.vehicle_sublogo = vehicle_sublogo
        self.vehicle_model = vehicle_model
        self.pilotsunvisor = pilotsunvisor

    def __repr__(self):
        return '<Traffic %r>' % self.pass_id


class TrafficDispositionVehicle(db.Model):
    """过车信息"""
    __bind_key__ = 'kakou'
    __tablename__ = 'traffic_disposition_vehicle'
    disposition_id = db.Column(db.Integer, primary_key=True)
    disposition_index = db.Column(db.String(32))
    disposition_type = db.Column(db.String(10))
    control_unit_id = db.Column(db.Integer)
    disposition_nature = db.Column(db.String(10))
    disposition_reason = db.Column(db.String(10))
    priority = db.Column(db.String(10))
    plate_no = db.Column(db.String(15))
    plate_color = db.Column(db.String(10))
    vehicle_color = db.Column(db.String(10))
    vehicle_type = db.Column(db.String(10))
    plate_type = db.Column(db.String(10))
    disposition_start_time = db.Column(db.DateTime)
    disposition_stop_time = db.Column(db.DateTime)
    contact_tel = db.Column(db.String(32))
    alarm_plan = db.Column(db.String(256))
    region_code = db.Column(db.String(15))
    identify = db.Column(db.String(10))
    disposition_remark = db.Column(db.String(256))
    user_id = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    modify_time = db.Column(db.DateTime)
    del_flag = db.Column(db.Integer)
    

    def __init__(self, disposition_id, disposition_index, disposition_type, control_unit_id,
                 disposition_nature, disposition_reason, priority, plate_no, plate_color,
		 vehicle_color, vehicle_type, plate_type, disposition_start_time,
		 disposition_stop_time, contact_tel, alarm_plan, region_code, identify,
		 disposition_remark, user_id, create_time, modify_time, del_flag=0):
        self.disposition_id = disposition_id
        self.disposition_index = disposition_index
        self.disposition_type = disposition_type
        self.control_unit_id = control_unit_id
        self.disposition_nature = disposition_nature
        self.disposition_reason = disposition_reason
        self.priority = priority
        self.plate_no = plate_no
        self.plate_color = plate_color
        self.vehicle_color = vehicle_color
	self.vehicle_type = vehicle_type
	self.plate_type = plate_type
	self.disposition_start_time = disposition_start_time
	self.disposition_stop_time = disposition_stop_time
	self.contact_tel = contact_tel
	self.alarm_plan = alarm_plan
	self.region_code = region_code
	self.identify = identify
	self.disposition_remark = disposition_remark
	self.user_id = user_id
	self.create_time = create_time
	self.modify_time = modify_time
	self.del_flag = del_flag

    def __repr__(self):
        return '<TrafficDispositionVehicle %r>' % self.disposition_id


class TrafficSpecialVehicle(db.Model):
    """白名单信息"""
    __bind_key__ = 'kakou'
    __tablename__ = 'traffic_special_vehicle'
    special_vehicle_id = db.Column(db.Integer, primary_key=True)
    special_vehicle_type = db.Column(db.String(10))
    plate_no = db.Column(db.String(15))
    plate_color = db.Column(db.String(10))
    vehicle_color = db.Column(db.String(10))
    vehicle_type = db.Column(db.String(10))
    plate_type = db.Column(db.String(10))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    control_unit_id = db.Column(db.Integer)
    operator_id = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    del_flag = db.Column(db.Integer)

    def __init__(self, special_vehicle_type, plate_no, plate_color, vehicle_color,
		 vehicle_type, plate_type, start_time, end_time, control_unit_id,
		 operator_id, create_time, update_time, del_flag):
        self.special_vehicle_type = special_vehicle_type
	self.plate_no = plate_no
	self.plate_color = plate_color
	self.vehicle_color = vehicle_color
	self.vehicle_type = vehicle_type
	self.plate_type = plate_type
	self.start_time = start_time
	self.end_time = end_time
	self.control_unit_id = control_unit_id
	self.operator_id = operator_id
	self.create_time = create_time
	self.update_time = update_time
	self.del_flag = del_flag

    def __repr__(self):
        return '<TrafficSpecialVehicle %r>' % self.special_vehicle_id


class TrafficPrivilegevehiclePass(db.Model):
    """白名单信息"""
    __bind_key__ = 'kakou'
    __tablename__ = 'traffic_privilegevehicle_pass'
    pass_id = db.Column(db.Integer, primary_key=True)
    crossing_id = db.Column(db.Integer)
    lane_no = db.Column(db.Integer)
    direction_index = db.Column(db.Integer)
    plate_no = db.Column(db.String(20))
    plate_type = db.Column(db.String(10))
    pass_time = db.Column(db.DateTime)
    vehicle_speed = db.Column(db.Integer)
    vehicle_len = db.Column(db.Integer)
    plate_color = db.Column(db.String(10))
    vehicle_color = db.Column(db.String(10))
    vehicle_type = db.Column(db.String(10))
    vehicle_color_depth = db.Column(db.String(10))
    plate_state = db.Column(db.String(10))
    image_path = db.Column(db.String(256))
    plate_image_path = db.Column(db.String(256))
    tfs_id = db.Column(db.Integer)
    vehicle_state = db.Column(db.Integer)
    res_num1 = db.Column(db.Integer)
    res_num2 = db.Column(db.Integer)
    res_str3 = db.Column(db.String(64))
    res_str4 = db.Column(db.String(64))
    vehicle_info_level = db.Column(db.Integer)
    vehicle_logo = db.Column(db.Integer)
    pilotsunvisor = db.Column(db.Integer)

    def __init__(self, crossing_id, lane_no, direction_index, plate_no, plate_type,
		 pass_time, vehicle_speed, vehicle_len, plate_color, vehicle_color,
		 vehicle_type, vehicle_color_depth, plate_state, image_path,
		 plate_image_path, tfs_id, vehicle_state, res_num1, res_num2,
		 res_str3, res_str4, vehicle_info_level, vehicle_logo, pilotsunvisor):
        self.crossing_id = crossing_id
	self.lane_no = lane_no
	self.direction_index = direction_index
	self.plate_no = plate_no
	self.plate_type = plate_type
	self.pass_time = pass_time
	self.vehicle_speed = vehicle_speed
	self.vehicle_len = vehicle_len
	self.plate_color = plate_color
	self.vehicle_color = vehicle_color
	self.vehicle_type = vehicle_type
	self.vehicle_color_depth = vehicle_color_depth
	self.plate_state = plate_state
	self.image_path = image_path
	self.plate_image_path = plate_image_path
	self.tfs_id = tfs_id
	self.vehicle_state = vehicle_state
	self.res_num1 = res_num1
	self.res_num2 = res_num2
	self.res_str3 = res_str3
	self.res_str4 = res_str4
	self.vehicle_info_level = vehicle_info_level
	self.vehicle_logo = vehicle_logo
	self.pilotsunvisor = pilotsunvisor

    def __repr__(self):
        return '<TrafficPrivilegevehiclePass %r>' % self.pass_id


class TrafficCrossingInfo(db.Model):
    """卡口地点信息"""
    __bind_key__ = 'kakou'
    __tablename__ = 'traffic_crossing_info'
    crossing_id = db.Column(db.Integer, primary_key=True)
    crossing_index = db.Column(db.String(32))
    control_unit_id = db.Column(db.Integer)
    crossing_name = db.Column(db.String(64))
    inside_index = db.Column(db.Integer)

    def __init__(self, crossing_index, control_unit_id, crossing_name, inside_index):
        self.crossing_index = crossing_index
	self.control_unit_id = control_unit_id
	self.crossing_name = crossing_name
	self.inside_index = inside_index

    def __repr__(self):
        return '<TrafficCrossingInfo %r>' % self.crossing_id

