import thumby
import types
import grayscale
from framebuf import FrameBuffer, MONO_VLSB

#### Sound

@micropython.native
def playSound(playingPattern, pattern, pitch):
    thumby.audio.play(400, 5000)

@micropython.native
def stopSound():
    thumby.audio.stop()


#### Display

class Display:
    def __init__(self):
        self._initMonochrome()

    def setType(self, type):
        if type == types.GRAYSCALE and self._dispType == types.MONOCHROME:
            self._initGrayscale()
        if type == types.MONOCHROME and self._dispType == types.GRAYSCALE:
            self._gs.stop()
            self._initMonochrome()

    def stop(self):
        if self._dispType == types.GRAYSCALE:
            self._gs.stop()

    def _initMonochrome(self):
        self._dispBuffer = FrameBuffer(
            thumby.display.display.buffer,
            thumby.display.width,
            thumby.display.height,
            MONO_VLSB
        )
        self._dispType = types.MONOCHROME

    def _initGrayscale(self):
        self._gs = grayscale.Grayscale()
        self._dispBuffer1 = FrameBuffer(
            self._gs.gsBuffer1.buffer,
            self._gs.width,
            self._gs.height,
            MONO_VLSB
        )
        self._dispBuffer2 = FrameBuffer(
            self._gs.gsBuffer2.buffer,
            self._gs.width,
            self._gs.height,
            MONO_VLSB
        )
        self._dispType = types.GRAYSCALE

    @micropython.viper
    def render(dispWidth:int, dispHeight:int, planeBuffers):
        if self._dispType == types.MONOCHROME:
            self._dispBuffer.blit(
                planeBuffers[0],
                (int(thumby.display.width) - dispWidth) >> 1,
                (int(thumby.display.height) - dispHeight) >> 1,
                min(dispWidth, thumby.display.width),
                min(dispHeight, thumby.display.height)
            )
            thumby.display.update()

        if self._dispType == types.GRAYSCALE:
            self._dispBuffer1.blit(
                planeBuffers[0],
                (int(thumby.display.width) - dispWidth) >> 1,
                (int(thumby.display.height) - dispHeight) >> 1,
                min(dispWidth, thumby.display.width),
                min(dispHeight, thumby.display.height)
            )
            self._dispBuffer2.blit(
                planeBuffers[1],
                (int(thumby.display.width) - dispWidth) >> 1,
                (int(thumby.display.height) - dispHeight) >> 1,
                min(dispWidth, thumby.display.width),
                min(dispHeight, thumby.display.height)
            )
            self._gs._joinBuffers()

display = Display()

#### Key input

keymap = {}

def setKeys(keys):
    global keymap
    keymap = keys

# Get an array of keys that maps Thumby keys to CHIP-8 keys
@micropython.native
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

# Key combination to quit the running program
@micropython.viper
def breakCombo():
    return thumby.buttonL.pressed() and thumby.buttonA.pressed() and thumby.buttonB.pressed()
