# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dan_web.adapter.job_adapter import Tool

class Adapter_rank(Tool):
    optional = [("layer_arg", {
        "template":"plain_text_input",
        "template_args": {
            'CONFIG_NAME': 'rank number to retain',
            'PLACEHOLDER': 'default 512'
        }
    })]
    required = []
