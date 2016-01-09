# -*- coding: utf-8 -*-
import os
from contextlib import contextmanager
from subprocess import check_output

from flask import jsonify, flash, redirect

def success_json(**other_info):
    info = {'status': 'success'}
    info.update(other_info)
    return jsonify(info)

def fail_json(**other_info):
    info = {'status': 'fail'}
    info.update(other_info)
    return jsonify(info)

def success_redirect(redirect_to, flash_string=None):
    if flash_string is not None:
        flash(flash_string, 'success')
    return redirect(redirect_to)

def fail_redirect(redirect_to, flash_string=None):
    if flash_string is not None:
        flash(flash_string, 'danger')
    return redirect(redirect_to)

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

def which(cmd):
    try:
        return check_output(['which', cmd])
    except CalledProcessError:
        pass


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
