# Install — from a clean checkout to the game running on the console

*(Español: [INSTALL.es.md](INSTALL.es.md))*

## 0. Where you type these commands

- **PowerShell** (press **Windows**, type `powershell`, **Enter**) for `apply_uwp.py`, the
  certificate and the Device Portal.
- **The "Developer Command Prompt for VS 2022"** (same menu, type `developer`) for `msbuild`.

**You do not need "run as administrator"**, and using it would break section 4: the certificate is
created in the store of whoever runs the command.

## 1. Clone the game project

```powershell
git clone https://github.com/snesrev/sm.git C:\sm
cd C:\sm
git checkout 578f90b
```

That commit is what the patch was generated against. A later one may still work — `apply_uwp.py`
checks and tells you before writing anything.

## 2. Apply the recipe, then vendor SDL2

```powershell
python <this repo>\tools\apply_uwp.py C:\sm
```

It applies the patch over 4 files and copies in six more. `--check` reports without
writing, `--revert` undoes both halves, `--list` explains every piece.

Then SDL2, which is the step people underestimate: **the desktop SDL2 will not work inside an
AppContainer.** You need 2.26.3 **from source**, in `third_party\SDL2\` of your checkout, with
its Visual Studio project retargeted to the v143 toolset so it builds alongside the game. Download
the 2.26.3 source release from SDL's own releases, unpack it there, open its UWP solution once and
let Visual Studio retarget it.

## 3. Build, package and sign

In the **Developer Command Prompt**:

```
msbuild src\sm_uwp.vcxproj /p:Configuration=Release /p:Platform=x64 ^
        /p:AppxBundle=Never /p:UapAppxPackageBuildMode=SideloadOnly
```

MSBuild does all three things here — compiles, packages and signs — which is why the **C++ UWP
workload** is a real requirement for this port and not for the snesrecomp ones.

Before that, open [`../package/Package.appxmanifest`](../package/Package.appxmanifest) and replace
the two `CHANGE-ME` values; section 4 explains what each one does. The manifest in the project
folder is the one MSBuild reads.

## 4. A certificate to sign with

```powershell
New-SelfSignedCertificate -Type Custom -Subject "CN=<your name>" -KeyUsage DigitalSignature `
  -FriendlyName "<your name> UWP dev" -CertStoreLocation "Cert:\CurrentUser\My" `
  -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
```

`Publisher` in the manifest must be **exactly** that `-Subject`, `CN=` included. `Name` plus
`Publisher` form the family the console identifies the game by, and its `LocalState` — where the
game data and your saves live — hangs off it. Pick it once.

⚠ Visual Studio may also offer to create a `*_TemporaryKey.pfx` beside the project. That file is a
**private key**: do not commit it anywhere. This repository's `.gitignore` blocks it by name.

## 5. Install it, and put the game data in place

Install the `.msix` from the console's **Device Portal** (`https://<console ip>:11443`, user
`xbox`): **Add** → the package → and the `Microsoft.VCLibs.140.00` x64 appx as a dependency. The
console needs **a user signed in**.

Then the data: this port reads the ROM itself, copied into the app folder as `sm.smc` -- this project reads the ROM at run time instead of extracting an asset blob. Upload it to the app's `LocalState` through the Device
Portal's file browser.

⚠ Two things that cost an afternoon each:

- The app's data folder **does not exist until the app has run once**. Launch it, let it fail to
  find the data, close it, and then upload.
- **Upload files one by one, never as a `.zip`.** Unpacked by the portal they get permissions the
  AppContainer cannot open, and the app behaves as if they were not there.

## 6. When something goes wrong

| What you see | What it is |
|---|---|
| MSBuild cannot find the UWP targets | The C++ UWP workload is not installed (section 0) |
| Link errors about duplicate or missing CRT symbols | The library order in the `.vcxproj` got lost: `vccorlib.lib` and `msvcrt.lib` first, and in `IgnoreSpecificDefaultLibraries` |
| SDL symbols missing at link time | SDL2 is not vendored, or its project was not retargeted to v143 (section 2) |
| The console installs the package and then does nothing | Usually no user signed in on the console |
| The game starts and complains about missing data | The data is not in `LocalState` yet, or it was uploaded inside a zip (section 5) |
| The console rejects the package | `Publisher` and the certificate subject are not the same string (section 4) |
