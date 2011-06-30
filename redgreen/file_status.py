import os

def FileStatus(filename):
    stat = os.stat(filename)
    return (stat.st_mtime, stat.st_size)
