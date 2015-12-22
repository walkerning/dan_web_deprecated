# -*- coding: utf-8 -*-
"""
一些View的配置"""

STATUS_TO_LABEL_CONF = {
    "running": "warning",
    "success": "success",
    "starting": "success",
    "failed": "danger",
    "_other": "default"
}


def status_to_label(status):
    return STATUS_TO_LABEL_CONF.get(status, STATUS_TO_LABEL_CONF['_other'])
