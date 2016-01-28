# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from dan_web.adapter.job_adapter import Tool

class Adapter_foolmode(Tool):
    optional = [('compression_rate', {
        'template': 'plain_text_input',
        'template_args': {
            'CONFIG_NAME': 'compress rate',
            'PLACEHOLDER': 'an integer in the range 4~20, default 4'
        }
    })]
    required = []

class Adapter_advancemode(Tool):
    required = [
        ('prune_conditions', {
            'template': 'multiple_field_list',
            'template_args': {
                'CONFIG_NAME': 'prunning configuration',
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
        }),
        ('quantize_conditions', {
            'template': 'multiple_field_list',
            'template_args': {
                'CONFIG_NAME' : 'quantization configuration',
                'FIELD_LIST' : [
                    {
                        'type': 'checkbox',
                        'name': 'regex',
                        'text': 'reg exp?'
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
