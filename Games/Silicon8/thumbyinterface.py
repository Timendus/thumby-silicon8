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
        if type == types.GRAYSCALE or type == types.SCALED:
            self._initGrayscale()
        elif type == types.MONOCHROME:
            self._initMonochrome()
        else:
            raise "Unsupported display type"

    def stop(self):
        if self._dispType == types.GRAYSCALE:
            self._gs.stopGPU()

    def setColourMap(self, map):
        self._colourMap = map
        self._colourLookup:ptr8 = [ [ [0,0],[0,0] ], [ [0,0],[0,0] ] ]
        for i in range(len(map)):
            if map[i] == "B":
                self._colourLookup[0][(i&2)>>1][i&1] = 0x00
                self._colourLookup[1][(i&2)>>1][i&1] = 0x00
            elif map[i] == "W":
                self._colourLookup[0][(i&2)>>1][i&1] = 0x00
                self._colourLookup[1][(i&2)>>1][i&1] = 0xFF
            elif map[i] == "L":
                self._colourLookup[0][(i&2)>>1][i&1] = 0xFF
                self._colourLookup[1][(i&2)>>1][i&1] = 0x00
            elif map[i] == "D":
                self._colourLookup[0][(i&2)>>1][i&1] = 0xFF
                self._colourLookup[1][(i&2)>>1][i&1] = 0xFF
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
        self._gs = grayscale.display
        self._dispBuffer1 = FrameBuffer(
            self._gs.buffer,
            self._gs.width,
            self._gs.height,
            MONO_VLSB
        )
        self._dispBuffer2 = FrameBuffer(
            self._gs.shading,
            self._gs.width,
            self._gs.height,
            MONO_VLSB
        )
        self._gs.startGPU()

    @micropython.viper
    def render(self, chipDisp):
        chipWidth:int  = int(chipDisp.width)
        chipHeight:int = int(chipDisp.height)
        if self._dispType == types.SCALED:
            chipWidth  = chipWidth >> 1
            chipHeight = chipHeight >> 1

        left:int   = (int(thumbyDisp.width) - chipWidth) >> 1
        top:int    = (int(thumbyDisp.height) - chipHeight) >> 1
        width:int  = min(chipWidth, int(thumbyDisp.width))
        height:int = min(chipHeight, int(thumbyDisp.height))

        if self._dispType == types.MONOCHROME:
            self._dispBuffer.blit(chipDisp.frameBuffers[0], left, top, width, height)
            thumbyDisp.display.show()
            return

        if self._dispType == types.GRAYSCALE:
            buffer1, buffer2 = self._grayscaleTransform(chipDisp)
        else:
            buffer1, buffer2 = self._scaleTransform(chipDisp)
        self._dispBuffer1.blit(buffer2, left, top, width, height)
        self._dispBuffer2.blit(buffer1, left, top, width, height)
        self._gs.show()

    @micropython.viper
    def _scaleTransform(self, chipDisp):
        # Scale the image down from black and white to grayscale
        srcBuf:ptr8 = chipDisp.buffers[0]
        size:int = int(len(srcBuf)) // 4
        chipWidth:int = int(chipDisp.width) // 8
        dispWidth:int = int(chipDisp.width) // 8 // 2

        if not hasattr(self, 'transformBuf1'):
            self.transformBuf1 = bytearray(size)
            self.transformFB1 = FrameBuffer(self.transformBuf1, int(chipDisp.width) // 2, int(chipDisp.height) // 2, MONO_HLSB)
            self.transformBuf2 = bytearray(size)
            self.transformFB2 = FrameBuffer(self.transformBuf2, int(chipDisp.width) // 2, int(chipDisp.height) // 2, MONO_HLSB)
        destBuf1:ptr8 = self.transformBuf1
        destBuf2:ptr8 = self.transformBuf2

        srcMask:int = 0b10000000
        destMask:int = 0b10000000
        pixels:int
        j:int
        nextByte:int = 0
        while destMask != 0:
            for i in range(size):
                pixels = 0
                i = int(i)
                # Calculate the offset into the source buffer
                # row: (i // dispWidth[8]) * 2 * chipWidth[16]
                # col: (i % dispWidth[8]) * 2
                # plus nextByte to see if we rolled over to the next byte
                # Optimized into shifts and a mask
                j = ((i >> 3) << 5) + ((i & 7) << 1) + nextByte

                # Find the four pixels that make up this spot, count how many
                # are actually lit
                if int(srcBuf[j]) & srcMask: pixels += 1
                if int(srcBuf[j]) & (srcMask >> 1): pixels += 1
                if int(srcBuf[j + chipWidth]) & srcMask: pixels += 1
                if int(srcBuf[j + chipWidth]) & (srcMask >> 1): pixels += 1

                # pixels is now the number of pixels in the square of four that
                # are lit up. Translate number to a colour.
                # 0    -> Black      -> 00
                # 1    -> Dark gray  -> 10
                # 2    -> Light gray -> 11
                # 3, 4 -> White      -> 01
                destBuf1[i] = (int(destBuf1[i]) & (destMask ^ 0xFF)) | ((0xFF if pixels > 0 and pixels < 3 else 0x00) & destMask)
                destBuf2[i] = (int(destBuf2[i]) & (destMask ^ 0xFF)) | ((0xFF if pixels > 1 else 0x00) & destMask)
            destMask = destMask >> 1
            srcMask = srcMask >> 2
            if srcMask == 0:
                srcMask = 0b10000000
                nextByte = 1

        return self.transformFB1, self.transformFB2

    @micropython.viper
    def _grayscaleTransform(self, chipDisp):
        # These are the easy (and fast) cases
        if self._colourMap == "BWDL":
            return chipDisp.frameBuffers[0], chipDisp.frameBuffers[1]
        if self._colourMap == "BDWL":
            return chipDisp.frameBuffers[1], chipDisp.frameBuffers[0]

        # Otherwise, do a transformation
        srcBuf1:ptr8 = chipDisp.buffers[0]
        srcBuf2:ptr8 = chipDisp.buffers[1]
        size:int = int(len(srcBuf1))
        lookup:ptr8 = self._colourLookup

        if not hasattr(self, 'transformBuf1'):
            width:int = int(chipDisp.width) // 8
            self.transformBuf1 = bytearray(size)
            self.transformFB1 = FrameBuffer(self.transformBuf1, int(chipDisp.width), int(chipDisp.height), MONO_HLSB)
            self.transformBuf2 = bytearray(size)
            self.transformFB2 = FrameBuffer(self.transformBuf2, int(chipDisp.width), int(chipDisp.height), MONO_HLSB)
        destBuf1:ptr8 = self.transformBuf1
        destBuf2:ptr8 = self.transformBuf2

        mask:int = 0b10000000
        inA:int
        inB:int
        outA:int
        outB:int
        while mask != 0:
            for i in range(size):
                i = int(i)

                # Determine the 'colour' of the destination
                inA = 1 if int(srcBuf1[i]) & mask else 0
                inB = 1 if int(srcBuf2[i]) & mask else 0
                outA = int(lookup[0][inA][inB])
                outB = int(lookup[1][inA][inB])

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
