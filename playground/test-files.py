# From https://github.com/TinyCircuits/tinycircuits.github.io/blob/master/ThumbyGames/main.py

os.chdir("/Games")
selpos = 0
files = os.listdir()
selected = False
scroll = 0

print(files)
for k in range(len(files)):
    if(os.stat("/Games/"+files[k])[0] != 16384):
        files[k] = ""
try:
    while(True):
        files.remove("")
except ValueError:
    pass
