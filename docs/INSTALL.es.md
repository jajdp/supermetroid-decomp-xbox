# Instalación — de una copia limpia al juego corriendo en la consola

*(English: [INSTALL.md](INSTALL.md))*

## 0. Dónde se escriben estas órdenes

- **PowerShell** (pulsa **Windows**, escribe `powershell`, **Entrar**) para `apply_uwp.py`, el
  certificado y el Device Portal.
- **El «Developer Command Prompt for VS 2022»** (mismo menú, escribe `developer`) para `msbuild`.

**No hace falta «ejecutar como administrador»**, y usarlo rompería el apartado 4: el certificado se
crea en el almacén de quien ejecuta la orden.

## 1. Clonar el proyecto del juego

```powershell
git clone https://github.com/snesrev/sm.git C:\sm
cd C:\sm
git checkout 578f90b
```

Ese commit es contra el que se generó el parche. Uno posterior puede seguir valiendo:
`apply_uwp.py` lo comprueba y te lo dice antes de escribir nada.

## 2. Aplicar la receta y vendorizar SDL2

```powershell
python <este repo>\tools\apply_uwp.py C:\sm
```

Aplica el parche sobre 4 archivos y copia seis más. `--check` informa sin escribir,
`--revert` deshace las dos mitades y `--list` explica cada pieza.

Luego SDL2, que es el paso que todo el mundo subestima: **el SDL2 de escritorio no funciona dentro
de un AppContainer.** Necesitas el 2.26.3 **en fuente**, en `third_party\SDL2\` de tu copia, con
su proyecto de Visual Studio retargeteado al toolset v143 para que se compile junto al juego.
Descarga el código de la release 2.26.3 de SDL, descomprímelo ahí, abre su solución de UWP una vez
y deja que Visual Studio la retargetee.

## 3. Compilar, empaquetar y firmar

En el **Developer Command Prompt**:

```
msbuild src\sm_uwp.vcxproj /p:Configuration=Release /p:Platform=x64 ^
        /p:AppxBundle=Never /p:UapAppxPackageBuildMode=SideloadOnly
```

Aquí MSBuild hace las tres cosas —compila, empaqueta y firma—, que es por lo que la **carga de
trabajo de C++ para UWP** sí es un requisito real en este port y no lo era en los de snesrecomp.

Antes de eso, abre [`../package/Package.appxmanifest`](../package/Package.appxmanifest) y cambia
los dos valores `CHANGE-ME`; el apartado 4 explica qué hace cada uno. El manifiesto de la carpeta
del proyecto es el que lee MSBuild.

## 4. Un certificado para firmar

```powershell
New-SelfSignedCertificate -Type Custom -Subject "CN=<tu nombre>" -KeyUsage DigitalSignature `
  -FriendlyName "<tu nombre> UWP dev" -CertStoreLocation "Cert:\CurrentUser\My" `
  -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
```

El `Publisher` del manifiesto tiene que ser **exactamente** ese `-Subject`, con el `CN=`. El `Name`
y el `Publisher` forman la familia por la que la consola identifica el juego, y de ella cuelga su
`LocalState`, donde viven los datos del juego y tus partidas. Elígelo una vez.

⚠ Visual Studio puede ofrecerte crear un `*_TemporaryKey.pfx` junto al proyecto. Ese archivo es una
**clave privada**: no lo subas a ningún sitio. El `.gitignore` de este repositorio lo bloquea por
nombre.

## 5. Instalarlo y poner los datos del juego

Instala el `.msix` desde el **Device Portal** de la consola (`https://<ip de la
consola>:11443`, con el usuario y la contraseña de Dev Home): **Add** → el paquete → y el appx
de `Microsoft.VCLibs.140.00` para x64 como dependencia. La consola necesita **un usuario
conectado**.

Luego los datos: este port lee la propia ROM, copiada a la carpeta de la app como `sm.smc`: este proyecto lee la ROM en ejecución en vez de extraer un paquete de datos. Súbelo al `LocalState` de la app con el explorador de
archivos del Device Portal.

⚠ Dos cosas que cuestan una tarde cada una:

- La carpeta de datos de la app **no existe hasta que la app ha corrido una vez**. Láncala, deja
  que no encuentre los datos, ciérrala y entonces sube.
- **Sube los archivos de uno en uno, nunca en un `.zip`.** Extraídos por el portal quedan con
  permisos que el AppContainer no puede abrir, y la app se comporta como si no estuvieran.

## 6. Cuando algo sale mal

| Lo que ves | Qué es |
|---|---|
| MSBuild no encuentra los targets de UWP | No está instalada la carga de trabajo de C++ para UWP (apartado 0) |
| Errores de enlazado por símbolos del CRT duplicados o ausentes | Se perdió el orden de bibliotecas del `.vcxproj`: `vccorlib.lib` y `msvcrt.lib` primero, y en `IgnoreSpecificDefaultLibraries` |
| Faltan símbolos de SDL al enlazar | SDL2 no está vendorizado, o su proyecto no se retargeteó a v143 (apartado 2) |
| La consola instala el paquete y luego no pasa nada | Normalmente, que no hay usuario conectado en la consola |
| El juego arranca y se queja de que faltan datos | Los datos no están aún en `LocalState`, o se subieron dentro de un zip (apartado 5) |
| La consola rechaza el paquete | El `Publisher` y el sujeto del certificado no son la misma cadena (apartado 4) |
