#!/usr/bin/python

import os
import time
import argparse
import subprocess

from fsevents import Observer
from fsevents import Stream

produce_need = False


def produce(cmd, verbose=False):
    """
    Perform command if necessary
    :param cmd: shell command
    """
    global produce_need
    if not produce_need:
        return None

    produce_need = False

    output('%s Cmd run: %s' % (time.strftime("%Y %h %d %H:%M:%S", time.localtime()), cmd), '')

    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out, error = pipe.communicate()

    if True == verbose and None == error:
        output(out)
        output('')
    elif error:
        output(error)
        output('')


def watch_change_callback(event):
    """
    Callback for fsevent stream
    """
    global produce_need
    produce_need = True
    return event.name


def output(text, delimiter='-', delimiter_repeat=50):
    if len(delimiter) > 0:
        print delimiter * delimiter_repeat

    if len(text) > 0:
        print text


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('path')
    arg_parser.add_argument('-c', '--cmd', required=True, type=str, nargs='?', help='Console command for execute')
    arg_parser.add_argument('-d', '--delay', type=int, default=5, nargs='?', help='Synchronization delay in seconds')
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='verbose flag')

    args = arg_parser.parse_args()
    path = args.path

    if not os.path.isdir(path):
        output('Path "%s" is not a directory' % path, '')
        return

    stream = Stream(watch_change_callback, path, file_events=True)
    observer = Observer()
    observer.schedule(stream)
    observer.start()

    try:
        while True:
            time.sleep(args.delay)
            produce(args.cmd, args.verbose)
    except KeyboardInterrupt:
        observer.unschedule(stream)
        observer.stop()

if __name__ == '__main__':
    main()
