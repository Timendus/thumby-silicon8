#!/usr/bin/env python3

# This sends Silicon8 to your Thumby, and launches it.
# It only sends files modified since the last send to your Tumby to save time.
# Works on Mac, depends on Ampy being installed.
# See: https://github.com/scientifichackers/ampy

from os import listdir, system
from os.path import isfile, isdir, join, getmtime, splitext
from glob import glob
from textwrap import dedent
from inspect import getsource
from ampy import pyboard, files

import build

time = 'send.time'

def hasBeenUpdated(file):
    return not isfile(time) or getmtime(file) > getmtime(time)

class Thumby:
    def _thumby(self):
        if not hasattr(self, 'thumby'):
            devices = glob('/dev/tty.usbmodem*')
            port = devices and devices[0]
            if not port:
                print('Could not find your Thumby! Is it plugged in and turned on..?')
                exit()
            try:
                self.thumby = pyboard.Pyboard(port)
            except pyboard.PyboardError as err:
                print('Ampy gave an error opening the device. Is code.thumby.us interfering..?')
                exit()
        return self.thumby

    def _files(self):
        if not hasattr(self, 'files'):
            self.files = files.Files(self._thumby())
        return self.files

    def _thumbyCall(self, command, streaming=False):
        self._thumby().enter_raw_repl()
        result = self._thumby().exec(dedent(command), streaming)
        self._thumby().exit_raw_repl()
        return result.decode('utf-8')

    def exists(self, file):
        result = self._thumbyCall(
            """
                from os import stat
                try:
                    stat('{0}')
                    print(True)
                except OSError:
                    print(False)
            """.format(file)
        )
        return result.strip() == "True"

    def put(self, localfile, remotefile):
        with open(localfile, "rb") as infile:
            data = infile.read()
            self._files().put(remotefile, data)

    def send(self, path):
        global time
        for f in listdir(path):
            file = join(path, f)
            remotefile = file[1:]

            # Skip hidden files, including .DS_Store
            if f[0] == '.':
                continue

            # Send newly updated files to Thumby
            if isfile(file) and hasBeenUpdated(file):
                name, ext = splitext(file)
                if ext == '.py' and isfile(name + '.mpy') and self.exists(remotefile):
                    print('Removing file', remotefile, '(because .mpy version exists now)')
                    self._files().rm(remotefile)
                else:
                    print("Sending file", remotefile)
                    self.put(file, remotefile)

            # Create directories that don't exist yet
            if isdir(file):
                self._files().mkdir(remotefile, True)
                self.send(file)

    def execute(self, function, verbose=False):
        code = dedent(getsource(function))
        code += f'\n{function.__name__}()\n'
        if verbose: print("Running on Thumby:\n\n", code)
        self._thumbyCall(code, True)

def startProgram():
    __import__('/Games/Silicon8/Silicon8.py')

thumby = Thumby()
thumby.send('./Games/')
system('touch send.time')
thumby.execute(startProgram, verbose=True)
