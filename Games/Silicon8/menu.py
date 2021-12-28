import thumby
import time

class Menu:
    def __init__(self):
        self.selected = 0
        self.scroll = 0

    def choose(self, programs):
        self.programs = programs
        while True:
            self.animate = 0
            self.render()
            self.lastInputTime = time.ticks_ms()
            self.lastAnimateTime = time.ticks_ms()
            if self.waitInput():
                return self.programs[self.selected]

    def waitInput(self):
        # Wait for button release
        while thumby.buttonU.pressed() or thumby.buttonD.pressed() or thumby.buttonA.pressed() or thumby.buttonB.pressed():
            pass
        # Wait for button press
        while True:
            if thumby.buttonU.pressed() and self.selected > 0:
                self.selected -= 1
                if self.selected < self.scroll:
                    self.scroll -= 1
                return False
            if thumby.buttonD.pressed() and self.selected < len(self.programs)-1:
                self.selected += 1
                if self.selected - 3 > self.scroll:
                    self.scroll += 1
                return False
            if thumby.buttonA.pressed() or thumby.buttonB.pressed():
                return True

            # Wait for animation to start
            now = time.ticks_ms()
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
            thumby.display.drawFilledRectangle(0, self.row - 1, thumby.display.width, 9, 1)
            thumby.display.drawText(string, 1 - self.animate, self.row, 0)
            if len(string) > 12:
                thumby.display.drawText(string, (len(string) + 2) * 6 - self.animate + 2, self.row, 0)
        else:
            thumby.display.drawText(string, 1, self.row, 1)
        self.row += 8

    def render(self):
        thumby.display.fill(0)
        self.row = 1
        for i in range(self.scroll, len(self.programs)):
            self.printline(self.programs[i]["name"], self.selected == i)
        thumby.display.update()
