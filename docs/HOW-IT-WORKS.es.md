# Cómo funciona

*(English: [HOW-IT-WORKS.md](HOW-IT-WORKS.md))*

## Qué cambia una versión UWP y qué no

El juego en sí no se toca: la decompilación sigue haciendo lo que hace, y cada línea que añade esta
receta va bajo `#ifdef SM_UWP`. Lo que cambia es todo lo de alrededor, porque una app empaquetada
en una consola vive con unas reglas que una compilación de escritorio nunca se encuentra:

- **No arranca por `main()`.** El proceso empieza en `CoreApplication`. SDL2 trae el cascarón para
  eso (`SDL_winrt_main_NonXAML.cpp`), y el parche engancha ahí el arranque del juego.
- **No puede escribir junto a su ejecutable.** Un paquete instalado es de solo lectura, así que la
  carpeta de datos pasa al `LocalState` de la app. Por eso también hay que subir ahí los datos del
  juego a mano una vez (`docs/INSTALL.es.md` apartado 5).
- **Partes del host de escritorio simplemente no existen.** El mezclador de volumen del sistema es
  COM solo de escritorio: se compila fuera y manda el volumen de la consola.
- **El mando viene de otro sitio.** `uwpfunc.cpp` lo lee por `Windows.Gaming.Input`.

## SDL2 hay que compilarlo, no descargarlo

Este es el paso que pilla a todo el mundo. Los binarios de escritorio de SDL2 no se pueden usar
dentro de un AppContainer: importan bibliotecas que no están y les falta el backend de vídeo de
WinRT. Así que el 2.26.3 se vendoriza **en fuente** dentro de la copia y se compila con el
proyecto, retargeteado al toolset v143.

De SDL2 no se redistribuye nada en este repositorio salvo su propio punto de entrada de WinRT y dos
archivos de recursos, sin modificar y bajo su licencia zlib (ver [`../NOTICE.es.md`](../NOTICE.es.md)).

## El orden de enlazado que no es opcional

Un enlazado de WinRT necesita `vccorlib.lib` y `msvcrt.lib` **primero**, y los dos en
`IgnoreSpecificDefaultLibraries`. Si se equivoca, los errores hablan de símbolos del CRT duplicados
o ausentes, que suena a cadena de compilación corrupta. Ese orden va dentro de `sm_uwp.vcxproj`, que es
también por lo que esta receta publica un archivo de proyecto en vez de una lista de opciones que
marcar a mano.

## Cómo se verificó esto

No leyéndolo. Sobre un **clon nuevo de `snesrev/sm` en `578f90b`**, el 2026-10-14:

| Qué se midió | Resultado |
|---|---|
| El parche aplica a una copia limpia | Sí, limpio, comprobado con `git apply --check` antes de escribir |
| El árbol que produce la receta, contra el árbol del que salió el paquete instalado | **4 de 4 archivos parcheados idénticos, byte a byte**, y **5 de 5 archivos copiados idénticos** |
| Idempotencia | Una segunda corrida dice que todo está en su sitio y no escribe nada |
| `--revert` | Revierte el parche y quita los archivos copiados |

Lo que **no** se vuelve a medir aquí es la salida de MSBuild. El paquete de las consolas
(0.1.0.1, 4 740 639 bytes) se construyó con este mismo árbol; rehacerlo necesita el
árbol de SDL2 vendorizado, que este repositorio no puede llevar. Así que lo que se afirma es
preciso: la receta reproduce el árbol. El resto es el compilador de Visual Studio haciendo su
trabajo.

## Sobre el idioma

El código que añade esta receta lleva sus comentarios en inglés, como el proyecto en el que entra.
Esta documentación está en inglés y en español.
