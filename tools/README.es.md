# tools/

*(English: [README.md](README.md))*

Un solo script, porque este port lo empaqueta MSBuild y no nosotros.

`apply_uwp.py` aplica la receta a **tu** copia: el parche sobre 4 archivos de código y
seis archivos que el proyecto no tiene. Las dos mitades o ninguna: una copia a medio aplicar es el
estado del que de verdad hay que protegerse.

```powershell
python tools\apply_uwp.py <tu copia>          # hacerlo
python tools\apply_uwp.py <tu copia> --check  # informar sin escribir
python tools\apply_uwp.py <tu copia> --revert # deshacer las dos mitades
python tools\apply_uwp.py --list              # para qué es cada pieza
```

Es Python 3 pelado, solo biblioteca estándar, y recibe la copia como argumento: aquí no hay ningún
valor por defecto que apunte a la máquina de nadie.

**Qué comprueba antes de escribir nada:** que el parche sea un parche de verdad (un `.patch` que ha
pasado por una tubería de shell puede llegar sin saltos de línea, y entonces `git apply` falla de
una forma que parece culpa de *tu* copia); que la copia sea un árbol de git, para poder comprobar
el parche en vez de intentarlo; y si cada archivo copiado ya está y es idéntico.

Aquí no hay `package_uwp.py` a propósito. En esta familia MSBuild compila, empaqueta y firma en un
solo paso, así que un script de empaquetado nuestro solo estorbaría. Los ports de snesrecomp
(`dkc1-xbox` y compañía) sí lo llevan, porque allí el empaquetado es `makeappx` a mano.
