import time
from .file_status import FileStatus

class FileChangeIterator(object):
    def __init__(self, filename, sleep):
        super(FileChangeIterator, self).__init__()
        self.filename = filename
        self.sleep = sleep
    def __iter__(self):
        last_status = None
        while True:
            new_status = FileStatus(self.filename)
            if new_status != last_status:
                yield self.filename
            last_status = new_status
            time.sleep(self.sleep)
