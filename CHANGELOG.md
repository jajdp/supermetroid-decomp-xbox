# Changelog

All notable changes to this recipe. Dates are `YYYY-MM-DD`.

## 1.0.2 — 2026-10-20

### Changed

- **The README now says which console this was tested on, and which one it was not.** Everything here
  was built and measured on an **Xbox Series X** in Developer Mode; a **Series S has never been tried**,
  so nothing here says anything about one. The wording used to say "Xbox Series", which reads as if it
  covered both, and it does not.

## 1.0.1 — 2026-10-16

### Fixed

- **`LICENSE`: the explanatory block named the wrong project.** Everything after the MIT text had
  been copied from the `dkr-xbox` repository and never adapted: it said this was a derivative of
  Golden Balloon, denied granting rights in Diddy Kong Racing, quoted "the 57 lines of the upstream
  project", and listed folders this repository does not have. The MIT grant itself was correct all
  along, and `NOTICE.md` always had the right figures. The block now names snesrev/sm (MIT, in `LICENSE.txt`), the zelda3 UWP port (MIT) and SDL2 (zlib) and
  Super Metroid, and points at `NOTICE.md` for the measurements instead of repeating a number.

## 1.0.0 — 2026-10-14

First release. The port has been running on two Xbox Series X consoles since 2026-09-05 (package
0.1.0.1); this is the recipe for it, extracted, cleaned of anything local, and verified against a
fresh clone.

### Included

- `patches/01-game-src.patch`: 165 added lines over 4 files, all behind
  `#ifdef SM_UWP`.
- `src/`: the UWP helpers, SDL2's WinRT entry point and resources, and the Visual Studio project
  that builds the package.
- `tools/apply_uwp.py`: applies the patch **and** installs the new files, checks before writing,
  idempotent, with `--revert` and `--list`.
- `package/Package.appxmanifest` with `CHANGE-ME` identity, and documentation in English and
  Spanish.

### Verified before release

On a fresh clone of `snesrev/sm` at `578f90b`: the patch applies clean; the recipe reproduces the
tree the shipped package was built from — **4 of 4 patched files and 5 of 5
copied files identical byte for byte**; and it is idempotent, with `--revert` leaving the checkout
as it was. Detail in [`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md).
