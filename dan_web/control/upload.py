# -*- coding: utf-8 -*-

import os
from werkzeug import secure_filename

def allowed_file(filetype, filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] == filetype

def get_upload_filename(user_id, filename, filetype):
    filename = secure_filename(filename)
    return os.path.join(str(user_id), 'upload_' + filetype, filename)

def allowed_filetype(filetype):
    return filetype in {'caffemodel', 'prototxt'}
