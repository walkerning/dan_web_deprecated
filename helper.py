# -*- coding: utf-8 -*-

from flask import jsonify

def success_json(**other_info):
    info = {'status': 'success'}
    info.update(other_info)
    return jsonify(info)

def fail_json(**other_info):
    info = {'status': 'fail'}
    info.update(other_info)
    return jsonify(info)
