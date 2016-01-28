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
                'CONFIG_NAME': 'input prototxt'
            },
            "convert_flags": ['input_file']
        }),
        ("input_caffemodel", {
            "template": "pre_ajax_selector",
            "template_args": {
                'CONFIG_NAME': 'input caffemodel'
            },
            "convert_flags": ['input_file']
        }),
        ("output_proto", {
            "template": "plain_text_input",
            "template_args": {
                'CONFIG_NAME': 'output prototxt',
                'PLACEHOLDER': 'will override files with the same name'
            },
            "convert_flags": ['output_proto']
        }),
        ("output_caffemodel", {
            "template": "plain_text_input",
            "template_args": {
                'CONFIG_NAME': 'output caffemodel',
                'PLACEHOLDER': 'will override files with the same name'
            },
            "convert_flags": ['output_caffemodel']
        }),
        ("layer_name", {
            "template": "plain_text_input",
            "template_args": {
                'CONFIG_NAME': 'layer name',
                'PLACEHOLDER': 'the name of an existing FC layer'
            }
        }),
        ("layer_method", {
            "template": "post_ajax_selector",
            "template_args": {
                'CONFIG_NAME': 'decompose method',
                'AVAILABLE_OPTIONS': [('rank', 'retain <number> ranks of the matrix')],
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
                'CONFIG_NAME': 'input prototxt'
            },
            "convert_flags": ['input_file']
        }),
        ("input_caffemodel", {
            "template": "pre_ajax_selector",
            "template_args": {
                'CONFIG_NAME': 'input caffemodel'
            },
            "convert_flags": ['input_file']
        }),
        ("output_caffemodel", {
            "template": "plain_text_input",
            "template_args": {
                'CONFIG_NAME': 'output caffemodel',
                'PLACEHOLDER': 'will override files with the same name'
            },
            "convert_flags": ['output_caffemodel']
        }),
        ("conditions", {
            "template": "multiple_field_list",
            "template_args": {
                'CONFIG_NAME' : 'matching condition and prunning ratio',
                'FIELD_LIST' : [
                    {
                        'type': 'checkbox',
                        'name': 'regex',
                        'text': 'regular exp?'
                    },
                    {
                        'type': 'text',
                        'name': 'pattern',
                        'text': 'sub-string or regular exp'
                    },
                    {
                        'type': 'text',
                        'name': 'rate',
                        'text': 'prunning ratio'
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
                'CONFIG_NAME': 'input prototxt'
            },
            "convert_flags": ['input_file']
        }),
        ("input_caffemodel", {
            "template": "pre_ajax_selector",
            "template_args": {
                'CONFIG_NAME': 'input caffemodel'
            },
            "convert_flags": ['input_file']
        }),
        ("output_caffemodel", {
            "template": "plain_text_input",
            "template_args": {
                'CONFIG_NAME': 'output caffemodel',
                'PLACEHOLDER': 'will override files with the same name'
            },
            "convert_flags": ['output_caffemodel']
        }),
        ("conditions", {
            "template": "multiple_field_list",
            "template_args": {
                'CONFIG_NAME' : 'matching conditions and quantization bit number',
                'FIELD_LIST' : [
                    {
                        'type': 'checkbox',
                        'name': 'regex',
                        'text': 'regular exp?'
                    },
                    {
                        'type': 'text',
                        'name': 'pattern',
                        'text': 'sub-string or regular exp'
                    },
                    {
                        'type': 'text',
                        'name': 'bits',
                        'text': 'quantization bits number'
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
                'CONFIG_NAME': 'input npz(*.npz)'
            },
            "convert_flags": ['input_file']
        }),
        ("output_file", {
            "template": "plain_text_input",
            "template_args": {
                'CONFIG_NAME': 'output bin file',
                'PLACEHOLDER': 'will override files with the same name'
            },
            "convert_flags": ['output_caffemodel']
        }),
        ("mode", {
            "template": "post_ajax_selector",
            "template_args": {
                'CONFIG_NAME': 'configuration mode',
                'AVAILABLE_OPTIONS': [('foolmode', 'simple'),
                                      ('advancemode', 'advance: specify details yourself')],
            },
            "convert_flags": ['recursive']
        })
    ]

    optional = [
        ("note_for_user", {
            "template": "plain_text",
            "template_args": {
                'CONFIG_NAME': 'format converting tool',
                'TEXT': '<a href="https://github.com/angel-eye/dan-tools" target="_blank">The github repo of the converting tool</a>'
            }
        })
    ]

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
