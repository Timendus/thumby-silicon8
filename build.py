#!/usr/bin/env python3

import mpy_cross
from os.path import exists, splitext, getmtime

files = [
    './Games/Silicon8/files.py',
    './Games/Silicon8/grayscale-calibration.py',
    './Games/Silicon8/roms.py',
    './Games/Silicon8/types.py'
]

for file in files:
    name, ext = splitext(file)
    mpyfile = name + '.mpy'
    if exists(mpyfile) and getmtime(mpyfile) < getmtime(file):
        print("Compiling file", file[1:])
        mpy_cross.run(file)
