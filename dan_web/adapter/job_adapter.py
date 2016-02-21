# -*- coding: utf-8 -*-
"""
定义一下每个工具需要哪些配置,
以及配置需要的template名字和参数"""

import logging
from collections import OrderedDict

from dan_web.error import AdapterException, ConfigException

class ToolMeta(type):
    def __new__(mcls, name, bases, attrs):
        parents = [b for b in bases if isinstance(b, ToolMeta)]
        if not parents:
            return super(ToolMeta, mcls).__new__(mcls, name, bases, attrs)
        required = attrs.get('required', None)
        optional = attrs.get('optional', None)
        if not isinstance(required, list) or not isinstance(optional, list):
            # Adapter类定义错误
            logging.getLogger('dan_web.adapter').error("Adapter class %s is illy defined: Should have 'optional' and 'required' attributes defined!", name)
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
        'int': int
    }

    def get_adapter(self, adapter_layer, now_package):
        """
        get son adapter."""
        # fixme: the now_package thing is buggy! 换成self.__package__这样的
        now_package = '.'.join([now_package, self.__name__])
        adapter =  get_adapter([adapter_layer], now_package)
        if adapter is None:
            raise AdapterException("在 %s 下没有找到adapter %s" % (now_package, adapter_layer))
        else:
            return adapter

    def convert_recursive_conf(self, conf_name, conf_value, conf_dict, converter, now_package):
        son_adapter = self.get_adapter((conf_name, conf_value), now_package)()
        son_converted_conf = son_adapter.convert_conf(conf_dict,
                                                      addition_converter=converter)
        return son_converted_conf

    def convert_one_conf(self, value, flags, converter, conf_dict, **kwargs):
        for flag in flags:
            if flag in converter:
                if isinstance(converter[flag], list):
                    # converter list
                    for single_converter in converter[flag]:
                        value = single_converter(value)
                else:
                    # single converter
                    value = converter[flag](value)
            elif flag in self.DEFAULT_CONVERTER:
                value = self.DEFAULT_CONVERTER[flag](value)
            elif flag == "recursive":
                # 如果有多个flag, 记得将recursive放到最后
                self.converted_conf.update(self.convert_recursive_conf(kwargs['conf_name'], value,
                                                                       conf_dict, converter, kwargs['now_package']))
            else:
                # fixme: 为了debug先raise
                raise AdapterException("不能识别的flag")
                continue
        return value

    def convert_conf(self, conf_dict, now_package=__package__,
                     addition_converter=None):
        """
        调用的时候切记使用now_package=__package__调用"""
        self.converted_conf = {}
        addition_converter = addition_converter or {}
        for conf_name, conf_meta in self.required.iteritems():
            if not conf_name in conf_dict:
                # 缺少required配置
                raise ConfigException("No required configuration: %s" % conf_name)

            self.converted_conf[conf_name] = self.convert_one_conf(conf_dict[conf_name],
                                                              conf_meta.get("convert_flags", []),
                                                              addition_converter,
                                                              conf_dict,
                                                              now_package=now_package,
                                                              conf_name=conf_name)

        for conf_name, conf_meta in self.optional.iteritems():
            conf_value = conf_dict.get(conf_name, None)
            if conf_value is None:
                continue
            else:
                self.converted_conf[conf_name] = self.convert_one_conf(conf_dict[conf_name],
                                                                  conf_meta.get("convert_flags", []),
                                                                  addition_converter,
                                                                  conf_dict,
                                                                  now_package=now_package,
                                                                  conf_name=conf_name)
        return self.converted_conf


def get_adapter(adapter_layers, now_package=__package__):
    mod_list = [item for sub_list in adapter_layers for item in sub_list]
    mod_list, adapter_name = mod_list[:-1], 'Adapter_' + mod_list[-1]
    pkg = '.'.join([now_package] + mod_list)
    try:
        adapter_mod =  __import__(pkg, fromlist=['just_for_the_rightmost_one'])
        adapter = getattr(adapter_mod, adapter_name, None)

        if adapter and issubclass(adapter, Tool) and not Tool is adapter:
            return adapter
        else:
            return None
    except Exception:
        # no such adapter
        return None
