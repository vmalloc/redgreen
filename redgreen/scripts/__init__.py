#! /usr/bin/python
from __future__ import print_function
import subprocess
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
    parser.add_argument("-m", "--monitor-target", dest="monitored_target", default=".", help="Directory or file to monitor")
    parser.add_argument("-t", "--testing-utility", default="nosetests")
    parser.add_argument("--shell", help="Treat the '-t' argument as a shell command", default=False, action="store_true")
    parser.add_argument("--ignore-pyc", default=False, action="store_true")
    parser.add_argument("remainder", nargs="*", default=None)
    return parser

def main_loop(args):
    watcher = _build_watcher(args)
    for change in watcher:
        _run_nosetests(args)
    return 0

def _build_watcher(args):
    accepted_extensions = [".py"]
    if not args.ignore_pyc:
        accepted_extensions.append(".pyc")
    if os.path.isdir(args.monitored_target):
        return DirectoryChangeIterator(
            args.monitored_target,
            sleep=args.sleep,
            accepted_extensions=accepted_extensions,
            exclude_dirs=args.exclude_dirs)
    return FileChangeIterator(
        args.monitored_target,
        sleep=args.sleep,
        )

def _run_nosetests(args):
    command = [args.testing_utility]
    command.extend(args.remainder)
    cwd = args.run_in_dir
    if cwd is None:
        cwd = args.monitored_target
        if not os.path.isdir(cwd):
            cwd = os.path.dirname(cwd)
    p = subprocess.Popen(command, cwd=cwd, shell=args.shell)
    p.wait()

################################## Boilerplate #################################
_VERBOSE = False
def log(msg, *args, **kwargs):
    if _VERBOSE:
        if args or kwargs:
            msg = msg.format(*args, **kwargs)
        print(msg, file=sys.stderr)


def main():
    args = get_parser().parse_args()
    _VERBOSE = args.verbose
    try:
        sys.exit(main_loop(args))
    except KeyboardInterrupt:
        sys.exit(-1)
