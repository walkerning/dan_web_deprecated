# -*- coding: utf-8 -*-

import subprocess
from dan_web.job_runner.conf import END_LOG_TOKEN

def read_log_and_send(ws, log_file):

    now_message = open(log_file, 'r').read()
    # fixme: 这里可能会有些读不到, 最好给subprocess的tail设置多读几行,
    # 与now_message最后一个一样的句子之后的都要打印出来

    # Open subprocess in a long-time connection is fine.
    # Open the subprocess as soon as possible to avoid lose log.
    p = subprocess.Popen(['tail', '-n', '0', '-F', log_file], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    # must strip to get the last log
    now_message_list = now_message.strip('\n').split('\n')
    for message in now_message_list:
        ws.send(message)

    # logfile is changing,
    if now_message_list and now_message_list[-1].strip('\n') == END_LOG_TOKEN:
        p.terminate()
    else:
        for message in iter(p.stdout.readline, END_LOG_TOKEN):
            message = message.strip('\n')
            if message == END_LOG_TOKEN:
                break
            ws.send(message.strip('\n'))

    p.terminate()
