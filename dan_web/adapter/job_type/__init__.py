# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from dan_web.adapter.job_adapter import Tool

class Adapter_svd_tool(Tool):
    # 先只提供单层分解
    required = [
        ("input_proto", ("pre_ajax_selector", {
            # 所需的配置
            'CONFIG_NAME': '输入的prototxt',
        })),
        ("input_caffemodel", ("pre_ajax_selector", {
            'CONFIG_NAME': '输入的caffemodel'
        })),
        ("output_proto", ("plain_text_input", {
            'CONFIG_NAME': '输出的prototxt',
            'PLACEHOLDER': '会覆盖generated目录下的同名文件'
        })),
        ("output_caffemodel", ("plain_text_input", {
            'CONFIG_NAME': '输出的caffemodel',
            'PLACEHOLDER': '会覆盖generated目录下的同名文件'
        })),
        ("layer_name", ("plain_text_input", {
            'CONFIG_NAME': '要分解的层名',
            'PLACEHOLDER': '一个存在的全连接层的名字'
        })),
        ("layer_method", ("post_ajax_selector", {
            'CONFIG_NAME': '分解方法',
            'AVAILABLE_OPTIONS': [('rank', '保留确定秩数')],
        }))
    ]

    # the path of pycaffe will be specifed by the process that actually call svd_tool
    # and was read from a configuration file
    optional = [
        ("quiet_caffe", ('plain_checkbox', {
            'CONFIG_NAME': '是否记录caffe的输出'
        }))
    ]
