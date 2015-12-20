import os
from contextlib import contextmanager

@contextmanager
def chdir(path):
    if path:
        cwd = os.getcwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(cwd)
    else:
        yield
