# -*- coding: utf-8 -*-
"""
就是定义一下每个工具需要哪些配置,
以及配置需要的template名字和参数"""

from __future__ import unicode_literals
from collections import OrderedDict

class Tool(object):
    __slots__ = ['required', 'optional']
    required = {}
    optional = {}

class svd_tool(Tool):
    # 先只提供单层分解
    required = OrderedDict([
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
    ])

    # the path of pycaffe will be specifed by the process that actually call svd_tool
    # and was read from a configuration file
    optional = OrderedDict([
        ("quiet_caffe", ('plain_checkbox', {
            'CONFIG_NAME': '是否记录caffe的输出'
        }))
    ])
