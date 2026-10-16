# Aviso

*(English: [NOTICE.md](NOTICE.md))*

## Sin afiliación

Este es un proyecto de aficionado, no oficial y sin ánimo de lucro. **No está afiliado,
patrocinado ni relacionado con Nintendo ni con Microsoft**, ni con los autores de
[snesrev/sm](https://github.com/snesrev/sm), del port UWP de zelda3, ni de
[SDL](https://github.com/libsdl-org/SDL). *Super Metroid*, *Xbox* y todos los nombres y marcas
relacionados son de sus respectivos propietarios.

Aquí no se vende nada y nada está monetizado.

## Qué NO se distribuye en este repositorio

Ninguna ROM. Ningún dato del juego —tampoco el paquete de datos que el proyecto extrae de tu
volcado—. Ningún ejecutable. Ningún paquete `.msix`. Ninguna partida. Ningún mosaico, que se
hicieron con el arte del propio juego. Ningún certificado de firma: ojo, que Visual Studio deja un
`*_TemporaryKey.pfx` junto a un proyecto UWP, y eso es una **clave privada**; el `.gitignore` lo
bloquea por nombre.

## Qué contiene de trabajo ajeno

| | Líneas | Qué es | Licencia |
|---|---|---|---|
| Líneas propias del parche | 165 | Lo que el parche añade a tu copia, bajo `#ifdef SM_UWP` | nuestras, MIT |
| Citado de snesrev/sm | 102 | Las **líneas de contexto** que lleva un diff unificado para saber dónde va cada cambio, más las 2 que quita | del propio proyecto, MIT (`LICENSE.txt`) |
| `uwpfunc.cpp`, `uwpfunc.h` | — | Los ayudantes de UWP, tomados del **port UWP de zelda3**, que es MIT y viene de la misma familia de motor | MIT |
| `SDL_winrt_main_NonXAML.cpp`, `SDL2-WinRTResources.rc`, `SDL2-WinRTResource_BlankCursor.cur` | — | El punto de entrada de WinRT y los recursos **de SDL2**, sin modificar | zlib |
| `sm_uwp.vcxproj` | — | El proyecto de Visual Studio, generado aquí a partir del de escritorio del proyecto | nuestro, MIT |

La ROM la pones tú y nunca pasa por aquí. Lo que la receta lleva sobre ella es un **hash SHA-256**:
una huella, no contenido.

## Retirada

Si tienes derechos sobre algo de lo anterior y quieres que se retire, escribe a
**jajdpmail@gmail.com** y se retira. Sin discusión y sin demora.
