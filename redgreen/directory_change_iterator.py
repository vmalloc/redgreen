import time
import os

def _get_file_key(filename):
    stat = os.stat(filename)
    return (stat.st_mtime, stat.st_size)

class DirectoryChangeIterator(object):
    def __init__(self, root, sleep, exclude_dirs=()):
        super(DirectoryChangeIterator, self).__init__()
        self._state = {}
        self._root = root
        self._sleep = sleep
        self._exclude_dirs = set(os.path.relpath(d, self._root) for d in exclude_dirs)
    def __iter__(self):
        while True:
            new_state = self._get_state()
            changed = set(filename
                          for filename in set(new_state) | set(self._state)
                          if self._state.get(filename) != new_state.get(filename))
            if changed:
                yield changed
                self._state = new_state
            time.sleep(self._sleep)
    def _get_state(self):
        returned = {}
        for dirname, dirnames, filenames in os.walk(self._root):
            dirname = os.path.relpath(dirname, self._root)
            if dirname in self._exclude_dirs:
                continue
            for filename in filenames:
                if not filename.endswith(".py"):
                    continue
                full_filename = os.path.abspath(os.path.join(self._root, dirname, filename))
                returned[full_filename] = _get_file_key(full_filename)
        return returned
