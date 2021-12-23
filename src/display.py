from framebuf import FrameBuffer, MONO_HLSB

# Representation of the CHIP-8 display. Supports two planes and two screen
# sizes. Implementation in MicroPython of all the operations, which isn't the
# fastest, but is accurate to CHIP-8 and friends.
class AccurateDisplay:
    def __init__(self, cpu):
        self.cpu = cpu

    def reset(self):
        self.width = 64
        self.height = 32
        self.numPlanes = 1
        self.selectedPlane = 1
        self.dirty = True
        self.waitForInt = 0
        self.initBuffers()

    @micropython.native
    def initBuffers(self):
        self.buffers = [
            bytearray(int(self.width*self.height/8)),
            bytearray(int(self.width*self.height/8))
        ]
        self.frameBuffers = [
            FrameBuffer(self.buffers[0], self.width, self.height, MONO_HLSB),
            FrameBuffer(self.buffers[1], self.width, self.height, MONO_HLSB)
        ]

    # Called by 60Hz interrupt timer for dispQuirk
    @micropython.native
    def interrupt(self):
        if self.waitForInt == 1:
            self.waitForInt = 2

    @micropython.native
    def getFrameBuffers(self):
        return self.frameBuffers

    # Clears currently selected plane
    @micropython.native
    def clear(self):
        self.clearPlanes(self.selectedPlane)

    # Clears given planes
    @micropython.native
    def clearPlanes(self, planes):
        for i in range(len(self.buffers)):
            if (i+1) & planes > 0:
                for j in range(len(self.buffers[i])):
                    self.buffers[i][j] = 0
        self.dirty = True

    @micropython.native
    def scrollDown(self, n):
        offset = int(self.width * n / 8)
        for plane in range(1, 2):
            if (plane & self.selectedPlane) == 0:
                continue
            for i in range(len(self.buffers[plane-1]) - 1, 0, -1):
                self.buffers[plane-1][i] = self.buffers[plane-1][i - offset] if i > offset else 0
            self.dirty = True

    @micropython.native
    def scrollUp(self, n):
        offset = int(self.width * n / 8)
        for plane in range(1, 2):
            if (plane & self.selectedPlane) == 0:
                continue
            maxIndex = len(self.buffers[plane-1]) - 1
            for i in range(maxIndex):
                self.buffers[plane-1][i] = self.buffers[plane-1][i + offset] if i + offset < maxIndex else 0
            self.dirty = True

    @micropython.native
    def scrollLeft(self):
        # TODO
        return
        for i in range(self.DispWidth * self.DispHeight):
            if i % self.DispWidth < self.DispWidth - 4:
                pixel = self.planeBuffer[i + 4] & self.plane
            else:
                pixel = 0
            self.planeBuffer[i] = self.planeBuffer[i] & (self.plane ^ 0xFF) | pixel
        self.SD = True

    @micropython.native
    def scrollRight(self):
        # TODO
        return
        for i in range(self.DispWidth * self.DispHeight, 0, -1):
            j = i - 1
            if j % self.DispWidth >= 4:
                pixel = self.planeBuffer[j - 4] & self.plane
            else:
                pixel = 0
            self.planeBuffer[j] = self.planeBuffer[j] & (self.plane ^ 0xFF) | pixel
        self.SD = True

    @micropython.native
    def draw(self, x, y, n):
        if self.waitForInterrupt():
            return

    	# Get real sprite position & height
    	xPos = self.cpu.v[x] % self.width
    	yPos = self.cpu.v[y] % self.height
        height = n
        if height == 0:
            self.cpu.bumpSpecType(SCHIP)
            height = 16

        # Do the actual drawing
        erases = False
        ramPointer = self.cpu.i

        for plane in range(1, 2):                   # Go through both planes
            if (plane & self.selectedPlane) == 0:   # Only manipulate if this plane is currently selected
                continue
            bufferPointer = int((yPos*self.width + xPos) / 8)
            byteOffset = xPos % 8
            for i in range(height):                 # Draw N lines
                # Does this line fall off the bottom of the screen?
                if bufferPointer >= int(self.width * self.height / 8):
                    if self.cpu.clipQuirk:
                        continue
                    else:
                        bufferPointer -= int(self.width * self.height / 8)
                pixels = self.cpu.ram[self.cpu.a(ramPointer)]
                erases = self.xorLine(pixels >> byteOffset, bufferPointer, plane) or erases
                if byteOffset > 0:
                    erases = self.xorLine(pixels << 8 - byteOffset, bufferPointer+1, plane) or erases
                ramPointer += 1
                if height == 16:
                    pixels = self.cpu.ram[self.cpu.a(ramPointer)]
                    erases = self.xorLine(pixels >> byteOffset, bufferPointer+1, plane) or erases
                    if byteOffset > 0:
                        erases = self.xorLine(pixels << 8 - byteOffset, bufferPointer+2, plane) or erases
                    ramPointer += 1
                bufferPointer += int(self.width / 8)

        self.dirty = True
        self.cpu.v[0xF] = 1 if erases else 0 # Set collision flag

    @micropython.native
    def waitForInterrupt(self):
        if not self.cpu.dispQuirk:
            return False

        if self.waitForInt == 0:
            self.waitForInt = 1
            self.cpu.pc -= 2
            return True
        elif self.waitForInt == 1:
            self.cpu.pc -= 2
            return True
        else:
            self.waitForInt = 0
            return False

    @micropython.native
    def xorLine(self, pixels, bufferPointer, plane):
        if bufferPointer >= len(self.buffers[plane-1]):
            return False
        current = self.buffers[plane-1][bufferPointer]
        erases = (current & pixels) != 0
        self.buffers[plane-1][bufferPointer] = current ^ pixels
        return erases

    @micropython.native
    def setResolution(self, width, height):
        self.width = width
        self.height = height
        self.initBuffers()




