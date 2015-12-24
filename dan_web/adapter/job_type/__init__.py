# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from dan_web.adapter.job_adapter import Tool

class Adapter_svd_tool(Tool):
    __name__ = "svd_tool"
    RECURSIVE_ADAPTER_LIST = ["post_ajax_selector"]
    # 先只提供单层分解
    required = [
        ("input_proto", {
            "template":"pre_ajax_selector",
            "template_args": {
                # 所需的配置
                'CONFIG_NAME': '输入的prototxt'
            },
            "convert_flags": ['input_file']
        }),
        ("input_caffemodel", {
            "template": "pre_ajax_selector",
            "template_args": {
                'CONFIG_NAME': '输入的caffemodel'
            },
            "convert_flags": ['input_file']
        }),
        ("output_proto", {
            "template": "plain_text_input",
            "template_args": {
                'CONFIG_NAME': '输出的prototxt',
                'PLACEHOLDER': '会覆盖generated目录下的同名文件'
            },
            "convert_flags": ['output_proto']
        }),
        ("output_caffemodel", {
            "template": "plain_text_input",
            "template_args": {
                'CONFIG_NAME': '输出的caffemodel',
                'PLACEHOLDER': '会覆盖generated目录下的同名文件'
            },
            "convert_flags": ['output_caffemodel']
        }),
        ("layer_name", {
            "template": "plain_text_input",
            "template_args": {
                'CONFIG_NAME': '要分解的层名',
                'PLACEHOLDER': '一个存在的全连接层的名字'
            }
        }),
        ("layer_method", {
            "template": "post_ajax_selector",
            "template_args": {
                'CONFIG_NAME': '分解方法',
                'AVAILABLE_OPTIONS': [('rank', '保留确定秩数')],
            },
            "convert_flags": ['recursive']
        })
    ]

    # the path of pycaffe will be specifed by the process that actually call svd_tool
    # and was read from a configuration file
    optional = [
        # ("quiet_caffe", ('plain_checkbox', {
        #     'CONFIG_NAME': '是否记录caffe的输出'
        # }))
    ]

    def convert_conf(self, conf_dict, addition_converter=None):
        super_converted =  super(Adapter_svd_tool,
                                 self).convert_conf(conf_dict,
                                                    now_package=__package__,
                                                    addition_converter=addition_converter)
        import pdb
        pdb.set_trace()
        # tool-specific adapting
        layer_string = super_converted['layer_name'] + ',' + super_converted['layer_method']
        layer_arg = super_converted.get('layer_arg', '')
        if layer_arg:
            layer_string += ',' + layer_arg

        super_converted['layers'] = [layer_string]
        return super_converted
