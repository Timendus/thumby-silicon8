# Silicon8 for Thumby

![The Silicon8 for Thumby splash screen](./pictures/emu-splash.png) ![The Silicon8 for Thumby menu system](./pictures/emu-menu.png)

![Gameplay of the game PONG](./pictures/emu-pong.png) ![Gameplay of the game Space Invaders](./pictures/emu-space.png)

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

Also, the physical Thumby keychains haven't shipped yet, so I do not yet have
access to the real hardware. This has so far been developed using the emulator
in the [Thumby IDE](https://tinycircuits.github.io/). So we have to be patient
to be able to finalise this project 📭

## Installation

While it's not in the "Arcade" yet, you can manually download or copy & paste
[`main.py`](./main.py) from this repository and load it onto your Thumby using
the [Thumby IDE](https://tinycircuits.github.io/).

### Getting CHIP-8 games into Silicon8 for Thumby

For the time being, you have to hardcode your ROMs into `main.py`. At the top of
the file, from line 38 onwards, a dictionary of programs is defined. You can add
any ROM you like to this dictionary by following the structure of the other
programs. You can use the [`convert.js`](./convert.js) script to convert any
`*.ch8` file into the right tuple of bytes (NodeJS required):

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
originals. However, there are a few issues to be aware of. If you find issues
that are not described below, please [file an
issue](https://github.com/Timendus/thumby-silicon8/issues/new).

### Display limitations

Due to the small screen size and the limited colours of the Thumby, Silicon8 for
Thumby is currently limited to `lowres` mode (64x32 pixels) in monochrome. If
you use `hires` mode, the central 72x40 pixels will be shown and the rest
discarded, which doesn't make for great gameplay. When using XO-CHIP's four
colour mode, only plane 1 will be rendered to the screen.

I have some ideas on how to improve this in the future, but I will need to play
with the physical hardware first to see if those ideas are feasible.

### Sound limitations

The Thumby has a very simple speaker. The current Thumby library does not expose
this speaker in a more complicated way than setting a frequency and a duty
cycle. You can, however, bypass the library and talk to the pin directly.
Supporting the full XO-CHIP audio capabilities on this low a level will be a bit
of a chore, that I have not yet felt like doing 😄🎶

### Speed

This interpreter is not particularly fast in the Thumby emulator. I'm hoping
it's a little better on the actual hardware. There's probably a lot to win in
simplifying the sprite drawing function, I'll look at that when I refactor all
the display stuff. If you have any other ideas or suggestions on how to boost
the speed, please let me know. An issue or pull request on this repository will
get my attention.

### Type "AUTO"

Like the original Silicon8, Silicon8 for Thumby has a mode "AUTO" that tries to
auto-detect the right interpreter type. This doesn't always correctly identify
SCHIP and XO-CHIP programs when they do rely on quirks for those platforms, but
don't use any of the features of those platforms. You can easily work around
this issue by specifying the interpreter type explicitly.
