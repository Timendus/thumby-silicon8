from thumbyGraphics import display
from thumbyButton import buttonA, buttonB, buttonU, buttonD, buttonL, buttonR
from time import ticks_ms

class Menu:
    def __init__(self, selected = 0, scroll = 0):
        self.selected = selected
        self.scroll = scroll

    def choose(self, programs):
        self.programs = programs
        self.programs.append({
            "name": "Quit Silicon8",
            "file": False
        })
        while True:
            self.animate = 0
            self.render()
            self.lastInputTime = ticks_ms()
            self.lastAnimateTime = ticks_ms()
            if self.waitInput():
                return self.programs[self.selected], self.selected, self.scroll

    def waitInput(self):
        # Wait for button release
        while buttonU.pressed() or buttonD.pressed() or buttonA.pressed() or buttonB.pressed():
            pass
        # Wait for button press
        while True:
            if buttonU.pressed() and self.selected > 0:
                self.selected -= 1
                if self.selected < self.scroll:
                    self.scroll -= 1
                return False
            if buttonD.pressed() and self.selected < len(self.programs)-1:
                self.selected += 1
                if self.selected - 3 > self.scroll:
                    self.scroll += 1
                return False
            if buttonA.pressed() or buttonB.pressed():
                return True

            # Wait for animation to start
            now = ticks_ms()
            if now - self.lastInputTime > 300 and now - self.lastAnimateTime > 20:
                nameLength = len(self.programs[self.selected]["name"])
                if nameLength > 12:
                    if self.animate > (nameLength + 2) * 6:
                        self.animate = 0
                    else:
                        self.animate += 1
                    self.lastAnimateTime = now
                    self.render()

    def printline(self, string, highlight = False):
        if highlight:
            display.drawFilledRectangle(0, self.row - 1, display.width, 9, 1)
            display.drawText(string, 1 - self.animate, self.row, 0)
            if len(string) > 12:
                display.drawText(string, (len(string) + 2) * 6 - self.animate + 2, self.row, 0)
        else:
            display.drawText(string, 1, self.row, 1)
        self.row += 8

    def render(self):
        display.fill(0)
        self.row = 1
        for i in range(self.scroll, len(self.programs)):
            self.printline(self.programs[i]["name"], self.selected == i)
        display.update()

class Confirm:
    def __init__(self):
        self.selected = 0
        self.scroll = 0
        self.textHeight = 0

    def choose(self, program):
        # What to display about this program?
        totalText = program["name"] + '\n\n' + program["desc"]
        if "link" in program:
            totalText += '\n\nMore info:\n' + program["link"]
        self.text = self.breakText(totalText)

        while True:
            self.render()
            while buttonU.pressed() or \
                  buttonD.pressed() or \
                  buttonA.pressed() or \
                  buttonB.pressed() or \
                  buttonL.pressed() or \
                  buttonR.pressed():
                pass
            while True:
                if buttonL.pressed():
                    self.selected = 1
                    break
                if buttonR.pressed():
                    self.selected = 0
                    break
                if buttonU.pressed() and self.scroll > 0:
                    self.scroll -= 1
                    break
                if buttonD.pressed() and self.scroll < len(self.text) - 3:
                    self.scroll += 1
                    break
                if buttonA.pressed() or buttonB.pressed():
                    return self.selected == 0

    # Figure out where to break the sentence so it makes sense to the reader.
    @micropython.native
    def breakText(self, text):
        c = const(12) # Max characters per line
        result = []
        i = 0
        while i < len(text):
            # Where to break this line?
            j = i
            brk = i + c
            while j < len(text) and j - i < c + 1:
                a = text[j]
                if j - i < c and (a == '/' or a == '&'):
                    brk = j + 1
                if a == ' ':
                    brk = j + 1
                if a == '\n':
                    brk = j + 1
                    break
                j += 1
            if j == len(text):
                brk = len(text)
            result.append(text[i:brk])
            i = brk
        return result

    @micropython.native
    def render(self):
        dt = display.drawText
        display.fill(0)

        # Show game information
        for i in range(0,4):
            j = self.scroll + i
            if j < len(self.text):
                dt(self.text[j], 0, i*8, 1)

        # Show bottom menu
        height = 10
        top = display.height - height
        middle = int(display.width / 2)
        display.drawFilledRectangle(0, top, display.width, height, 1)
        display.drawFilledRectangle(self.selected * middle, top + 1, middle, height - 1, 0)
        dt("BACK", 6, top + 2, self.selected ^ 1)
        dt("RUN", middle + 10, top + 2, self.selected)
        display.update()
