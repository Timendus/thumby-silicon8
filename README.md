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

While Silicon8 is not in the "Arcade" yet, you can manually download or copy &
paste the MicroPython files from [`Games/Silicon8`](./Games/Silicon8) in this
repository and load them onto your Thumby using the [Thumby
IDE](https://tinycircuits.github.io/).

(_When running in the emulator: Being able to load multiple files is a
must, so use the [`/testing`](https://tinycircuits.github.io/testing/) version
if still needed._)

### Getting CHIP-8 ROMs into Silicon8 for Thumby

CHIP-8 ROMs should be placed on your Tumby in a directory called `CHIP-8 roms`
in the root of the file system. To get you started, try to copy a few of the
games in [this repository](./CHIP-8 roms) to your device!

You can put any `*.ch8` file in your `CHIP-8 roms` directory and it will be
picked up by Silicon8. If you want, you can add a JSON file with the same name
(so `somegame.ch8` would become `somegame.json`) to configure your ROM.

The config file accepts this structure:

```json
{
  "name": "The Classic Game of Pong",
  "type": "SCHIP",
  "keys": {
    "up": 1,
    "down": 4
  }
}
```

Valid options for `type` are `AUTO`, `VIP`, `SCHIP` or `XOCHIP`. Valid options
for the keys are `up`, `down`, `left`, `right`, `a` and `b` for all the buttons
on the Thumby. The numeric values are the corresponding keys to be pressed on
the CHIP-8 keypad (0 - 15).

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
it's a little better on the actual hardware. If you have any ideas or
suggestions on how to boost the speed, please let me know. An issue or pull
request on this repository will get my attention.

### Type "AUTO"

Like the original Silicon8, Silicon8 for Thumby has a mode "AUTO" that tries to
auto-detect the right interpreter type. This doesn't always correctly identify
SCHIP and XO-CHIP programs when they do rely on quirks for those platforms, but
don't use any of the features of those platforms. You can easily work around
this issue by specifying the interpreter type explicitly in the JSON config
file that corresponds to your wrongly detected ROM.
