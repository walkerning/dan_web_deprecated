# -*- coding: utf-8 -*-

from __future__ import print_function

import sys, os, atexit

from dan_web.job_runner.conf import END_LOG_TOKEN
from dan_web.job_runner.error import RunnerException

class JobRunnerDaemon(object):
    def __init__(self, runner, pidfile, set_end_status, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        super(JobRunnerDaemon, self).__init__(pidfile, stdin=stdin, stdout=stdout, stderr=stderr)
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.set_end_status = set_end_status #fixme: 不一定行, 可能需要自己用model写数据库
        self.pidfile = pidfile
        self.end_status = False

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                return pid
        except OSError, e:
            raise RunnerException("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            # fixme: 如果在这里失败了怎么办... 在外面开时候还需要检查
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        open(self.pidfile,'w+').write("%s\n" % pid)
        return False

    def delpid(self):
        os.remove(self.pidfile)
        ending_log = 'END: Job %s\n' % ('Job success' if self.end_status else 'Job failed') + END_LOG_TOKEN + '\n'

        print(ending_log)
        self.set_end_status(self.end_status)
        # Job失败或者被终止
        # fixme: 不太确定这样可不可以, 试一试

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        pid = self.daemonize()
        if pid and pid > 0:
            # in the parent process
            return
        else:
            # in the daemonized subprocess
            self.run()

    def run(self):
        self.end_status = self.runner.run()
        sys.exit(0)
