# Silicon8 for Thumby

[Silicon8](https://github.com/Timendus/silicon8) is an interpreter for CHIP-8,
SCHIP and XO-CHIP that was initially built in Go, and targeted mainly at
WebAssembly. This version of it is a port to MicroPython for the
[Thumby](https://thumby.us/pages/beta) playable keychain.

[CHIP-8](https://en.wikipedia.org/wiki/CHIP-8) is an interpreted programming
language, going back to the '70s. It was initially used on the COSMAC VIP and
Telmac 1800 8-bit microcomputers and was made to allow video games to be more
easily programmed for and shared among these computers. In 1990 CHIP-8 saw a
revival in the form or SCHIP on HP-48 graphing calculators, and in more recent
years the XO-CHIP extension has given it more colours, memory and better sound.
Many people still write new software for this platform, not in the least at the
yearly [Octojam](https://itch.io/jam/octojam-8).

This is my first experiment with MicroPython and the Thumby, so it's probably an
inefficient mess in the eyes of a "real" MicroPython developer. But this is a
fun learning project for me 😄

## Installation

While it's not in the "Arcade" yet, you can manually download or copy & paste
[`main.py`](./main.py) from this repository and load it onto your Thumby using
the [Thumby IDE](https://tinycircuits.github.io/).

### Getting CHIP-8 games into Silicon8 for Thumby

For the time being, you have to hardcode your ROMs into `main.py`. At the top of
the file, from line 38 onwards, a dictionary of programs is defined. You can add
any ROM you like to this dictionary by following the structure of the other
programs. You can use the [`convert.js`](./convert.js) script to convert any
`*.ch8` file into the required tuple of bytes (NodeJS required):

```bash
git clone git@github.com:Timendus/thumby-silicon8.git
cd thumby-silicon8
./convert.js /path/to/pong.ch8
```

I plan on having Silicon8 for Thumby find any `*.ch8` files on the Thumby
filesystem and allow you to run those. But since the filesystem isn't stable yet
in the emulator, again we will have to be patient until the actual devices get
shipped.

## Known issues

The interpretation of CHIP-8, SCHIP and XO-CHIP should be pretty close to the
originals. However, there are a few issues to be aware of.

### Missing instructions

The SCHIP/XO-CHIP scroll instructions have yet to be ported.

Also, sound doesn't work at all yet.

### Speed

This interpreter is not particularly fast in the Thumby emulator. I'm hoping
it's a little better on the actual hardware. If you have ideas or suggestions on
how to boost the speed, please let me know. An issue or pull request on this
repository will get my attention.

### Display limitations

Due to the small screen size and the limited colours of the Thumby, Silicon8 for
Thumby is currently limited to `lowres` mode (64x32 pixels) in monochrome. If
you use `hires` mode, the central 72x40 pixels will be shown and the rest
discarded. When using XO-CHIP's four colour mode, only plane 1 will be rendered
to the screen.

I have some ideas on how to improve this in the future, but I will need to play
with the physical hardware first to be able to determine their feasibility. And since the Thumby keychains haven't shipped yet, we have to be patient 📭

### Type "AUTO"

Like the original Silicon8, Silicon8 for Thumby has a mode "AUTO" that tries to
auto-detect the right interpreter type. This doesn't always correctly identify
SCHIP and XO-CHIP programs when they do rely on quirks for those platforms, but
don't use any of the features of those platforms. You can work around this issue
by specifying the interpreter type explicitly.
