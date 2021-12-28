import types
import os
import ujson

ROM_PATH = '/CHIP-8 roms'

def catalog():
    try:
        files = os.listdir(ROM_PATH)
    except OSError as err:
        print("ROMs directory not found! Does '/CHIP-8 roms' exist?", err)
        return [{
            "name": "ROMs directory '/CHIP-8 roms' not found"
        }]

    catalog = []
    for file in files:
        if file.endswith('.ch8'):
            defaults = {
                "name": file.replace('.ch8',''),
                "type": types.AUTO,
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
            configFile = file.replace('.ch8', '.json')
            if configFile in files:
                try:
                    with open(ROM_PATH + '/' + configFile, 'r') as stream:
                        config = ujson.load(stream)
                        if "type" in config:
                            config["type"] = types.parseType(config["type"])
                        defaults.update(config)
                except ValueError as err:
                    print('JSON parse error for ' + configFile + ':', err)
            catalog.append(defaults);
    if len(catalog) == 0:
        print("No ROMs found in '/CHIP-8 roms'")
        return [{
            "name": "No ROMs found in '/CHIP-8 roms'"
        }]
    return catalog

def load(entry):
    try:
        with open(ROM_PATH + '/' + entry["file"], 'rb') as stream:
            bytes = bytearray(stream.read(-1))
            return bytes
    except IOError as err:
        print('Could not read CH8 file ' + file + ':', err)
