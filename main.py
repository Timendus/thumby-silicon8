# Silicon8 for Thumby
# By Timendus

# This is a (crappy start at a) CHIP-8 interpreter

import time
import gc
import random
import thumby
import machine
from framebuf import FrameBuffer, MONO_VLSB

gc.enable()
# machine.freq(125000000)

splash = (
    255,255,255,255,255,255,255,31,7,195,241,241,248,248,252,252,248,248,241,241,243,255,255,255,255,255,223,223,63,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,31,15,135,227,241,249,249,249,241,227,135,15,31,255,
    255,255,255,255,255,255,255,240,224,199,143,159,159,31,63,63,63,127,127,255,255,255,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,248,240,225,71,15,31,31,31,15,71,225,240,248,255,
    255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,254,254,252,240,1,7,255,255,59,191,255,255,0,255,255,59,191,255,255,255,127,191,191,191,255,255,255,127,191,191,127,255,255,255,63,191,191,191,127,255,255,255,3,1,240,252,254,255,255,255,254,252,240,1,3,255,
    255,207,143,143,31,31,63,63,63,63,63,63,63,63,31,159,143,199,227,240,248,254,255,255,192,255,255,255,192,255,255,192,255,255,255,240,239,223,223,223,255,255,240,239,223,223,239,240,255,255,192,255,255,255,255,192,255,255,252,248,240,227,199,207,207,207,199,227,240,248,252,255,
    255,195,189,189,189,255,131,239,239,131,255,133,255,131,235,235,247,255,215,171,171,215,255,255,255,189,129,189,255,131,251,251,135,255,193,187,255,199,171,171,167,255,131,247,251,255,131,235,235,247,255,131,247,251,255,199,171,171,167,255,193,187,255,199,171,171,167,255,131,247,251,255
)

ibm = (
    0x00, 0xe0, 0xa2, 0x2a, 0x60, 0x0c, 0x61, 0x08, 0xd0, 0x1f, 0x70, 0x09, 0xa2, 0x39, 0xd0, 0x1f,
    0xa2, 0x48, 0x70, 0x08, 0xd0, 0x1f, 0x70, 0x04, 0xa2, 0x57, 0xd0, 0x1f, 0x70, 0x08, 0xa2, 0x66,
    0xd0, 0x1f, 0x70, 0x08, 0xa2, 0x75, 0xd0, 0x1f, 0x12, 0x28, 0xff, 0x00, 0xff, 0x00, 0x3c, 0x00,
    0x3c, 0x00, 0x3c, 0x00, 0x3c, 0x00, 0xff, 0x00, 0xff, 0xff, 0x00, 0xff, 0x00, 0x38, 0x00, 0x3f,
    0x00, 0x3f, 0x00, 0x38, 0x00, 0xff, 0x00, 0xff, 0x80, 0x00, 0xe0, 0x00, 0xe0, 0x00, 0x80, 0x00,
    0x80, 0x00, 0xe0, 0x00, 0xe0, 0x00, 0x80, 0xf8, 0x00, 0xfc, 0x00, 0x3e, 0x00, 0x3f, 0x00, 0x3b,
    0x00, 0x39, 0x00, 0xf8, 0x00, 0xf8, 0x03, 0x00, 0x07, 0x00, 0x0f, 0x00, 0xbf, 0x00, 0xfb, 0x00,
    0xf3, 0x00, 0xe3, 0x00, 0x43, 0xe0, 0x00, 0xe0, 0x00, 0x80, 0x00, 0x80, 0x00, 0x80, 0x00, 0x80,
    0x00, 0xe0, 0x00, 0xe0
)

AUTO      = 0
VIP       = 1
SCHIP     = 2
XOCHIP    = 3

