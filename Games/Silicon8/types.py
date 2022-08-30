AUTO   = const(0)
VIP    = const(1)
SCHIP  = const(2)
XOCHIP = const(3)

typeMap = {
    "AUTO": AUTO,
    "VIP": VIP,
    "SCHIP": SCHIP,
    "XOCHIP": XOCHIP
}

def parseType(type):
    if isinstance(type, int):
        return type
    if isinstance(type, str) and type.upper() in typeMap:
        return typeMap[type.upper()]

MONOCHROME = const(0)
GRAYSCALE = const(1)
SCALED = const(2)

dispMap = {
    "MONOCHROME": MONOCHROME,
    "GRAYSCALE": GRAYSCALE,
    "SCALED": SCALED
}

def parseDisp(type):
    if isinstance(type, int):
        return type
    if isinstance(type, str) and type.upper() in dispMap:
        return dispMap[type.upper()]
