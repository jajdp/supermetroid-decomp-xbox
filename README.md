# Super Metroid on Xbox — the UWP port

How to take the [snesrev/sm](https://github.com/snesrev/sm) decompilation of *Super Metroid* (Super
Nintendo, 1994) and run it **on an Xbox Series in Developer Mode**, as a UWP package you build
and sign yourself.

*(Español: [README.es.md](README.es.md))*

It is not a theory: the package built with this recipe has been running on two Xbox Series consoles
since 2026-09-05, and the one on them today is 0.1.0.1.

## What this repository is

**A recipe.** Nobody had published a UWP build of this game. What it takes is a patch over
4 source files — all of it behind `#ifdef SM_UWP`, so your desktop build is
untouched — plus six files the project does not have: the WinRT entry point, the UWP helpers, the
SDL2 WinRT resources, and the Visual Studio project that builds and packages the UWP target.

`python tools/apply_uwp.py <your checkout>` does both halves, checks before it writes, and refuses
to leave a checkout half-applied.

## What this repository is **not**

It contains **no ROM, no game assets, no built executable, no `.msix` package and no artwork**. It
cannot produce a playable game on its own, and nothing you can download here is a game. You need
your own legally dumped copy of the cartridge. See [`NOTICE.md`](NOTICE.md).

The package tiles are not here either: the ones on the real console were made from the game's own
art, which is Nintendo's. [`docs/ASSETS.md`](docs/ASSETS.md) lists the sizes.



## What you need first

| | |
|---|---|
| The game project | [snesrev/sm](https://github.com/snesrev/sm) at commit **`578f90b`**, which is what the patch is generated against |
| Your own ROM | `Super Metroid (Japan, USA) (En,Ja).sfc`, 3,145,728 bytes, SHA-256 `12b77c4bc9c1832cee8881244659065ee1d84c70c3d29e6eaf92e6798cc2ca72` |
| Visual Studio | 2022 with the **C++ UWP workload** and the v143 toolset. Unlike the snesrecomp ports, here MSBuild is what builds, packages and signs, so that workload is genuinely required |
| SDL2 | **2.26.3, from source, vendored into the checkout** and retargeted to v143. The desktop binaries will not do: UWP needs the WinRT backend compiled in |
| Windows SDK | 10.0.26100 or similar, for `makeappx` and `signtool` if you re-package with your own tiles |
| Python 3 | For `tools/apply_uwp.py` and for the project's own asset extraction. Standard library only |
| An Xbox in Developer Mode | And a certificate to sign with ([`docs/INSTALL.md`](docs/INSTALL.md) section 4) |

## How it goes

```powershell
# 1. patch and install the new files into your checkout
python tools\apply_uwp.py <path-to-your-checkout>

# 2. vendor SDL2 2.26.3 source into third_party\SDL2 and retarget it to v143 (docs/INSTALL.md)

# 3. build, package and sign with MSBuild
msbuild src\sm_uwp.vcxproj /p:Configuration=Release /p:Platform=x64 ^
        /p:AppxBundle=Never /p:UapAppxPackageBuildMode=SideloadOnly
```

Then upload the ROM itself, copied into the app folder as `sm.smc` -- this project reads the ROM at run time instead of extracting an asset blob to the app's `LocalState`, and install the `.msix` through the Device
Portal. Step by step: **[`docs/INSTALL.md`](docs/INSTALL.md)** ([en español](docs/INSTALL.es.md)).

## What it had to solve

| | Symptom | Fix |
|---|---|---|
| 1 | In UWP the process does not start at `main()` | SDL2's own WinRT entry point (`SDL_winrt_main_NonXAML.cpp`) plus the startup path in the patch |
| 2 | The desktop host writes next to the executable, which is read-only once installed | The data folder moves to the app's `LocalState`, which is the only place a packaged app may write |
| 3 | The system volume mixer would not compile | It is desktop-only COM. Compiled out behind the define, and the port leaves volume to the console |
| 4 | No gamepad | Read through `Windows.Gaming.Input` in `uwpfunc.cpp` |
| 5 | The desktop SDL2 does not work in an AppContainer | SDL2 2.26.3 is vendored and compiled for WinRT with the project |
| 6 | A UWP link fails with duplicate or missing CRT symbols | `vccorlib.lib` and `msvcrt.lib` have to come first and be listed in `IgnoreSpecificDefaultLibraries`; that ordering is in the `.vcxproj` |

The detail is in **[`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md)**.

## How it was verified

Not by reading it. On a **fresh clone of `snesrev/sm` at `578f90b`**, on 2026-10-14:

| What was measured | Result |
|---|---|
| The patch applies to a clean checkout | Yes, clean, with `git apply --check` first |
| The tree the recipe produces, against the tree the shipped package was built from | **4 of 4 patched files and 5 of 5 copied files identical, byte for byte** |
| Idempotence | A second run reports everything in place and writes nothing |
| `--revert` | Removes both halves and leaves the checkout as it was |

What has **not** been re-measured here is the MSBuild step: the package that runs on the consoles
(0.1.0.1, 4,740,639 bytes) was built with this exact tree, and rebuilding it needs the
vendored SDL2 tree, which is not something this repository can carry. The recipe is the part that
is verified; the compiler is Visual Studio's.

## Credits and license

Port and tooling by **Recompilaciones**, under the [MIT License](LICENSE).

Of other people's work this repository carries: `uwpfunc.cpp` and `uwpfunc.h`, from the **zelda3
UWP port** (MIT), and three SDL2 files (**zlib**). Both are credited in
[`NOTICE.md`](NOTICE.md), which also measures exactly how much is quoted from the game project
itself: 102 context lines in the patch, and nothing else.

*Super Metroid* is © Nintendo. This project is not affiliated with them, with Microsoft, or with the
authors of the decompilation, and it distributes nothing that belongs to them. Rights holders can
write to **jajdpmail@gmail.com**.
