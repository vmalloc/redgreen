import os
import sys
import time
import itertools

def get_sleeper():
    if os.isatty(sys.stdout.fileno()):
        return PrettySleeper()
    return Sleeper()

_PROGRESS_WIDTH = 50
_WATCHING_MESSAGE = "Watching for changes... "
_PROGRESS_BAR = [
    _WATCHING_MESSAGE + "".join('>' if offset == position else ' ' for offset in range(_PROGRESS_WIDTH - len(_WATCHING_MESSAGE)))
    for position in range(_PROGRESS_WIDTH - len(_WATCHING_MESSAGE))
    ]
_WIPE_STRING = "\b" * _PROGRESS_WIDTH

class PrettySleeper(object):
    def __init__(self):
        super(PrettySleeper, self).__init__()
        self._bar_iterator = itertools.cycle(_PROGRESS_BAR)
    def sleep(self, seconds):
        sys.stdout.write(next(self._bar_iterator))
        sys.stdout.flush()
        sys.stdout.write(_WIPE_STRING)
        time.sleep(seconds)
    def wake(self):
        sys.stdout.write(" " * _PROGRESS_WIDTH)
        sys.stdout.write(_WIPE_STRING)
        sys.stdout.flush()

