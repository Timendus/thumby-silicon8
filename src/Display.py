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
        self.buffer = [
            bytearray(int(128*64/8)),
            bytearray(int(128*64/8))
        ]

    # Called by 60Hz interrupt timer for dispQuirk
    def interrupt(self):
        if self.waitForInt == 1:
            self.waitForInt = 2

    def getFrameBuffers(self):
        return self.buffer
        # return [
        #     FrameBuffer(self.buffer[0], 128, 64, MONO_HLSB),
        #     FrameBuffer(self.buffer[1], 128, 64, MONO_HLSB)
        # ]

    # Clears currently selected plane
    def clear(self):
        self.clearPlanes(self.selectedPlane)

    # Clears given planes
    def clearPlanes(self, planes):
        for i in range(len(self.buffer)):
            if (i+1) & planes > 0:
                for j in range(len(self.buffer[i])):
                    self.buffer[i][j] = 0
        self.dirty = True

    def scrollDown(self, n):
        # TODO
        return
        offset = self.DispWidth * n
        for i in range(self.DispWidth * self.DispHeight, 0, -1):
            j = i - 1
            if j > offset:
                pixel = self.planeBuffer[j - offset] & self.plane
            else:
                pixel = 0
            self.planeBuffer[j] = self.planeBuffer[j] & (self.plane ^ 0xFF) | pixel
        self.SD = True

    def scrollUp(self, n):
        # TODO
        return
        offset = self.DispWidth * n
        for i in range(self.DispWidth * self.DispHeight):
            if i + offset > self.DispWidth * self.DispHeight:
                pixel = self.planeBuffer[i + offset] & self.plane
            else:
                pixel = 0
            self.planeBuffer[i] = self.planeBuffer[i] & (self.plane ^ 0xFF) | pixel
        self.SD = True

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
        plane = 1

        # TODO: fix weird erase bug

        while plane < 4:                            # Go through two planes
            if (plane & self.selectedPlane) != 0:   # If this plane is currently selected
                planeBufPointer = int(yPos*self.width/8 + xPos / 8)
                byteOffset = xPos % 8
                for i in range(height):             # Draw N lines
                    # Does this line fall off the bottom of the screen?
                    if planeBufPointer > int(self.width * self.height / 8):
                        if self.cpu.clipQuirk:
                            continue
                        else:
                            planeBufPointer -= int(self.width * self.height / 8)
                    pixels = self.cpu.ram[self.cpu.a(ramPointer)]
                    erases = erases or self.xorLine(pixels >> byteOffset, planeBufPointer, plane) or self.xorLine(pixels << 8 - byteOffset, planeBufPointer+1, plane)
                    ramPointer += 1
                    if height == 16:
                        pixels = self.cpu.ram[self.cpu.a(ramPointer)]
                        erases = erases or self.xorLine(pixels >> byteOffset, planeBufPointer+8, plane) or self.xorLine(pixels << 8 - byteOffset, planeBufPointer+9, plane)
                        ramPointer += 1
                    planeBufPointer += int(self.width / 8)
            plane = plane << 1

        self.dirty = True
        self.cpu.v[0xF] = 1 if erases else 0 # Set collision flag

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

    def xorLine(self, pixels, planeBufPointer, plane):
        current = self.buffer[plane-1][planeBufPointer]
        erases = (current & pixels) != 0
        self.buffer[plane-1][planeBufPointer] = current ^ pixels
        return erases

    def setResolution(self, width, height):
        self.width = width
        self.height = height
        self.clearPlanes(3)




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
