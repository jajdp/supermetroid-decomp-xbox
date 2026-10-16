# Notice

*(Español: [NOTICE.es.md](NOTICE.es.md))*

## Not affiliated

This is an unofficial, noncommercial fan project. It is **not affiliated with, endorsed by or
connected to Nintendo or Microsoft**, nor to the authors of
[snesrev/sm](https://github.com/snesrev/sm), of the zelda3 UWP port, or of
[SDL](https://github.com/libsdl-org/SDL). *Super Metroid*, *Xbox* and all related names and marks are
the property of their respective owners.

Nothing here is for sale, and nothing here is monetized.

## What this repository does not distribute

No ROM. No game assets — not the asset blob the project extracts from your dump either. No built
executable. No `.msix` package. No save data. No package tiles, which were made from the game's own
artwork. No signing certificate: note that Visual Studio drops a `*_TemporaryKey.pfx` next to a UWP
project, and that is a **private key**; the `.gitignore` blocks it by name.

## What it does contain of other people's work

| | Lines | What it is | License |
|---|---|---|---|
| Our own patch lines | 165 | What the patch adds to your checkout, behind `#ifdef SM_UWP` | ours, MIT |
| Quoted from snesrev/sm | 102 | The **context lines** a unified diff carries to know where each change goes, plus the 2 lines it removes | the project's own, MIT (`LICENSE.txt`) |
| `uwpfunc.cpp`, `uwpfunc.h` | — | The UWP helpers, taken from the **zelda3 UWP port**, which is MIT and comes from the same engine family | MIT |
| `SDL_winrt_main_NonXAML.cpp`, `SDL2-WinRTResources.rc`, `SDL2-WinRTResource_BlankCursor.cur` | — | **SDL2's own** WinRT entry point and resources, unmodified | zlib |
| `sm_uwp.vcxproj` | — | The Visual Studio project, generated here from the project's desktop one | ours, MIT |

The ROM is yours to supply and never travels through here. What the recipe carries about it is a
**SHA-256 hash** — a fingerprint, not content.

## Takedown

If you hold rights to any of the above and want something removed, write to
**jajdpmail@gmail.com** and it will be taken down. No argument, no delay.
