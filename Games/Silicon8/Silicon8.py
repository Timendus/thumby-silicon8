# Silicon8 for Thumby
# By Timendus
#
# An interpreter for CHIP-8, SCHIP and XO-CHIP in MicroPython for the Thumby
# playable keychain by TinyCircuits.
#
# See https://github.com/Timendus/thumby-silicon8 for more information and
# licensing information.

import machine
machine.freq(125000000)
import thumby

# Stop sound and show splash while we wait ;)
thumby.audio.stop()
thumby.display.setFPS(0)
myPath = "/".join(__file__.split("/")[0:-1])
thumby.display.drawSprite(thumby.Sprite(72, 40, myPath + "/assets/splash.bin"))
thumby.display.update()

# Fix import path so it finds our modules above all else
import sys
sys.path.insert(0, '/Games/Silicon8')

import gc
gc.threshold(2000)
gc.enable()
import thumbyinterface
gc.collect()
import roms
gc.collect()
import cpu
gc.collect()
import menu
gc.collect()

index = 0
scroll = 0

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

def runSilicon8():
    global index, scroll
    # Ask user to choose a ROM
    while True:
        gb_collect()
        program, index, scroll = menu.Menu(index, scroll).choose(roms.catalog())
        if not program["file"]:
            return False
        if menu.Confirm().choose(program):
            break
    return runProgram(program)

def runProgram(program):
    gb_collect()
    instance = cpu.CPU()  # Instantiate interpreter

    # Start the display, which may start a grayscale thread
    try:
        thumbyinterface.display.start(program["disp"])
    except NotImplementedError as err:
        # User is not on at least MicroPython v1.19.1, and grayscale library
        # can't run. This should be handled more gracefully, but for now, print.
        print(err)
        return True

    # Initialize the rest of the interpreter
    thumbyinterface.setKeys(program["keys"])
    thumbyinterface.display.setColourMap(program["cmap"])
    instance.reset(program["type"])
    thumby.display.fill(0)
    thumby.display.update()

    # Load program file directly into memory, unless it doesn't fit
    memory = memoryview(instance.ram)
    if roms.loadinto(program, memory[512:]) == -1:
        return False

    gb_collect()
    instance.run()  # This will block as long as the program is running

    return True

while runSilicon8():
    pass

thumby.reset()
