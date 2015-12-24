# -*- coding: utf-8 -*-
import os
from contextlib import contextmanager

from flask import jsonify

def success_json(**other_info):
    info = {'status': 'success'}
    info.update(other_info)
    return jsonify(info)

def fail_json(**other_info):
    info = {'status': 'fail'}
    info.update(other_info)
    return jsonify(info)

@contextmanager
def chdir(path):
    if path:
        cwd = os.getcwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(cwd)
    else:
        yield
