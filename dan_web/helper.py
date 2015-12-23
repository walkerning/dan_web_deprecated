# -*- coding: utf-8 -*-
import os
from contextlib import contextmanager

from flask import jsonify

from dan_web.adapter import job_adapter

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

def get_adapter(adapter_layers):
    mod_list = [item for sub_list in adapter_layers for item in sub_list]
    mod_list, adapter_name = mod_list[:-1], 'Adapter_' + mod_list[-1]
    pkg = '.'.join(['dan_web.adapter'] + mod_list)
    try:
        adapter_mod =  __import__(pkg, fromlist=['just_for_right_most_one'])
        adapter = getattr(adapter_mod, adapter_name, None)

        if adapter and issubclass(adapter, job_adapter.Tool) and not job_adapter.Tool is adapter:
            return adapter
        else:
            return None
    except Exception:
        # no such adapter
        return None
