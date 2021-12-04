import machine

def timerfunc(t):
    print(t)

timer = machine.Timer()
timer.init(mode=timer.PERIODIC, period=2000, callback=timerfunc)
