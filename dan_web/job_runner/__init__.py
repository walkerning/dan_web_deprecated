# -*- coding: utf-8 -*-

import os
import subprocess

from dan_web.adapter.job_adapter import get_adapter
from dan import load_command_packages
from dan_web.job_runner.conf import END_LOG_TOKEN
from dan_web.job_runner.error import RunnerException


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


class JobRunner(object):
    """
    The Job Runner! Core function of this website!"""

    def __init__(self, job):
        self.job_adapter = get_adapter([('job_type', job.job_type)])
        for cmd_type, cmd_cls in load_command_packages():
            if cmd_type == job.job_type:
                self.job_cls = cmd_cls
                break
        else:
            raise RunnerException('在当前环境的dan包里没有找到工具: %s'%job.job_type)

        # convert conf
        self.conf = self.job_adapter.convert_conf(job.get_conf(),
                                                  addition_converter={'data_file':
                                                                      job.get_abs_data_file})
        self.log_file = job.abs_log_file
        self.runner = self.job_cls.load_from_config(self.conf)

    def run(self):
        """
        fork新进程开始运行, return新进程的pid"""
        pid = os.fork()
