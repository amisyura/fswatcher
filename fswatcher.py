#!/usr/bin/python

import os
import time
import argparse
import subprocess

from subprocess import Popen
from threading import Thread
from threading import Event

from fsevents import Observer
from fsevents import Stream


class EmptyEventsWarning(Warning):
    pass


class CmdError(Exception):
    pass


class EventHandler:
    def __init__(self):
        self.events = []

    def __len__(self):
        return len(self.events)

    def clear(self):
        del self.events[:]

    def callback_handler(self, event):
        self.events.append(event)


class TimerInterval(Thread):
    def __init__(self, callback, interval=5, *args, **kwargs):
        Thread.__init__(self)

        self.event = Event()
        self.callback = callback
        self.interval = interval
        self.args = args
        self.kwargs = kwargs

    def start(self):
        while not self.event.wait(self.interval):
            self.callback(*self.args, **self.kwargs)

    def stop(self):
        self.event.set()


def callback_output(func):
    def wrapper(cmd, event_handler, verbose):
        try:
            start_time = time.time() * 1000
            out, file_count = func(cmd, event_handler, verbose)
            print '\033[41m%s\033[0m Files: \033[32m%i\033[0m Cmd run: \033[33m%s\033[0m' % (time.strftime("%Y %h %d %H:%M:%S", time.localtime()), file_count, cmd)
            if verbose:
                print out
            print 'Execute time: \033[32m%i ms\033[0m' % int(time.time() * 1000 - start_time)
        except EmptyEventsWarning:
            pass
        except CmdError as e:
            print e

    return wrapper


@callback_output
def callback_func(cmd, event_handler, verbose=False):
    if not isinstance(cmd, list) or len(cmd) == 0:
        raise TypeError('Command must be entered')

    if not isinstance(event_handler, EventHandler):
        raise TypeError('Event handler is not a handler =)')

    file_count = len(event_handler)

    if file_count == 0:
        raise EmptyEventsWarning()

    event_handler.clear()

    stdout = ''

    for command in cmd:
        print command
        pipe = Popen(command, shell=True, stdout=subprocess.PIPE)
        out, error = pipe.communicate()

        stdout += '\n' + command + '\n' + out

        if error:
            raise CmdError(error)

    return stdout, file_count


def main():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('path')
    arg_parser.add_argument('-c', '--cmd', required=True, nargs='+', help='Console command for execute')
    arg_parser.add_argument('-d', '--delay', type=int, default=5, nargs='?', help='Synchronization delay in seconds')
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='verbose flag')

    try:
        args = arg_parser.parse_args()
        path = args.path

        if not os.path.isdir(path):
            raise IOError('Path `%s` is not a directory' % path)

        event_handler = EventHandler()
        timer = TimerInterval(callback_func, args.delay, event_handler=event_handler, cmd=args.cmd, verbose=args.verbose)
        stream = Stream(event_handler.callback_handler, path, file_events=True)
        observer = Observer()

        observer.schedule(stream)
        observer.start()
        timer.start()
    except IOError as e:
        print e
    except KeyboardInterrupt:
        observer.unschedule(stream)
        observer.stop()
        timer.stop()

if __name__ == '__main__':
    main()
