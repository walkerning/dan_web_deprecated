# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from dan_web.adapter.job_adapter import Tool
import json

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
        # tool-specific adapting
        layer_string = super_converted['layer_name'] + ',' + super_converted['layer_method']
        layer_arg = super_converted.get('layer_arg', '')
        if layer_arg:
            layer_string += ',' + layer_arg

        super_converted['layers'] = [layer_string]
        return super_converted

class Adapter_prune_tool(Tool):
    __name__ = "prune_tool"
    required = [
        ("input_proto", {
            "template":"pre_ajax_selector",
            "template_args": {
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
        ("output_caffemodel", {
            "template": "plain_text_input",
            "template_args": {
                'CONFIG_NAME': '输出的caffemodel',
                'PLACEHOLDER': '会覆盖generated目录下的同名文件'
            },
            "convert_flags": ['output_caffemodel']
        }),
        ("conditions", {
            "template": "multiple_field_list",
            "template_args": {
                'CONFIG_NAME' : '匹配条件与剪枝比例',
                'FIELD_LIST' : [
                    {
                        'type': 'checkbox',
                        'name': 'regex',
                        'text': '是否为正则表达式'
                    },
                    {
                        'type': 'text',
                        'name': 'pattern',
                        'text': '匹配子字符串或正则表达式'
                    },
                    {
                        'type': 'text',
                        'name': 'rate',
                        'text': '剪枝去掉的比例'
                    }
                ]
            }
        })
    ]

    optional = []

    def convert_conf(self, conf_dict, addition_converter=None):
        super_converted =  super(Adapter_prune_tool,
                                 self).convert_conf(conf_dict,
                                                    now_package=__package__,
                                                    addition_converter=addition_converter)
        # tool-specific adapting
        conditions = json.loads(super_converted['conditions'])
        conditions = [[True if conf['regex'] else False, conf['pattern'], float(conf['rate'])] for conf in conditions]
        super_converted['conditions'] = conditions
        return super_converted


class Adapter_quantize_tool(Tool):
    __name__ = "quantize_tool"
    required = [
        ("input_proto", {
            "template":"pre_ajax_selector",
            "template_args": {
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
        ("output_caffemodel", {
            "template": "plain_text_input",
            "template_args": {
                'CONFIG_NAME': '输出的caffemodel',
                'PLACEHOLDER': '会覆盖generated目录下的同名文件'
            },
            "convert_flags": ['output_caffemodel']
        }),
        ("conditions", {
            "template": "multiple_field_list",
            "template_args": {
                'CONFIG_NAME' : '匹配条件与量化bit数',
                'FIELD_LIST' : [
                    {
                        'type': 'checkbox',
                        'name': 'regex',
                        'text': '是否为正则表达式'
                    },
                    {
                        'type': 'text',
                        'name': 'pattern',
                        'text': '匹配子字符串或正则表达式'
                    },
                    {
                        'type': 'text',
                        'name': 'bits',
                        'text': '量化bit数'
                    }
                ]
            }
        })
    ]

    optional = []

    def convert_conf(self, conf_dict, addition_converter=None):
        super_converted =  super(Adapter_quantize_tool,
                                 self).convert_conf(conf_dict,
                                                    now_package=__package__,
                                                    addition_converter=addition_converter)
        # tool-specific adapting
        conditions = json.loads(super_converted['conditions'])
        conditions = [[True if conf['regex'] else False, conf['pattern'], int(conf['bits'])] for conf in conditions]
        super_converted['conditions'] = conditions
        return super_converted


class Adapter_nonmodel_tool(Tool):
    __name__ = "nonmodel_tool"
    required = [
        ("input_npz", {
            "template": "pre_ajax_selector",
            "template_args": {
                'CONFIG_NAME': '输入的npz文件'
            },
            "convert_flags": ['input_file']
        }),
        ("output_file", {
            "template": "plain_text_input",
            "template_args": {
                'CONFIG_NAME': '输出的bin文件',
                'PLACEHOLDER': '会覆盖generated_caffemodel目录下的同名文件'
            },
            "convert_flags": ['output_caffemodel']
        }),
        ("mode", {
            "template": "post_ajax_selector",
            "template_args": {
                'CONFIG_NAME': '配置方法',
                'AVAILABLE_OPTIONS': [('foolmode', '简易模式'),
                                      ('advancemode', '高级模式: 详细指定剪枝和量化的细节')],
            },
            "convert_flags": ['recursive']
        })
    ]

    optional = []

    def convert_conf(self, conf_dict, addition_converter=None):
        super_converted =  super(Adapter_nonmodel_tool,
                                 self).convert_conf(conf_dict,
                                                    now_package=__package__,
                                                    addition_converter=addition_converter)
        # tool-specific adapting
        if super_converted.get('mode', None) == 'advancemode':
            prune_conditions = json.loads(super_converted.pop('prune_conditions'))
            prune_conditions = [[True if conf['regex'] else False, conf['pattern'], float(conf['rate'])] for conf in prune_conditions]
            quantize_conditions = json.loads(super_converted.pop('quantize_conditions'))
            quantize_conditions = [[True if conf['regex'] else False, conf['pattern'], int(conf['bits'])] for conf in quantize_conditions]

            super_converted['mode'] = {
                'foolmode': False,
                'prune_conditions': prune_conditions,
                'quantize_conditions': quantize_conditions
            }
        else:
            super_converted['mode'] = {
                'foolmode': True,
                'compression_rate': int(super_converted.pop('compression_rate', 4))
            }
            
        return super_converted
