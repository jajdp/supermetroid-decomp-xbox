# Super Metroid en la Xbox — el port UWP

Cómo coger la decompilación [snesrev/sm](https://github.com/snesrev/sm) de *Super Metroid* (Super
Nintendo, 1994) y hacerla correr **en una Xbox Series X en modo desarrollador**, como un paquete
UWP que compilas y firmas tú.

*(English: [README.md](README.md))*

No es una teoría: el paquete construido con esta receta lleva corriendo en dos Xbox Series X desde el
2026-09-05, y el que tienen hoy es el 0.1.0.1.

## En qué consola se probó

**En una Xbox Series X**, en modo desarrollador. Las dos consolas en las que se construyó y se probó esto
son Series X, así que es el único hardware al que se refiere cualquier cosa que se afirme aquí.

**En una Series S no se ha probado nunca, ni una vez.** Es otra máquina: menos memoria disponible para un
juego y una GPU más floja. Puede que funcione en una, puede que vaya más despacio, o puede que no
arranque; nada de aquí se ha medido en ella. Si lo ejecutas en una Series S, lo que obtengas no es lo que
dice este README, y ninguna de las cifras de aquí es una promesa sobre esa consola.

## Qué es este repositorio

**Una receta.** Nadie había publicado una versión UWP de este juego. Lo que hace falta es un parche
sobre 4 archivos de código —todo bajo `#ifdef SM_UWP`, así que tu compilación de
escritorio no se toca— más seis archivos que el proyecto no tiene: el punto de entrada de WinRT,
los ayudantes de UWP, los recursos de SDL2 para WinRT y el proyecto de Visual Studio que compila y
empaqueta el objetivo UWP.

`python tools/apply_uwp.py <tu copia>` hace las dos mitades, comprueba antes de escribir y se niega
a dejar una copia a medias.

## Qué **no** es

Aquí **no hay ROM, ni datos del juego, ni ejecutable, ni paquete `.msix`, ni arte**. Esto no puede
dar un juego jugable por sí solo, y nada de lo que te puedas descargar aquí es un juego. Necesitas
tu propio volcado legal del cartucho. Ver [`NOTICE.es.md`](NOTICE.es.md).

Los mosaicos del paquete tampoco están: los de la consola de verdad se hicieron con el arte del
propio juego, que es de Nintendo. En [`docs/ASSETS.es.md`](docs/ASSETS.es.md) están las medidas.



## Qué hace falta antes

