# tools/

*(Español: [README.es.md](README.es.md))*

One script, because this port is packaged by MSBuild and not by hand.

`apply_uwp.py` applies the recipe to **your** checkout: the patch over 4 source files, and
six files the project does not have. Both halves or neither — a half-applied checkout is the one
state worth protecting against.

```powershell
python tools\apply_uwp.py <your checkout>          # do it
python tools\apply_uwp.py <your checkout> --check  # report, write nothing
python tools\apply_uwp.py <your checkout> --revert # undo both halves
python tools\apply_uwp.py --list                   # what every piece is for
```

It is plain Python 3, standard library only, and it takes the checkout as an argument: there is no
default pointing at anyone's machine.

**What it checks before writing anything:** that the patch is a real patch (a `.patch` that went
through a shell pipeline can arrive with its newlines stripped, and then `git apply` fails in a way
that looks like *your* checkout is wrong); that the checkout is a git work tree, so the patch can
be checked rather than attempted; and whether each copied file is already there and identical.

There is no `package_uwp.py` here on purpose. In this family MSBuild compiles, packages and signs
in one step, so a packaging script of ours would only get in the way. The snesrecomp ports
(`dkc1-xbox` and friends) do have one, because there the packaging is `makeappx` by hand.
