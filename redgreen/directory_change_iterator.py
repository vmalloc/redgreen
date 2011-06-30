import functools
import time
import os

from .file_status import FileStatus

def _make_suffix_predicate(suffix):
    return functools.partial(str.endswith, suffix=suffix)

class DirectoryChangeIterator(object):
    def __init__(self, root, sleep, accepted_extensions, exclude_dirs=()):
        super(DirectoryChangeIterator, self).__init__()
        self._state = {}
        self._root = root
        self._sleep = sleep
        self._exclude_dirs = set(os.path.relpath(d, self._root) for d in exclude_dirs)
        self._accepted_extensions = accepted_extensions
    def __iter__(self):
        while True:
            new_state = self._get_state()
            changed = set(filename
                          for filename in set(new_state) | set(self._state)
                          if self._state.get(filename) != new_state.get(filename))
            self._discard_pyc_of_unchanged_files(new_state, changed)
            if changed:
                yield changed
                self._state = new_state
            time.sleep(self._sleep)
    def _get_state(self):
        returned = {}
        for filename in self._walk_filenames():
            try:
                returned[filename] = FileStatus(filename)
            except (OSError, IOError):
                continue
        return returned
    def _walk_filenames(self):
        for dirname, dirnames, filenames in os.walk(self._root):
            dirname = os.path.relpath(dirname, self._root)
            if dirname in self._exclude_dirs:
                continue
            for filename in filenames:
                if not self._is_extension_accepted(filename):
                    continue
                yield os.path.abspath(os.path.join(self._root, dirname, filename))
    def _is_extension_accepted(self, filename):
        for ext in self._accepted_extensions:
            if filename.endswith(ext):
                return True
        return False
    def _discard_pyc_of_unchanged_files(self, new_state, change):
        to_discard = set()
        for filename in change:
            if filename.endswith(".pyc"):
                orig_filename = filename[:-1]
                # properly handle cases where the pyc got deleted - this is important for missing modules that still
                # have their .pyc in place
                if orig_filename not in change:
                    # the original filename hasn't changed...
                    if filename in new_state:
                        to_discard.add(filename)
        for x in to_discard:
            change.discard(x)
