# -*- coding: utf-8 -*-
from __future__ import unicode_literals # every where should add a unicode_literal, could it be moved to metaclass
from dan_web.adapter.job_adapter import Tool

class Adapter_rank(Tool):
    optional = [("remain_rank", {
        "template":"plain_text_input",
        "template_args": {
            'CONFIG_NAME': '分解后矩阵秩数',
            'PLACEHOLDER': '需小于原矩阵秩数, 大于0, 默认512'
        }
    })]
    required = []
