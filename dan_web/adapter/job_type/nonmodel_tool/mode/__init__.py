# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from dan_web.adapter.job_adapter import Tool

class Adapter_foolmode(Tool):
    optional = [('compression_rate', {
        'template': 'plain_text_input',
        'template_args': {
            'CONFIG_NAME': '期望达到的总体压缩率',
            'PLACEHOLDER': '4~20中的一个整数, 默认4'
        }
    })]
    required = []

class Adapter_advancemode(Tool):
    required = [
        ('prune_conditions', {
            'template': 'multiple_field_list',
            'template_args': {
                'CONFIG_NAME': '剪枝操作配置',
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
        }),
        ('quantize_conditions', {
            'template': 'multiple_field_list',
            'template_args': {
                'CONFIG_NAME' : '量化操作配置',
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
