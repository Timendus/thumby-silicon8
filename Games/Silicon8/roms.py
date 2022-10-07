import types
from os import listdir
from ujson import load
import files

ROM_PATH = '/Games/Silicon8/chip8'

def catalog():
    try:
        files = listdir(ROM_PATH)
    except OSError as err:
        print("ROMs directory not found! Does '"+ROM_PATH+"' exist?", err)
        return [{
            "name": "ROMs directory '"+ROM_PATH+"' not found"
        }]

    catalog = []
    for file in files:
        if file.endswith('.ch8'):
            catalog.append(loadFile(file));
    if len(catalog) == 0:
        print("No ROMs found in '"+ROM_PATH+"'")
        return [{
            "name": "No ROMs found in '"+ROM_PATH+"'"
        }]

    catalog.sort(key=lambda p: p["name"])
    return catalog

def loadFile(file):
    defaults = {
        "name": file.replace('.ch8',''),
        "desc": "No additional information found",
        "type": types.AUTO,
        "disp": types.MONOCHROME,
        "cmap": "LDWB",
        "keys": {
            "up": 5,
            "down": 8,
            "left": 7,
            "right": 9,
            "a": 4,
            "b": 6
        },
        "file": file
    }

    configFile = file.replace('.ch8', '.ch8.json')
    try:
        with open(ROM_PATH + '/' + configFile, 'r') as stream:
            config = load(stream)
            if "type" in config:
                config["type"] = types.parseType(config["type"])
            if "disp" in config:
                config["disp"] = types.parseDisp(config["disp"])
            defaults.update(config)
    except ValueError as err:
        print('JSON parse error for ' + configFile + ':', err)
    except OSError:
        pass  # Can't find config file

    return defaults

def loadinto(entry, memory):
    return files.loadinto(ROM_PATH + '/' + entry["file"], memory)
