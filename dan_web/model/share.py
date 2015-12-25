# -*- coding: utf-8 -*-

import glob
import os
from dan_web.error import DanWebError

def get_shared_file_name_list(glob_pattern):
    shared_path = os.environ.get('DAN_WEB_SHARED_DATA_PATH', None)
    if shared_path is None:
        raise DanWebError('环境变量DAN_WEB_SHARED_DATA_PATH没有设置')
    else:
        return [path.rsplit('/', 1)[-1] for path in glob.glob(os.path.join(shared_path, glob_pattern))]

def convert_shared_path(path):
    path_list = path.rsplit('/', 2)
    if path_list[-2] == "shared":
        shared_path = os.environ.get('DAN_WEB_SHARED_DATA_PATH', None)
        if not shared_path:
            raise DanWebError('环境变量DAN_WEB_SHARED_DATA_PATH没有设置')
        else:
            return os.path.join(shared_path, path_list[-1])
    else:
        return path

