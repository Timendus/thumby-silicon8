# From https://github.com/TinyCircuits/tinycircuits.github.io/blob/master/ThumbyAPI.md

import thumby

freq = 265000
duration = 5000
duty = 32768
thumby.audio.set_enabled(True)
thumby.audio.play(freq, duration, duty)
