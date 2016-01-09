# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dan_web.adapter.job_adapter import Tool

class Adapter_rank(Tool):
    optional = [("layer_arg", {
        "template":"plain_text_input",
        "template_args": {
            'CONFIG_NAME': '分解后矩阵秩数',
            'PLACEHOLDER': '需小于原矩阵秩数, 大于0, 默认512'
        }
    })]
    required = []
