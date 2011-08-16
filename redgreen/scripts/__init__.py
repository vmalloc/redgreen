#! /usr/bin/python
from __future__ import print_function
import subprocess
import time
import argparse
import os
import sys
from .. import DirectoryChangeIterator, FileChangeIterator

def get_parser():
    parser = argparse.ArgumentParser(usage="%(prog)s [options] args...")
    parser.add_argument("--sleep", default=1, type=int)
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    parser.add_argument("-e", "--exclude-dir", dest="exclude_dirs", action="append", default=[])
    parser.add_argument("-d", "--run-in-dir", dest="run_in_dir", default=None, help="Specifies a directory in which to run nose (defaults to the monitored directory)")
    parser.add_argument("-m", "--monitor-targets", dest="monitored_targets", default=[".",], help="Directories or files to monitor", action="append")
    parser.add_argument("-t", "--testing-utility", default="nosetests")
    parser.add_argument("--shell", help="Treat the '-t' argument as a shell command", default=False, action="store_true")
    parser.add_argument("--ignore-pyc", default=False, action="store_true")
    parser.add_argument("-E", "--ext", "--extension", dest="accepted_extensions", action="append", default=[], help="Specifies extensions to track (like .py, etc.). Can be specified multiple times. NOTE: the default is to track .py and .pyc files. If this argument is given at least once, it replaces the default completely, so .py and .pyc should be passed again if desired.")
    parser.add_argument("remainder", nargs="*", default=None)
    return parser

def main_loop(args):
    watch_targets = _build_watch_targets(args)
    while True:
        for watch_target in watch_targets:
            watch_target.run_if_changed()
            time.sleep(args.sleep)
    return 0

def _build_watch_targets(args):
    accepted_extensions = args.accepted_extensions
    if not accepted_extensions:
        accepted_extensions = [".py"]
    if not args.ignore_pyc:
        accepted_extensions.append(".pyc")
    if len(args.monitored_targets) > 1 and args.monitored_targets[0] == ".":
        # workaroud to handle the "default"
        args.monitored_targets.pop(0)
    return [WatchTarget(args, target, accepted_extensions) for target in args.monitored_targets]

class WatchTarget(object):
    def __init__(self, args, target, accepted_extensions):
        super(WatchTarget, self).__init__()
        self.args = args
        self.target = target
        self._iterator = iter(_build_watcher(args, self.target, accepted_extensions))
    def run_if_changed(self):
        change = next(self._iterator)
        if not change:
            return
        command = [self.args.testing_utility]
        command.extend(self.args.remainder)
        cwd = self.args.run_in_dir
        if cwd is None:
            cwd = self.target
        if not os.path.isdir(cwd):
            cwd = os.path.dirname(cwd)
        if not cwd:
            cwd = '.'
        p = subprocess.Popen(command, cwd=cwd, shell=self.args.shell)
        p.wait()

def _build_watcher(args, monitored_target, accepted_extensions):
    if os.path.isdir(monitored_target):
        return DirectoryChangeIterator(
            monitored_target,
            accepted_extensions=accepted_extensions,
            exclude_dirs=args.exclude_dirs)
    return FileChangeIterator(
        monitored_target,
        )


################################## Boilerplate #################################
_VERBOSE = False
def log(msg, *args, **kwargs):
    if _VERBOSE:
        if args or kwargs:
            msg = msg.format(*args, **kwargs)
        print(msg, file=sys.stderr)


def main():
    global _VERBOSE
    args = get_parser().parse_args()
    _VERBOSE = args.verbose
    try:
        sys.exit(main_loop(args))
    except KeyboardInterrupt:
        sys.exit(-1)
