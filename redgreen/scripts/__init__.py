#! /usr/bin/python
from __future__ import print_function
import subprocess
import time
import argparse
import os
import sys
import logging
from .. import DirectoryChangeIterator, FileChangeIterator
from ..sleeper import get_sleeper

def get_parser():
    parser = argparse.ArgumentParser(usage="%(prog)s [options] args...")
    parser.add_argument("--sleep", default=1, type=int)
    parser.add_argument("-v", "--verbose", action="append_const", const=1, dest="verbose", default=[])
    parser.add_argument("-e", "--exclude-dir", dest="exclude_dirs", action="append", default=[])
    parser.add_argument("-d", "--run-in-dir", dest="run_in_dir", default=None, help="Specifies a directory in which to run nose (defaults to the monitored directory)")
    parser.add_argument("-m", "--monitor-targets", dest="monitored_targets", default=[".",], help="Directories or files to monitor", action="append")
    parser.add_argument("-t", "--testing-utility", default="nosetests")
    parser.add_argument("--ignore-pyc", default=False, action="store_true")
    parser.add_argument("-E", "--ext", "--extension", dest="accepted_extensions", action="append", default=[], help="Specifies extensions to track (like .py, etc.). Can be specified multiple times. NOTE: the default is to track .py and .pyc files. If this argument is given at least once, it replaces the default completely, so .py and .pyc should be passed again if desired.")
    parser.add_argument("remainder", nargs="*", default=None)
    return parser

def main_loop(args):
    watch_targets = _build_watch_targets(args)
    sleeper = get_sleeper()
    try:
        while True:
            for watch_target in watch_targets:
                logging.info("Monitoring %s", watch_target)
                if watch_target.changed():
                    sleeper.wake()
                    watch_target.run()
                sleeper.sleep(args.sleep)
    finally:
        sleeper.wake()
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
    def __repr__(self):
        return repr(self.target)
    def changed(self):
        change = next(self._iterator)
        if not change:
            logging.info("No change.")
            return False
        logging.info("Found change: %s elements", len(change))
        logging.debug("Change: %s", change)
        return True
    def run(self):
        command = [self.args.testing_utility]
        command.extend(self.args.remainder)
        cwd = self.args.run_in_dir
        if cwd is None:
            cwd = self.target
        if not os.path.isdir(cwd):
            cwd = os.path.dirname(cwd)
        if not cwd:
            cwd = '.'
        logging.info("Running %r in %s", command, cwd)
        p = subprocess.Popen(_get_shell_command_from_argv(command), cwd=cwd, shell=True)
        result = p.wait()
        logging.info("Result: %s", result)

def _get_shell_command_from_argv(argv):
    return " ".join(map(_quote_for_shell, argv))

def _quote_for_shell(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    if " " in s:
        s = '"{0}"'.format(s)
    else:
        s = s.replace("'", "\\'")
    return s

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

def main():
    args = get_parser().parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO if len(args.verbose) == 1 else logging.DEBUG, stream=sys.stderr)
    _VERBOSE = args.verbose
    try:
        sys.exit(main_loop(args))
    except KeyboardInterrupt:
        sys.exit(-1)
