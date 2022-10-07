# Silicon8 for Thumby
# By Timendus
#
# An interpreter for CHIP-8, SCHIP and XO-CHIP in MicroPython for the Thumby
# playable keychain by TinyCircuits.
#
# See https://github.com/Timendus/thumby-silicon8 for more information and
# licensing information.

_WATCHDOG_BASE=const(0x40058000)
_SCRATCH0_ADDR=const(_WATCHDOG_BASE+0x0C)

from machine import freq, mem32, reset, soft_reset
freq(250000000)

# Fix import path so it finds our modules above all else
from sys import path
myPath = "/".join(__file__.split("/")[0:-1])
path.insert(0, myPath)

import gc
gc.threshold(2000)
gc.enable()

def gb_collect():
    a1 = gc.mem_alloc()
    f1 = gc.mem_free()
    gc.collect()
    a2 = gc.mem_alloc()
    f2 = gc.mem_free()
    print("### \t\tUsed\t\tAllocated\tFree")
    print("# Before gc\t{}%\t{}\t\t{}".format(a1/(a1+f1)*100, a1, f1))
    print("# After gc\t{}%\t{}\t\t{}".format(a2/(a2+f2)*100, a2, f2))
    print("# => Freed {} bytes ({}%)".format(f2-f1, (f2-f1)/(a2+f2)))
    gc.collect()

autorun = False
try:
    file = open(myPath + "/autorun", "r")
    autorun = file.read()
    file.close()
except OSError:
    pass

if autorun:

    ### Launch CHIP-8 program!

    # Show simple loading screen
    from thumbyGraphics import display
    display.drawText('Loading...', 8, 17, 1)
    display.update()

    # Make sure we boot back into the menu next time
    from os import remove
    try:
        remove(myPath + "/autorun")
    except OSError:
        pass

    # Load dependencies, limiting memory fragmentation
    gc.collect()
    from roms import loadFile, loadinto
    gc.collect()
    import thumbyinterface
    gc.collect()
    import cpu
    gc.collect()
    from types import VIP, SCHIP, XOCHIP
    gc.collect()

    # How to get back to the menu
    def resetToMenu():
        mem32[_SCRATCH0_ADDR] = 1
        soft_reset()

    # Load the program to run
    program = loadFile(autorun)

    # Set desired execution speed
    if program["type"] == VIP:
        freq(50000000)
    if program["type"] == SCHIP:
        freq(125000000)
    if program["type"] == XOCHIP:
        freq(250000000)

    # Let's get started!
    gb_collect()
    instance = cpu.CPU()  # Instantiate interpreter

    # Clear screen
    display.fill(0)
    display.update()

    # Start the display, which may start a grayscale thread
    try:
        thumbyinterface.display.start(program["disp"])
    except NotImplementedError as err:
        # User is not on at least MicroPython v1.19.1, and grayscale library
        # can't run. This should be handled more gracefully, but for now, reset.
        print("We need at least MicroPython v1.19.1 for grayscale programs")
        resetToMenu()

    # Initialize the rest of the interpreter
    thumbyinterface.setKeys(program["keys"])
    thumbyinterface.display.setColourMap(program["cmap"])
    gb_collect()
    instance.reset(program["type"])

    # Load program file directly into memory, unless it doesn't fit
    memory = memoryview(instance.ram)
    if loadinto(program, memory[512:]) == -1:
        print("Not enough CHIP-8 RAM to load the program")
        resetToMenu()

    gb_collect()
    try:
        instance.run()  # This will block as long as the program is running
    except Exception as err:
        file = open(myPath + '/error.log', 'w')
        file.write(str(err))
        file.close()
        raise err
    resetToMenu()

else:

    ### Show the menu

    # Reset screen brightness to system default
    from thumbyGraphics import display
    brightnessSetting=2
    try:
        file = open("thumby.cfg", "r")
        conf = file.read().split(',')
        for k in range(len(conf)):
            if(conf[k] == "brightness"):
                brightnessSetting = int(conf[k+1])
        file.close()
    except OSError:
        pass
    brightnessVals=[0,28,127]
    display.brightness(brightnessVals[brightnessSetting])

    # Show splash while we wait ;)
    from thumbySprite import Sprite
    display.drawSprite(Sprite(72, 40, myPath + "/assets/splash.bin"))
    display.update()

    # Stop audio if still playing
    from thumbyAudio import audio
    audio.stop()

    # Load dependencies
    import roms
    import menu

    # How to load a program
    def resetToProgram(program):
        display.fill(0)
        display.drawText('Loading...', 8, 17, 1)
        display.update()
        try:
            file = open(myPath + "/autorun", "w")
            file.write(program["file"])
            file.close()
        except OSError:
            print("Could not write autorun file")
            reset()
        mem32[_SCRATCH0_ADDR] = 1
        soft_reset()

    freq(125000000)
    index = 0
    scroll = 0

    # Ask user to choose a ROM
    while True:
        gb_collect()
        program, index, scroll = menu.Menu(index, scroll).choose(roms.catalog())
        if not program["file"]:
            reset()
        if menu.Confirm().choose(program):
            resetToProgram(program)
