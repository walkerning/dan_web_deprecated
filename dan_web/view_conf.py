# -*- coding: utf-8 -*-
"""
一些View的配置"""
from __future__ import unicode_literals

class ViewConfer(object):
    STATUS_TO_LABEL_CONF = {
        "running": "warning",
        "success": "success",
        "starting": "success",
        "failed": "danger",
        "_other": "default"
    }

    STATUS_TO_COLOR_CONF = {
        "running": "#f0ad4e;",
        "success": "#5cb85c",
        "starting": "#5bc0de",
        "failed": "#c12e2a",
        "_other": "#ccc"
    }

    JOB_TYPE_TO_DESC_CONF = {
        "svd_tool": "SVD of FC Layer", #"全连接层分解",
        "prune_tool": "Prunning", #"剪枝",
        "quantize_tool": "Quantization", #"量化",
        "nonmodel_tool": "No-model Prunning and Quantization", #"无模型剪枝与量化",
        "_other": "Unknown Job Type", #"未知的Job类型"
    }

    def __getattr__(self, attr_name):
        attr_list = attr_name.split('_to_')
        if len(attr_list) == 2:
            conf_dict = getattr(self.__class__, '_TO_'.join(string.upper() for string in attr_list) + '_CONF', {})
            if conf_dict:
                def _func(inp):
                    return conf_dict.get(inp, conf_dict['_other'])

            else:
                def _func(inp):
                    return ''
            return _func
        else:
            return super(ViewConfer, self).__getattr__(attr_name)
