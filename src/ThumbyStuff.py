import thumby

def playSound(playingPattern, pattern, pitch):
    thumby.audio.play(400, 5000)

def stopSound():
    thumby.audio.stop()

@micropython.viper
def convertHLSBtoVLSB(inputBuf, width:int, height:int, outputBuf):
    inputPtr = ptr8(inputBuf)
    outputPtr = ptr8(outputBuf)
    for x in range(width):
        for y in range(height):
            if inputPtr[(y * width + x) >> 3] & (128 >> (x & 0x07)) > 0:
                outputPtr[(y >> 3) * width + x] |= 1 << (y & 0x07)
            else:
                outputPtr[(y >> 3) * width + x] &= 0xff ^ (1 << (y & 0x07))

# Render Silicon8 planeBuffer to Thumby display as best as you can
displayBuffer = bytearray((thumby.display.width * thumby.display.height) >> 3)
def render(dispWidth, dispHeight, planeBuffer):
    convertHLSBtoVLSB(planeBuffer[0], dispWidth, dispHeight, displayBuffer)
    thumby.display.blit(
        displayBuffer,
        int((thumby.display.width - dispWidth) / 2),
        int((thumby.display.height - dispHeight) / 2),
        min(dispWidth, thumby.display.width),
        min(dispHeight, thumby.display.height),
        -1, 0, 0
    )
    thumby.display.update()
    return


keymap = {}

def setKeys(keys):
    keymap = keys

# Get an array of keys that maps Thumby keys to CHIP-8 keys
def getKeys():
    keyboard = bytearray(16)
    if "up" in keymap:
        keyboard[keymap["up"]]    |= thumby.buttonU.pressed()
    if "down" in keymap:
        keyboard[keymap["down"]]  |= thumby.buttonD.pressed()
    if "left" in keymap:
        keyboard[keymap["left"]]  |= thumby.buttonL.pressed()
    if "right" in keymap:
        keyboard[keymap["right"]] |= thumby.buttonR.pressed()
    if "a" in keymap:
        keyboard[keymap["a"]]     |= thumby.buttonA.pressed()
    if "b" in keymap:
        keyboard[keymap["b"]]     |= thumby.buttonB.pressed()
    return keyboard
