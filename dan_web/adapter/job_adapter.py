# -*- coding: utf-8 -*-
"""
就是定义一下每个工具需要哪些配置,
以及配置需要的template名字和参数"""

class Tool(object):
    required = {}
    optional = {}

# class svd_tool(Tool):
#     # 先只提供单层分解
#     required = {
#         "input_proto": ["ajax_selector"],
#         "output_proto": ,
#         "input_caffemodel": ,
#         "output_caffemodel": ,
#         "layers":, # 分为好几个了... fc几, rank几, 干脆每一个写一段javascript代码, 嵌进去？
#     }
#     # the path of pycaffe will be specifed by the process that actually call svd_tool
#     # and was read from a configuration file
#     optional = {"quiet_caffe"}
