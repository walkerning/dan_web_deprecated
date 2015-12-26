# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import sys, os, atexit, signal

from dan_web.job_runner.conf import END_LOG_TOKEN
from dan_web.error import RunnerException

class JobRunnerDaemon(object):
    def __init__(self, runner, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', hooks={}):
        self.runner = runner # e... fuck...
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.hooks = hooks
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
            print("fork失败")
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
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'w', 1) # line buffered
        se = file(self.stderr, 'w', 0) # not buffered
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # register atexit handler
        atexit.register(self.delpid)
        # remember to register SIGTERM handler for this daemon
        signal.signal(signal.SIGTERM, lambda signum, _: self.delpid())

        # write pidfile
        pid = str(os.getpid())
        open(self.pidfile,'w+').write("%s\n" % pid)
        
        return 0

    def hook(self, hook_name):
        hook_func =  self.hooks.get(hook_name, None)
        if isinstance(hook_func, list):
            for hook_f in hook_func:
                if hook_f and callable(hook_f):
                    hook_f(self)
        else:
            if hook_func and callable(hook_func):
                hook_func(self)
            
    def delpid(self):
        # del pid file
        os.remove(self.pidfile)
        
        # print the end log and the ending token
        ending_log = '\n\n====== END: Job %s ======\n\n' % ('success' if self.end_status else 'failed') + \
                     END_LOG_TOKEN + '\n'
        
        # all logging here will be using sys.stderr, do we need an option... maybe not
        print(ending_log, file=sys.stderr)
        self.hook("at-exit")

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
            return pid
        else:
            # in the daemonized subprocess
            self.run()

    def run(self):
        """ Run Job in the sub process"""
        self.hook("pre-run")
        try:
            self.end_status = self.runner.run()
        except Exception as e:
            print("%s: %s" % (e.__class__.__name__, e), file=sys.stderr) # not print traceback
        except BaseException as e:
            print("base exception: %s: %s" % (e.__class__.__name__, e), file=sys.stderr) # not print traceback
        self.hook("post-run")

        # flush log file
        sys.stdout.flush() # from library block buffer to os buffer
        try:
            os.fsync(sys.stdout.fileno()) # fsync to disk
        except OSError:
            pass
        sys.stderr.flush()
        try:
            # cannot fsync a non-file, just check tty is not enough
            os.fsync(sys.stderr.fileno())
        except OSError:
            pass

        sys.exit(0)
