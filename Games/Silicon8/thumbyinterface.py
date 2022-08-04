from thumbyGraphics import display as thumbyDisp
from thumbyAudio import audio
from thumbyButton import buttonA, buttonB, buttonU, buttonD, buttonL, buttonR
from framebuf import FrameBuffer, MONO_VLSB, MONO_HLSB
import types

#### Sound

@micropython.native
def playSound(playingPattern, pattern, pitch):
    if not playingPattern:
        audio.play(400, 5000)

@micropython.native
def stopSound():
    audio.stop()


#### Display

class Display:
    def __init__(self):
        self._colourMap = 0b00011011

    def start(self, type):
        self._dispType = type;
        if type == types.GRAYSCALE:
            self._initGrayscale()
        elif type == types.MONOCHROME:
            self._initMonochrome()

    def stop(self):
        if self._dispType == types.GRAYSCALE:
            self._gs.stop()

    def setColourMap(self, map):
        self._colourMap = map
        self._colourLookup:ptr8 = [ [ [0,0],[0,0] ], [ [0,0],[0,0] ] ]
        for i in range(len(map)):
            if map[i] == "B":
                self._colourLookup[0][(i&2)>>1][i&1] = 0x00
                self._colourLookup[1][(i&2)>>1][i&1] = 0x00
            elif map[i] == "W":
                self._colourLookup[0][(i&2)>>1][i&1] = 0xFF
                self._colourLookup[1][(i&2)>>1][i&1] = 0xFF
            elif map[i] == "L":
                self._colourLookup[0][(i&2)>>1][i&1] = 0x00
                self._colourLookup[1][(i&2)>>1][i&1] = 0xFF
            elif map[i] == "D":
                self._colourLookup[0][(i&2)>>1][i&1] = 0xFF
                self._colourLookup[1][(i&2)>>1][i&1] = 0x00
            else:
                raise "Invalid colour character in cmap"

    def _initMonochrome(self):
        self._dispBuffer = FrameBuffer(
            thumbyDisp.display.buffer,
            thumbyDisp.width,
            thumbyDisp.height,
            MONO_VLSB
        )

    def _initGrayscale(self):
        import grayscale
        self._gs = grayscale.Grayscale()
        self._dispBuffer1 = FrameBuffer(
            self._gs.buffer1,
            self._gs.width,
            self._gs.height,
            MONO_VLSB
        )
        self._dispBuffer2 = FrameBuffer(
            self._gs.buffer2,
            self._gs.width,
            self._gs.height,
            MONO_VLSB
        )

    @micropython.viper
    def render(self, chipDisp):
        left:int   = (int(thumbyDisp.width) - int(chipDisp.width)) >> 1
        top:int    = (int(thumbyDisp.height) - int(chipDisp.height)) >> 1
        width:int  = min(int(chipDisp.width), int(thumbyDisp.width))
        height:int = min(int(chipDisp.height), int(thumbyDisp.height))

        if self._dispType == types.MONOCHROME:
            self._dispBuffer.blit(chipDisp.frameBuffers[0], left, top, width, height)
            thumbyDisp.display.show()

        if self._dispType == types.GRAYSCALE:
            buffer1, buffer2 = self._grayscaleTransform(chipDisp)
            self._dispBuffer1.blit(buffer2, left, top, width, height)
            self._dispBuffer2.blit(buffer1, left, top, width, height)
            self._gs.show()

    @micropython.viper
    def _grayscaleTransform(self, chipDisp):
        # These are the easy (and fast) cases
        if self._colourMap == "BDLW":
            return chipDisp.frameBuffers[0], chipDisp.frameBuffers[1]
        if self._colourMap == "BLDW":
            return chipDisp.frameBuffers[1], chipDisp.frameBuffers[0]

        # Otherwise, do a transformation
        srcBuf1:ptr8 = chipDisp.buffers[0]
        srcBuf2:ptr8 = chipDisp.buffers[1]
        size:int = int(len(srcBuf1))
        width:int = int(chipDisp.width) // 8
        lookup:ptr8 = self._colourLookup

        if not hasattr(self, 'transformBuf1'):
            self.transformBuf1 = bytearray(size)
            self.transformFB1 = FrameBuffer(self.transformBuf1, int(chipDisp.width), int(chipDisp.height), MONO_HLSB)
            self.transformBuf2 = bytearray(size)
            self.transformFB2 = FrameBuffer(self.transformBuf2, int(chipDisp.width), int(chipDisp.height), MONO_HLSB)
        destBuf1:ptr8 = self.transformBuf1
        destBuf2:ptr8 = self.transformBuf2

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

        return self.transformFB1, self.transformFB2

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
        keyboard[keymap["up"]]    |= buttonU.pressed()
    if "down" in keymap:
        keyboard[keymap["down"]]  |= buttonD.pressed()
    if "left" in keymap:
        keyboard[keymap["left"]]  |= buttonL.pressed()
    if "right" in keymap:
        keyboard[keymap["right"]] |= buttonR.pressed()
    if "a" in keymap:
        keyboard[keymap["a"]]     |= buttonA.pressed()
    if "b" in keymap:
        keyboard[keymap["b"]]     |= buttonB.pressed()
    return keyboard

# Key combination to quit the running program
@micropython.viper
def breakCombo():
    return buttonL.pressed() and buttonA.pressed() and buttonB.pressed()
