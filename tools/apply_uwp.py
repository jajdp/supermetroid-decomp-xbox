#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply this repository's UWP recipe to your own checkout of snesrev/sm.

Two things happen here, and the second one is what makes this port different from a plain patch:

  1. one patch over four source files, all of it behind `#ifdef SM_UWP`, so your
     desktop build keeps working exactly as it did;
  2. six files that did not exist in the project are copied in — the WinRT entry point,
     the UWP helpers, the SDL2 WinRT resources and the Visual Studio project that builds the
     package.

    python tools/apply_uwp.py <path-to-game-checkout>
    python tools/apply_uwp.py <path-to-game-checkout> --check     # dry run, writes nothing
    python tools/apply_uwp.py <path-to-game-checkout> --revert    # undo both halves
    python tools/apply_uwp.py --list                              # what each piece is

Idempotent: a second run reports what is already in place and writes nothing. The patch half is
checked by asking git itself (`git apply --reverse --check`); the copied half, by comparing bytes.
Nothing is written if either half cannot be completed, because a half-applied recipe is the one
state worth protecting against.
"""
import argparse
import filecmp
import shutil
import subprocess
import sys
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8', errors='replace')

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PATCHES = REPO / 'patches'
SRC = REPO / 'src'

PATCH = '01-game-src.patch'

# (file in src/ of this repo, where it goes in the checkout, what it is)
COPIES = (
    ('uwpfunc.cpp', 'src',
     'The UWP helpers: the bits of the desktop host that have no equivalent inside an\n'
     '      AppContainer -- the data folder, the file dialogs that are not there, the gamepad\n'
     '      through Windows.Gaming.Input. Taken from the zelda3 UWP port (MIT), same engine\n'
     '      family, and credited in NOTICE.md.'),
    ('uwpfunc.h', 'src', 'Its header.'),
    ('sm_uwp.vcxproj', 'src',
     'The Visual Studio project that builds and packages the UWP target: x64 only,\n'
     '      ApplicationType = Windows Store, paths anchored to $(ProjectDir)..\\ so it works\n'
     '      from any folder, and vccorlib.lib/msvcrt.lib ordered the way a WinRT link needs.'),
    ('SDL_winrt_main_NonXAML.cpp', '.',
     'SDL2\'s own WinRT entry point (zlib). In UWP the process starts at\n'
     '      CoreApplication, not at main(), and this is the shell SDL ships for that.'),
    ('SDL2-WinRTResources.rc', '.', 'SDL2\'s WinRT resource script (zlib).'),
    ('SDL2-WinRTResource_BlankCursor.cur', '.', 'The blank cursor it references (zlib).'),
)

PATCH_WHAT = """Four source files: src/main.c, src/config.c, src/sm_rtl.c and\n      src/platform/win32/volume_control.h. Everything it adds is behind\n      #ifdef SM_UWP: the WinRT startup path, the data folder the app is\n      allowed to write to, the gamepad, and the system volume mixer\n      compiled out (it is desktop-only COM)."""


def run(cmd, cwd):
    return subprocess.run([str(c) for c in cmd], cwd=str(cwd), capture_output=True,
                          text=True, errors='replace')


def sane(patch):
    raw = patch.read_bytes()
    if not raw:
        return 'it is empty'
    if b'@@ -' not in raw:
        return 'it has no hunk header (@@), so it is not a unified diff'
    if b'\n' not in raw:
        return ('it has no line breaks at all -- %d bytes on a single line. Something rewrote it '
                'after git produced it' % len(raw))
    if not raw.endswith(b'\n'):
        return 'it does not end in a newline, and git apply needs that'
    return None


def patch_state(root, patch):
    forward = run(['git', 'apply', '--check', str(patch)], root)
    if forward.returncode == 0:
        return 'pending'
    reverse = run(['git', 'apply', '--reverse', '--check', str(patch)], root)
    if reverse.returncode == 0:
        return 'applied'
    return 'stuck: ' + (forward.stderr.strip().splitlines() or ['git apply refused it'])[-1]


