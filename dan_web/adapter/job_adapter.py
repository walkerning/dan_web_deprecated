# -*- coding: utf-8 -*-
"""
定义一下每个工具需要哪些配置,
以及配置需要的template名字和参数"""

from collections import OrderedDict
from error import AdapterException

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
    __name__ = ""
    __metaclass__ = ToolMeta
    required = []
    optional = []
    RECURSIVE_ADAPTER_LIST = []
    DEFAULT_CONVERTER = {
        'int': int,
    }

    def get_adapter(self, adapter_layer, now_package):
        """
        get son adapter."""
        now_package = '.'.join([now_package, self.__name__])
        adapter =  get_adapter([adapter_layer], now_package)
        if adapter is None:
            raise AdapterException("在 %s 下没有找到adapter %s" % (now_package, adapter_layer))
        else:
            return adapter

    def convert_recursive_conf(self, conf_name, conf_value, now_package):
        son_adapter = self.get_adapter((conf_name, conf_value), now_package)
        son_converted_conf = son_adapter.convert_conf(conf_dict)
        return son_converted_conf

    def convert_one_conf(self, value, flags, converter, **kwargs):
        for flag in flags:
            if flag in converter:
                value = converter[flag](value)
            elif flag in self.DEFAULT_CONVERTER:
                value = self.DEFAULT_CONVERTER[flag](value)
            elif flag == "recursive":
                # 如果有多个flag, 记得将recursive放到最后
                value = {kwargs['conf_name']: value}
                value.update(self.convert_recursive_conf(kwargs['conf_name'], conf_value, kwargs['now_package']))
            else:
                # fixme: 为了debug先raise
                raise AdapterException("不能识别的flag")
                continue
        return value

    def convert_conf(self, conf_dict, now_package=__package__,
                     addition_converter=None):
        """
        调用的时候切记使用now_package=__package__调用"""
        converted_conf = {}
        addition_converter = addition_converter or {}
        for conf_name, conf_meta in self.required.iteritems():
            if not conf_name in conf_dict:
                # 缺少required配置
                raise

            converted_conf[conf_name] = self.convert_one_conf(conf_dict[conf_name],
                                                              conf_meta.get("convert_flags", []),
                                                              addition_converter,
                                                              now_package=now_package,
                                                              conf_name=conf_name)

        for conf_name, conf_meta in self.optional.iteritems():
            conf_value = conf_dict.get(conf_name, None)
            if conf_value is None:
                continue
            else:
                converted_conf[conf_name] = self.convert_one_conf(conf_dict[conf_name],
                                                                  conf_meta.get("convert_flags", []),
                                                                  addition_converter,
                                                                  now_package=now_package,
                                                                  conf_name=conf_name)
        return converted_conf


def get_adapter(adapter_layers, now_package=__package__):
    mod_list = [item for sub_list in adapter_layers for item in sub_list]
    mod_list, adapter_name = mod_list[:-1], 'Adapter_' + mod_list[-1]
    pkg = '.'.join([now_package] + mod_list)
    try:
        adapter_mod =  __import__(pkg, fromlist=['just_for_right_most_one'])
        adapter = getattr(adapter_mod, adapter_name, None)

        if adapter and issubclass(adapter, Tool) and not Tool is adapter:
            return adapter
        else:
            return None
    except Exception:
        # no such adapter
        return None
