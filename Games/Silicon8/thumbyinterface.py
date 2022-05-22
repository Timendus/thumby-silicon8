import thumby
import types
import grayscale
from framebuf import FrameBuffer, MONO_VLSB, MONO_HLSB

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
        self._colourMap = 0b00011011
        self._initMonochrome()

    def setType(self, type):
        if type == types.GRAYSCALE and self._dispType == types.MONOCHROME:
            self._initGrayscale()
        if type == types.MONOCHROME and self._dispType == types.GRAYSCALE:
            self._gs.stop()
            self._initMonochrome()

    def setColourMap(self, map):
        self._colourMap = map

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
    def render(self, display):
        left:int   = (int(thumby.display.width) - int(display.width)) >> 1
        top:int    = (int(thumby.display.height) - int(display.height)) >> 1
        width:int  = min(int(display.width), int(thumby.display.width))
        height:int = min(int(display.height), int(thumby.display.height))

        if self._dispType == types.MONOCHROME:
            self._dispBuffer.blit(display.frameBuffers[0], left, top, width, height)
            thumby.display.display.show()

        if self._dispType == types.GRAYSCALE:
            buffer1, buffer2 = self._grayscaleTransform(display)
            self._dispBuffer1.blit(buffer1, left, top, width, height)
            self._dispBuffer2.blit(buffer2, left, top, width, height)
            self._gs._joinBuffers()

    @micropython.viper
    def _grayscaleTransform(self, display):
        colourMap = int(self._colourMap)

        if colourMap == 0b00011011:
            return display.frameBuffers[0], display.frameBuffers[1]

        if colourMap == 0b00100111:
            return display.frameBuffers[1], display.frameBuffers[0]

        srcBuf1:ptr8 = display.buffers[0]
        srcBuf2:ptr8 = display.buffers[1]
        size:int = int(len(srcBuf1))
        width:int = int(display.width) // 8
        destBuf1:ptr8 = bytearray(size)
        destBuf2:ptr8 = bytearray(size)

        # TODO: generate lookup from colourMap
        lookup:ptr8 = [
            # Plane 1
            [
                [ 0x00, 0xFF ], # 0x0X
                [ 0xFF, 0x00 ]  # 0x1X
            ],
            # Plane 2
            [
                [ 0xFF, 0x00 ], # 0x0X
                [ 0xFF, 0x00 ]  # 0x1X
            ]
        ]

        mask:int = 0b10000000
        while mask != 0:
            for i in range(size):
                i = int(i)

                # Determine the 'colour' of the destination
                inA:int = 1 if int(srcBuf1[i]) & mask else 0
                inB:int = 1 if int(srcBuf2[i]) & mask else 0
                outA:int = int(lookup[0][inA][inB])
                outB:int = int(lookup[1][inA][inB])

                # outA and outB are now either 0x00 or 0xFF to serve as a mask
                # for the layers

                destBuf1[i] = (int(destBuf1[i]) & (mask ^ 0xFF)) | (mask & outA)
                destBuf2[i] = (int(destBuf2[i]) & (mask ^ 0xFF)) | (mask & outB)
            mask = mask >> 1

        fbuf1 = FrameBuffer(destBuf1, int(display.width), int(display.height), MONO_HLSB)
        fbuf2 = FrameBuffer(destBuf2, int(display.width), int(display.height), MONO_HLSB)

        return fbuf1, fbuf2


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