| | |
|---|---|
| El proyecto del juego | [snesrev/sm](https://github.com/snesrev/sm) en el commit **`578f90b`**, que es contra el que se generó el parche |
| Tu propia ROM | `Super Metroid (Japan, USA) (En,Ja).sfc`, 3 145 728 bytes, SHA-256 `12b77c4bc9c1832cee8881244659065ee1d84c70c3d29e6eaf92e6798cc2ca72` |
| Visual Studio | 2022 con la **carga de trabajo de C++ para UWP** y el toolset v143. Al contrario que en los ports de snesrecomp, aquí MSBuild es quien compila, empaqueta y firma, así que esa carga de trabajo sí hace falta |
| SDL2 | **2.26.3, en fuente, vendorizado dentro de la copia** y retargeteado a v143. Los binarios de escritorio no sirven: UWP necesita el backend de WinRT compilado dentro |
| SDK de Windows | 10.0.26100 o similar, para `makeappx` y `signtool` si reempaquetas con tus mosaicos |
| Python 3 | Para `tools/apply_uwp.py` y para la extracción de datos del propio proyecto. Solo biblioteca estándar |
| Una Xbox en modo desarrollador | Y un certificado para firmar ([`docs/INSTALL.es.md`](docs/INSTALL.es.md) apartado 4) |

## Cómo va

```powershell
# 1. parchear e instalar los archivos nuevos en tu copia
python tools\apply_uwp.py <ruta-a-tu-copia>

# 2. vendorizar SDL2 2.26.3 en fuente dentro de third_party\SDL2 y retargetearlo a v143
#    (docs/INSTALL.es.md)

# 3. compilar, empaquetar y firmar con MSBuild
msbuild src\sm_uwp.vcxproj /p:Configuration=Release /p:Platform=x64 ^
        /p:AppxBundle=Never /p:UapAppxPackageBuildMode=SideloadOnly
```

Después se sube la propia ROM, copiada a la carpeta de la app como `sm.smc`: este proyecto lee la ROM en ejecución en vez de extraer un paquete de datos al `LocalState` de la app, y se instala el `.msix` por el Device Portal.
Paso a paso: **[`docs/INSTALL.es.md`](docs/INSTALL.es.md)**.

## Qué hubo que resolver

| | Síntoma | Arreglo |
|---|---|---|
| 1 | En UWP el proceso no arranca por `main()` | El punto de entrada de WinRT de SDL2 (`SDL_winrt_main_NonXAML.cpp`) más el arranque que trae el parche |
| 2 | El host de escritorio escribe junto al ejecutable, que una vez instalado es de solo lectura | La carpeta de datos pasa al `LocalState` de la app, que es el único sitio donde una app empaquetada puede escribir |
| 3 | El mezclador de volumen del sistema no compilaba | Es COM solo de escritorio. Se compila fuera bajo el define, y el port deja el volumen a la consola |
| 4 | No había mando | Se lee por `Windows.Gaming.Input` en `uwpfunc.cpp` |
| 5 | El SDL2 de escritorio no funciona dentro de un AppContainer | SDL2 2.26.3 se vendoriza y se compila para WinRT junto al proyecto |
| 6 | Un enlazado de UWP falla por símbolos del CRT duplicados o ausentes | `vccorlib.lib` y `msvcrt.lib` tienen que ir primero y estar en `IgnoreSpecificDefaultLibraries`; ese orden está en el `.vcxproj` |

El detalle está en **[`docs/HOW-IT-WORKS.es.md`](docs/HOW-IT-WORKS.es.md)**.

## Cómo se verificó

No leyéndolo. Sobre un **clon nuevo de `snesrev/sm` en `578f90b`**, el 2026-10-14:

| Qué se midió | Resultado |
|---|---|
| El parche aplica a una copia limpia | Sí, limpio, con `git apply --check` primero |
| El árbol que produce la receta, contra el árbol del que salió el paquete instalado | **4 de 4 archivos parcheados y 5 de 5 copiados idénticos, byte a byte** |
| Idempotencia | Una segunda corrida dice que todo está en su sitio y no escribe nada |
| `--revert` | Quita las dos mitades y deja la copia como estaba |

Lo que **no** se ha vuelto a medir aquí es el paso de MSBuild: el paquete que corre en las consolas
(0.1.0.1, 4 740 639 bytes) se construyó con este mismo árbol, y rehacerlo necesita el
árbol de SDL2 vendorizado, que no es algo que este repositorio pueda llevar dentro. Lo verificado
es la receta; el compilador es el de Visual Studio.

## Créditos y licencia

Port y herramientas de **Recompilaciones**, bajo la [licencia MIT](LICENSE).

De trabajo ajeno, este repositorio lleva: `uwpfunc.cpp` y `uwpfunc.h`, del **port UWP de zelda3**
(MIT), y tres archivos de SDL2 (**zlib**). Los dos están acreditados en
[`NOTICE.es.md`](NOTICE.es.md), que además mide exactamente cuánto se cita del proyecto del juego:
102 líneas de contexto en el parche, y nada más.

*Super Metroid* es © Nintendo. Este proyecto no está afiliado con ellos, ni con Microsoft, ni con los
autores de la decompilación, y no distribuye nada que les pertenezca. Los titulares de derechos
pueden escribir a **jajdpmail@gmail.com**.