# Main Silicon8 class that holds the virtual CPU
class Silicon8:
    def __init__(self):
        # CHIP-8 interpreter state
        self.ram = [0] * 4096 # (65023 + 512)
        self.stack = [0] * 16
        self.v = [0] * 16
        self.pc = 0x200
        self.sp = 15
        self.i = 0
        self.dt = 0
        self.st = 0
        self.keyboard = [0] * 16
        self.userFlags = [0] * 16

        self.specType = 0
        self.typeFixed = False
        self.running = True

        self.shiftQuirk = False
        self.jumpQuirk = False
        self.memQuirk = False
        self.vfQuirk = False
        self.clipQuirk = False
        self.dispQuirk = False

    def setQuirks():
        self.shiftQuirk = self.specType == SCHIP
    	self.jumpQuirk = self.specType == SCHIP
    	self.memQuirk = self.specType != SCHIP
    	self.vfQuirk = self.specType == VIP
    	self.clipQuirk = self.specType != XOCHIP
    	self.dispQuirk = self.specType == VIP

    def loadProgram(self, program):
        for i in range(0, len(program)):
            self.ram[i + 0x200] = program[i]

    # Run the CPU for one cycle and return control
    def cycle(self):
        op  = self.ram[self.a(self.pc)]<<8 | self.ram[self.a(self.pc+1)]
        x   = self.ram[self.a(self.pc)] & 0x0F
        y   = (self.ram[self.a(self.pc+1)] & 0xF0) >> 4
        n   = self.ram[self.a(self.pc+1)] & 0x0F
        nn  = self.ram[self.a(self.pc+1)] & 0xFF
        nnn = x<<8 | nn

        self.pc += 2

        check = op & 0xF000
        if check == 0:
            self.machineCall(op, n)
        elif check == 0x1000:
            # Jump
            self.pc = nnn
        elif check == 0x2000:
            # Call
            self.stack[self.s(self.sp)] = self.pc
            self.sp -= 1
            self.pc = nnn
        elif check == 0x3000:
            if v[x] == nn:
                self.skipNextInstruction()
        elif check == 0x4000:
            if v[x] != nn:
                self.skipNextInstruction()
        elif check == 0x5000:
            if x > y:
                n = x
                x = y
                y = n

            if n == 2:
                # Store range of registers to memory
                for i in range(x, y + 1):
                    self.ram[self.a(self.i+(i-x))] = self.v[i]
                self.bumpSpecType(XOCHIP)
            elif n == 3:
                # Load range of registers from memory
                for i in range(x, y + 1):
                    self.v[i] = self.ram[self.a(self.i+(i-x))]
                self.bumpSpecType(XOCHIP)
            else:
                if self.v[x] == self.v[y]:
                    self.skipNextInstruction()
        elif check == 0x6000:
            # Set register
            self.v[x] = nn
        elif check == 0x7000:
            # Add to register
            self.v[x] += nn
        elif check == 0x8000:
            self.maths(x, y, n)
        elif check == 0x9000:
            if self.v[x] != self.v[y]:
                self.skipNextInstruction()
        elif check == 0xA000:
            # Set i
            self.i = nnn
        elif check == 0xB000:
            # Jump to i + "v0"
            if self.jumpQuirk:
                self.pc = nnn + self.v[x]
            else:
                self.pc = nnn + self.v[0]
        elif check == 0xC000:
            # Set register to random number
            self.v[x] = random.randint(0, 255) & nn
        elif check == 0xD000:
            self.draw(x, y, n)
        elif check == 0xE000:
            if nn == 0x9E:
                if self.keyboard[self.v[x]]:
                    self.skipNextInstruction()
            elif nn == 0xA1:
                if not self.keyboard[self.v[x]]:
                    self.skipNextInstruction()
        elif check == 0xF000:
            if nn == 0x00:
                # Set i register to 16-bit value
                self.i = self.ram[self.a(self.pc)]<<8 | self.ram[self.a(self.pc+1)]
                self.pc += 2
                self.bumpSpecType(XOCHIP)
            elif nn == 0x01:
                # Select plane X
                # No-op in this implementation
                # TODO
                self.bumpSpecType(XOCHIP)
            elif nn == 0x02:
                # XO-Chip: Load 16 bytes of audio buffer from (i)
                # No-op in this implementation
                # TODO
                self.bumpSpecType(XOCHIP)
            elif nn == 0x07:
                # Set register to value of delay timer
    			self.v[x] = self.dt
            elif nn == 0x0A:
                # Wait for keypress and return key in vX
                # TODO
                nop = 1
            elif nn == 0x15:
    			# Set delay timer to value in vX
                self.dt = self.v[x]
            elif nn == 0x18:
    			# Set sound timer to value in vX
                self.st = self.v[x]
            elif nn == 0x1E:
    			# Add vX to i register
                self.i += self.v[x]
            elif nn == 0x29:
    			# Set i register to font data
                self.i = self.v[x] * 5
            elif nn == 0x30:
    			# Set i register to large font data
                self.i = self.v[x]*10 + 80
                self.bumpSpecType(SCHIP)
            elif nn == 0x33:
                # Binary coded decimal from vX to address in i
                self.ram[self.a(self.i+0)] = self.v[x] / 100
                self.ram[self.a(self.i+1)] = self.v[x] % 100 / 10
                self.ram[self.a(self.i+2)] = self.v[x] % 10
            elif nn == 0x3A:
    			# XO-Chip: Change pitch of audio pattern
    			# cpu.pitch = 4000 * math.Pow(2, (float64(cpu.v[x])-64)/48)
    			# cpu.playingPattern = true
    			# cpu.audioDirty = true
                self.bumpSpecType(XOCHIP)
            elif nn == 0x55:
    			# Store registers to memory (regular VIP/SCHIP)
                for i in range(0, x + 1):
                    self.ram[self.a(self.i + i)] = self.v[i]
                if self.memQuirk:
                    self.i += x + 1
            elif nn == 0x65:
    			# Load registers from memory (regular VIP/SCHIP)
                for i in range(0, x + 1):
                    self.v[i] = self.ram[self.a(self.i + i)]
                if self.memQuirk:
                    self.i += x + 1
            elif nn == 0x75:
    			# Store registers to "user flags" (SCHIP)
                for i in range(0, x + 1):
                    self.userFlags[i] = self.v[i]
                self.bumpSpecType(SCHIP)
            elif nn == 0x85:
    			# Load registers from "user flags" (SCHIP)
                for i in range(0, x + 1):
                    self.v[i] = self.userFlags[i]
                self.bumpSpecType(SCHIP)

    def machineCall(self, op, n):
        check = op & 0xFFF0
    	if check == 0x00C0:
            # TODO
    		# self.scrollDown(n)
    		self.bumpSpecType(SCHIP)
    		return
    	elif check == 0x00D0:
            # TODO
    		# self.scrollUp(n)
    		self.bumpSpecType(XOCHIP)
    		return

        if op == 0x00E0:
            # Clear screen
            thumby.display.fill(0)
        elif op == 0x00EE:
            # Return
            self.sp += 1
            self.pc = self.stack[self.s(self.sp)]
        elif op == 0x00FB:
            # TODO
    		# self.scrollRight()
    		self.bumpSpecType(SCHIP)
    	elif op == 0x00FC:
            # TODO
    		# self.scrollLeft()
    		self.bumpSpecType(SCHIP)
    	elif op == 0x00FD:
    		# "Exit" interpreter. Will just halt in our implementation
    		self.running = false
    		self.bumpSpecType(SCHIP)
    	elif op == 0x00FE:
            # TODO
    		# Set normal screen resolution
    		# self.initDisplay(64, 32, self.planes)
    		# self.clearPlanes(0)
    		self.bumpSpecType(SCHIP)
    	elif op == 0x00FF:
            # TODO
    		# Set extended screen resolution
    		# self.initDisplay(128, 64, self.planes)
    		# self.clearPlanes(0)
    		self.bumpSpecType(SCHIP)
    	else:
            print("RCA 1802 assembly calls not supported at address", self.pc-2, "opcode" op)
    		self.running = false

    def maths(self, x, y, n):
    	if n == 0x0:
    		self.v[x] = self.v[y]
    	elif n == 0x1:
    		self.v[x] |= self.v[y]
    		if self.vfQuirk:
    			self.v[0xF] = 0
    	elif n == 0x2:
    		self.v[x] &= self.v[y]
    		if self.vfQuirk:
    			self.v[0xF] = 0
    	elif n == 0x3:
    		self.v[x] ^= self.v[y]
    		if self.vfQuirk:
    			self.v[0xF] = 0
    	elif n == 0x4:
    		# Add register vY to vX
    		# Set VF to 01 if a carry occurs
    		# Set VF to 00 if a carry does not occur
    		flag = (0xFF - self.v[x]) < self.v[y]
    		self.v[x] += self.v[y]
    		self.setFlag(flag)
    	elif n == 0x5:
    		# Subtract register vY from vX and store in vX
    		# Set VF to 00 if a borrow occurs
    		# Set VF to 01 if a borrow does not occur
    		flag = self.v[x] >= self.v[y]
    		self.v[x] -= self.v[y]
    		self.setFlag(flag)
    	elif n == 0x6:
    		# Shift right
    		if self.shiftQuirk:
    			y = x
    		# Set register VF to the least significant bit prior to the shift
    		flag = self.v[y]&0b00000001 > 0
    		self.v[x] = self.v[y] >> 1
    		self.setFlag(flag)
    	elif n == 0x7:
    		# Subtract register vX from vY and store in vX
    		# Set VF to 00 if a borrow occurs
    		# Set VF to 01 if a borrow does not occur
    		flag = self.v[y] >= self.v[x]
    		self.v[x] = self.v[y] - self.v[x]
    		self.setFlag(flag)
    	elif n == 0xE:
    		# Shift left
    		if self.shiftQuirk:
    			y = x
    		# Set register VF to the most significant bit prior to the shift
    		flag = self.v[y]&0b10000000 > 0
    		self.v[x] = self.v[y] << 1
    		self.setFlag(flag)

    def skipNextInstruction(self):
        nextInstruction = self.ram[self.a(self.pc)]<<8 | self.ram[self.a(self.pc+1)]
    	if nextInstruction == 0xF000:
            self.pc += 4
        else:
            self.pc += 2

    def a(self, address):
        # TODO
        return address

    def s(self, address):
        # TODO
        return address

    def bumpSpecType(self, newType):
        if self.typeFixed:
    		return
    	if newType > self.specType:
    		self.specType = newType
    		self.setQuirks()
    		if newType == SCHIP:
    			print("Auto-upgraded interpreter to SCHIP")
    		elif newType == XOCHIP:
    			print("Auto-upgraded interpreter to XOCHIP")

    def setFlag(self, comparison):
        self.v[0xF] = 0
        if comparison:
            self.v[0xF] = 1

    def draw(self, x, y, n):
        # TODO
        sprite = ( 0xFF, 0xFF, 0xFF )
        thumby.display.blit(sprite, self.v[x], self.v[y], 8, 3)
        thumby.display.update()


thumby.audio.stop()
thumby.display.blit(splash, 0, 0, 72, 40)
thumby.display.update()

cpu = Silicon8()
cpu.loadProgram(ibm)
for i in range(0, 10):
    cpu.cycle()
