# Silicon8 for Thumby

[Silicon8](https://github.com/Timendus/silicon8) is an implementation of a
runtime for CHIP-8, SCHIP and XO-CHIP that was initially built in Go, and
targeted mainly at WebAssembly. This version of it is a port to MicroPython for
the [Thumby](https://thumby.us/pages/beta) playable keychain.

The interpretation of CHIP-8, SCHIP and XO-CHIP is pretty close to the originals
but please be aware that the auto-detection doesn't always correctly identify
SCHIP and XO-CHIP programs. You can work around that by specifying the
interpretation type explicitly.

Due to the small screen size and the limited colours of the Thumby, Silicon8 is
currently limited to `lowres` mode (64x32 pixels) in monochrome. I have some
ideas on how to improve this in the future, but I will need to hold the physical
hardware first to be able to determine their feasibility.

This is my first experiment with MicroPython and the Thumby, so it's probably an
inefficient mess in the eyes of a "real" MicroPython developer. But this is a
fun learning project for me 😄

## Installation

While it's not in the "Arcade" yet, you can manually download or copy & paste
[`main.py`](./main.py) from this repository and load it onto your Thumby using
the [Thumby IDE](https://tinycircuits.github.io/).

### Getting games into Silicon8 for Thumby

For the time being, you have to hardcode a ROM into `main.py`. At the bottom of
the file, where it says `cpu.loadProgram(....)` you can supply any ROM you like
in the form of an array or tuples of bytes. You can use the `convert.js` script
to convert any `*.ch8` file into the right form.

I plan on having Silicon8 find any `*.ch8` files on the Thumby filesystem and
allowing you to run those. But since the filesystem isn't stable yet in the
emulator and I don't have the physical product yet, this will not be implemented
for a while.
