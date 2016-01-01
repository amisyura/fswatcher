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

TIME_FORMAT = "%Y %h %d %H:%M:%S"

class EmptyEventsWarning(Warning):
    pass


class CmdError(Exception):
    pass


class EventHandler:
    def __init__(self):
        self.CREATE = 'C'
        self.CHANGE = 'M'
        self.DELETE = 'D'
        self.MOVE_FROM = 'MF'
        self.MOVE_TO = 'MT'

        self._objects = {
            self.CREATE:    [],
            self.CHANGE:    [],
            self.DELETE:    [],
            self.MOVE_FROM: [],
            self.MOVE_TO:   []
        }
        self._events = []
        self._codes = {
            2:   self.CHANGE,
            64:  self.MOVE_FROM,
            128: self.MOVE_TO,
            256: self.CREATE,
            512: self.DELETE
        }

    def __len__(self):
        return len(self._events)

    def __str__(self):
        result = ''
        str_codes = {
            self.CREATE:    '\033[32mC\033[0m',
            self.CHANGE:    '\033[33mM\033[0m',
            self.DELETE:    '\033[31mD\033[0m',
            self.MOVE_FROM: '\033[33mM>\033[0m',
            self.MOVE_TO:   '\033[33mM<\033[0m',
        }

        for al in self._objects:
            for i in self._objects[al]:
                result += '%s %s\n' % (str_codes.get(al, ''), i)

        return result

    def clear(self):
        for x in self._objects:
            del self._objects[x][:]

        del self._events[:]

    def callback_handler(self, event, *args, **kwargs):
        code = event.mask
        filename = event.name

        code_alias = self._codes.get(code, None)

        if code_alias:
            self._objects[code_alias].append(filename)

        self._events.append(event)


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
    def wrapper(cmd, event_handler, **kwargs):
        start_time = time.time() * 1000
        output = ''
        changed_files = ''
        command_output = ''

        try:
            if kwargs.get('show_files', False) and len(event_handler) > 0:
                changed_files += '\n\033[33mFiles:\033[0m\n'
                changed_files += str(event_handler)

            out, file_count = func(cmd, event_handler, **kwargs)

            if kwargs.get('verbose', False):
                command_output += '\n\033[33mCommand output:\033[0m\n'
                command_output += '_______________'
                command_output += out

            output += '\033[41m%s\033[0m' % time.strftime(TIME_FORMAT, time.localtime())
            output += ' Total files: \033[32m%i\033[0m' % file_count
            output += ' Time: \033[32m%i ms\033[0m' % int(time.time() * 1000 - start_time)
            output += ' Cmd run: \033[33m%s\033[0m' % cmd

            if len(changed_files) > 0:
                output += changed_files

            if len(command_output) > 0:
                output += command_output

            print output

        except EmptyEventsWarning:
            pass
        except CmdError as e:
            print e

    return wrapper


@callback_output
def callback_func(cmd, event_handler, **kwargs):
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
    arg_parser.add_argument('-f', '--files', action='store_true', help="show changed files snapshot")
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='increase verbosity')

    try:
        args = arg_parser.parse_args()
        path = args.path

        if not os.path.isdir(path):
            raise IOError('Path `%s` is not a directory' % path)

        event_handler = EventHandler()

        callback_params = {
            'event_handler': event_handler,
            'cmd': args.cmd,
            'verbose': args.verbose,
            'show_files': args.files
        }

        timer = TimerInterval(callback_func, args.delay, **callback_params)
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
