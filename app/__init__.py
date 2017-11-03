# -*- coding: utf-8 -*-
import logging

import arrow
from flask import Flask, request, jsonify
#from flask_restful import Api
from flask_httpauth import HTTPBasicAuth, HTTPDigestAuth
from flask_limiter import Limiter, HEADERS
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache

from config import Production
from my_logger import debug_logging, online_logging, access_logging


# create a flask application - this ``app`` object will be used to handle
app = Flask(__name__)
app.config.from_object(Production())
#api = Api(app)

db = SQLAlchemy(app)

auth = HTTPBasicAuth()

debug_logging(u'logs/error.log')
access_logging(u'logs/access.log')

logger = logging.getLogger('root')
access_logger = logging.getLogger('access')

limiter = Limiter(app, headers_enabled=True, global_limits=["10/minute"])
limiter.header_mapping = {
    HEADERS.LIMIT: "X-RateLimit-Limit",
    HEADERS.RESET: "X-RateLimit-Reset",
    HEADERS.REMAINING: "X-RateLimit-Remaining"
}

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

from . import views


@app.after_request
def after_request(response):
    """访问信息写入日志"""
    info = u'{0} - - [{1}] "{2} {3} HTTP/1.1" {4} {5}'.format(
        request.headers.get("X-Real-IP", request.remote_addr),
        arrow.now('PRC').format('DD/MMM/YYYY:HH:mm:ss ZZ'), request.method,
        request.path, response.status_code, response.content_length)
    access_logger.info(info)
    response.headers['Server'] = app.config['HEADER_SERVER']
    #response.headers['Content-Type'] = 'application/json; charset=utf-8'
    #response.headers['Access-Control-Allow-Origin'] = '*'
    #response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
    #response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'

    return response


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'message': 'Bad Request'}), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'message': 'Unauthorized'}), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({'message': 'Forbidden'}), 403


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({'message': 'Not Found'}), 404


@app.errorhandler(405)
def method_not_allow(error):
    return jsonify({'message': 'Method Not Allowed'}), 405


@app.errorhandler(415)
def unsupported_media_type(error):
    return jsonify({'message': 'Unsupported Media Type'}), 415


@app.errorhandler(422)
def unprocessable_entity(error):
    """请求格式正确，但是由于含有语义错误，无法响应"""
    return jsonify({'message': 'Unprocessable Entity'}), 422


@app.errorhandler(500)
def internal_server_error(error):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Server': app.config['HEADER_SERVER'],
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST',
        'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
    }

    return jsonify({'message': 'Internal Server Error'}), 500, headers
