# How it works

*(Español: [HOW-IT-WORKS.es.md](HOW-IT-WORKS.es.md))*

## What a UWP build changes, and what it does not

The game itself is untouched: the decompilation keeps doing what it does, and every line this
recipe adds sits behind `#ifdef SM_UWP`. What changes is everything around it, because a packaged
app on a console lives under rules a desktop build never meets:

- **It does not start at `main()`.** The process begins at `CoreApplication`. SDL2 ships the shell
  for that (`SDL_winrt_main_NonXAML.cpp`), and the patch wires the game's startup into it.
- **It cannot write next to its executable.** An installed package is read-only, so the data folder
  moves to the app's `LocalState`. That is also why the game data has to be uploaded there by hand
  once (`docs/INSTALL.md` section 5).
- **Parts of the desktop host simply do not exist.** The system volume mixer is desktop-only COM:
  it is compiled out, and the console's own volume takes over.
- **The gamepad comes from somewhere else.** `uwpfunc.cpp` reads it through
  `Windows.Gaming.Input`.

## SDL2 has to be built, not downloaded

This is the step that catches people. SDL2's desktop binaries are not usable inside an
AppContainer: they import libraries that are not there and they lack the WinRT video backend. So
2.26.3 is vendored **as source** into the checkout and compiled with the project, retargeted to the
v143 toolset.

Nothing of SDL2 is redistributed in this repository except its own WinRT entry point and two
resource files, unmodified and under its zlib license (see [`../NOTICE.md`](../NOTICE.md)).

## The link order that is not optional

A WinRT link needs `vccorlib.lib` and `msvcrt.lib` **first**, and both listed in
`IgnoreSpecificDefaultLibraries`. Get it wrong and the errors are about duplicate or missing CRT
symbols, which read like a corrupted toolchain. That ordering is baked into `sm_uwp.vcxproj`, which is
also why this recipe ships a project file rather than a list of settings to click through.

## How this was verified

Not by reading it. On a **fresh clone of `snesrev/sm` at `578f90b`**, on 2026-10-14:

| What was measured | Result |
|---|---|
| The patch applies to a clean checkout | Yes, clean, checked with `git apply --check` before writing |
| The tree the recipe produces, against the tree the shipped package was built from | **4 of 4 patched files identical, byte for byte**, and **5 of 5 copied files identical** |
| Idempotence | A second run reports everything in place and writes nothing |
| `--revert` | Reverts the patch and removes the copied files |

What is **not** re-measured here is MSBuild's own output. The package on the consoles (0.1.0.1,
4,740,639 bytes) was built from this exact tree; rebuilding it needs the vendored SDL2 tree,
which this repository cannot carry. So the verified claim is precise: the recipe reproduces the
tree. The rest is Visual Studio's compiler doing its job.

## A note on language

The code this recipe adds carries its comments in English, like the project it goes into. This
documentation is in English and Spanish.
