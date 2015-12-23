# -*- coding: utf-8 -*-
"""
定义一下每个工具需要哪些配置,
以及配置需要的template名字和参数"""

from collections import OrderedDict

class ToolMeta(type):
    def __new__(mcls, name, bases, attrs):
        parents = [b for b in bases if isinstance(b, ToolMeta)]
        if not parents:
            return super(ToolMeta, mcls).__new__(mcls, name, bases, attrs)
        required = attrs.get('required', None)
        optional = attrs.get('optional', None)
        if not isinstance(required, list) or not isinstance(optional, list):
            # Adapter类定义错误
            return None
        if not name.startswith('Adapter_'):
            name = 'Adapter_' + name
        cls = super(ToolMeta, mcls).__new__(mcls, name, bases, attrs)
        cls.required = OrderedDict(cls.required)
        cls.optional = OrderedDict(cls.optional)
        return cls

class Tool(object):
    __metaclass__ = ToolMeta
    required = []
    optional = []