class FastDisplay:
    def __init__(self, cpu):
        self.cpu = cpu

    def reset(self):
        self.width = 64
        self.height = 32
        self.numPlanes = 1
        self.selectedPlane = 1
        self.dirty = True
        self.buffer = [
            FrameBuffer(bytearray(int(128*64/8)), 128, 64, MONO_HLSB),
            FrameBuffer(bytearray(int(128*64/8)), 128, 64, MONO_HLSB)
        ]

    def interrupt(self):
        return

    def getFrameBuffers(self):
        return self.buffer

    # Clears currently selected plane
    def clear(self):
        self.clearPlanes(self.selectedPlane)

    # Clears given planes
    def clearPlanes(self, planes):
        for i in range(len(self.buffer)):
            if (i+1) & planes > 0:
                self.buffer[i].fill(0)
        self.dirty = True

    def scrollDown(self, n):
        for i in range(len(self.buffer)):
            if (i+1) & self.selectedPlane > 0:
                self.buffer[i].scroll(0, n)

    def scrollUp(self, n):
        for i in range(len(self.buffer)):
            if (i+1) & self.selectedPlane > 0:
                self.buffer[i].scroll(0, -1 * n)

    def scrollLeft(self):
        for i in range(len(self.buffer)):
            if (i+1) & self.selectedPlane > 0:
                self.buffer[i].scroll(-1, 0)

    def scrollRight(self):
        for i in range(len(self.buffer)):
            if (i+1) & self.selectedPlane > 0:
                self.buffer[i].scroll(1, 0)

    def draw(self, x, y, n):
        # Get real sprite position & height
    	xPos = self.cpu.v[x] % self.width
    	yPos = self.cpu.v[y] % self.height
        height = n
        if height == 0:
            self.cpu.bumpSpecType(SCHIP)
            height = 16

        # TODO: 16 by 16 sprites

        sprite = self.cpu.ram[self.cpu.a(self.cpu.i):self.cpu.a(self.cpu.i + 16)]

        for i in range(len(self.buffer)):
            if (i+1) & self.selectedPlane > 0:
                self.buffer[i].blit(
                    FrameBuffer(sprite, 8, height, MONO_HLSB),
                    xPos, yPos, 8, height
                )

        self.dirty = True
        self.cpu.v[0xF] = 0 # Never a collision
        return

    def setResolution(self, width, height):
        self.width = width
        self.height = height
        self.clearPlanes(3)
