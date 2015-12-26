# -*- coding: utf-8 -*-
"""
将新建Job的config进行securing"""

import os

from werkzeug import secure_filename

from dan_web.error import ConfigException
from dan_web.adapter.job_adapter import get_adapter, Tool

def secure_conf(job_type, conf_dict):
    job_adapter = get_adapter([('job_type', job_type)])
    if job_adapter is None:
        raise ConfigException("Wrong job type: %s" % job_type)
    job_adapter = job_adapter()
    conf = Tool.convert_conf(job_adapter, conf_dict,
                             addition_converter={
                                 'input_file': _secure_input_file,
                                 'output_proto': _secure_output_proto,
                                 'output_caffemodel': _secure_output_caffemodel
                                 # 如果还要其他需要secure的可以在这里加入
                             },
                             # very bugging now_package... really need fix
                             now_package='dan_web.adapter.job_type')

    return conf

def _secure_input_file(input_file):
    input_path_list = input_file.strip().split('/', 1)
    if input_path_list[0] not in ("shared", "upload_prototxt", "upload_caffemodel",
                                  "generated_prototxt", "generated_caffemodel") or \
                                  len (input_path_list) == 1:
        raise ConfigException(u"不合法的输入路径: %s"%input_file)
    else:
        file_name = secure_filename(input_path_list[-1])
        return os.path.join(input_path_list[0], file_name)

def _secure_output_proto(output_file):
    return os.path.join('generated_prototxt', secure_filename(output_file))

def _secure_output_caffemodel(output_file):
    return os.path.join('generated_caffemodel', secure_filename(output_file))