def copy_state(root):
    falta, distinto, igual = [], [], []
    for nombre, destino_rel, _que in COPIES:
        origen = SRC / nombre
        destino = root / destino_rel.replace('/', '\\') / nombre
        if not destino.is_file():
            falta.append(nombre)
        elif filecmp.cmp(str(origen), str(destino), shallow=False):
            igual.append(nombre)
        else:
            distinto.append(nombre)
    return falta, distinto, igual


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('checkout', nargs='?', type=Path, help='root of your snesrev/sm checkout')
    ap.add_argument('--check', action='store_true', help='report only, write nothing')
    ap.add_argument('--revert', action='store_true', help='remove the patch and the copied files')
    ap.add_argument('--list', action='store_true', help='print what each piece does')
    a = ap.parse_args()

    if a.list:
        print('%s  ->  <checkout>' % PATCH)
        print('      ' + PATCH_WHAT + '\n')
        for nombre, destino, que in COPIES:
            print('%s  ->  <checkout>/%s' % (nombre, destino if destino != '.' else ''))
            print('      ' + que + '\n')
        return 0

    if a.checkout is None:
        ap.error('pass the path to your checkout (there is no default: this script never guesses '
                 'a path)')
    root = a.checkout.expanduser().resolve()
    if not root.is_dir() or not (root / 'src').is_dir():
        sys.exit('that does not look like a snesrev/sm checkout: expected a src/ folder inside '
                 '%s' % root)
    p = run(['git', 'rev-parse', '--is-inside-work-tree'], root)
    if p.returncode or p.stdout.strip() != 'true':
        sys.exit('%s is not a git work tree, so the patch cannot be checked before it is written.'
                 % root)

    patch = PATCHES / PATCH
    if not patch.is_file():
        sys.exit('missing patch: %s' % patch)
    mal = sane(patch)
    if mal:
        sys.exit('%s is damaged: %s.\nRe-download the repository; this is not a problem with your '
                 'checkout.' % (patch.name, mal))

    estado = patch_state(root, patch)
    falta, distinto, igual = copy_state(root)
    print('patch                     %s' % estado.split(':')[0])
    print('copied files              %d in place, %d missing, %d different'
          % (len(igual), len(falta), len(distinto)))
    if estado.startswith('stuck'):
        print('\n%s: %s' % (PATCH, estado), file=sys.stderr)
        sys.exit('\nNothing was written. Either the checkout is not the commit this recipe was '
                 'written\nagainst (see docs/DEPENDENCIES.md) or it has local changes in the files '
                 'the patch touches.')

    if a.revert:
        if estado == 'pending' and not igual and not distinto:
            print('\nNothing to do: nothing of this recipe is in that checkout.')
            return 0
        if a.check:
            print('\n--check: would revert the patch and remove %d copied file(s).'
                  % (len(igual) + len(distinto)))
            return 0
        if estado == 'applied':
            r = run(['git', 'apply', '--reverse', str(patch)], root)
            if r.returncode:
                print(r.stdout, r.stderr, file=sys.stderr)
                sys.exit('could not revert the patch')
            print('reverted  %s' % PATCH)
        for nombre, destino_rel, _que in COPIES:
            destino = root / destino_rel.replace('/', '\\') / nombre
            if destino.is_file():
                destino.unlink()
                print('removed   %s' % nombre)
        return 0

    if estado == 'applied' and not falta and not distinto:
        print('\nNothing to do: everything is already applied.')
        return 0
    if a.check:
        print('\n--check: would %sapply the patch and write %d file(s). Nothing was written.'
              % ('' if estado == 'pending' else 'not ', len(falta) + len(distinto)))
        return 0

    if estado == 'pending':
        r = run(['git', 'apply', str(patch)], root)
        if r.returncode:
            print(r.stdout, r.stderr, file=sys.stderr)
            sys.exit('the patch failed; nothing else was written')
        print('applied   %s' % PATCH)
    for nombre, destino_rel, _que in COPIES:
        origen = SRC / nombre
        carpeta = root / destino_rel.replace('/', '\\')
        carpeta.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, carpeta / nombre)
        print('copied    %s -> %s' % (nombre, destino_rel))

    print('\nDone. Next: vendor SDL2 and build (docs/INSTALL.md sections 2 and 3).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
