# corvosetup

Configuracion reproducible de CachyOS con Niri y Noctalia.

Este repositorio guarda configuraciones, codigo propio y scripts de instalacion. Clonarlo no cambia el sistema: los cambios solo se aplican al ejecutar explicitamente `bash install.sh`.

## Componentes

1. Paquetes base para CachyOS.
2. Limine, Snapper y procedimiento seguro de Secure Boot.
3. Logitech Light Manager para teclado G213 y audifonos G733.
4. Niri con teclado latinoamericano, perfil de monitores y GUI de pantallas en espanol.
5. Barra Noctalia, fuente Monocraft y widget de uso de Codex.
6. Skills globales para OpenCode.

## Uso

Revisar sin ejecutar cambios:

```bash
bash install.sh --dry-run
```

Aplicar todo:

```bash
bash install.sh
```

Aplicar un solo modulo:

```bash
bash install.sh --only logitech
bash install.sh --only niri
bash install.sh --only noctalia
bash install.sh --only skills
```

Modulos validos: `packages`, `limine`, `logitech`, `niri`, `noctalia` y `skills`.

El instalador pide confirmacion antes de ejecutar. Los archivos existentes se respaldan con una extension `.corvosetup.bak`.
Debe ejecutarse como usuario normal, nunca mediante `sudo`. Las versiones observadas en la maquina de origen estan en `packages/current-versions.txt`; son referencia de diagnostico porque CachyOS es rolling-release.

## Secure Boot

El instalador normal configura Limine, pero no crea ni enrola claves de Secure Boot. Esa operacion depende del firmware y se ejecuta por separado:

```bash
bash scripts/secure-boot.sh
```

Las claves privadas de `sbctl`, el `machine-id`, UUID de discos y archivos generados de `/boot` nunca se guardan en este repositorio. El instalador detecta la ESP, reutiliza la linea activa de `/proc/cmdline` y exige una configuracion Snapper llamada `root`; aborta antes de escribir si esas condiciones no se cumplen.

Antes de usar `scripts/secure-boot.sh`, el firmware debe estar en Setup Mode y debe existir un medio USB de recuperacion. El script prepara y firma Limine antes de enrolar las claves como ultimo paso irreversible.

## Configuracion de Logitech

El modulo `logitech` instala y habilita Logitech Light Manager para configurar
perifericos Logitech compatibles. Sus ajustes se guardan localmente y pueden
adaptarse a cada equipo sin versionar identificadores ni detalles del hardware.

## Recursos visuales

`scripts/05-noctalia.sh` descarga Monocraft 4.2.1 desde su proyecto oficial y verifica su SHA-256. Los fondos no se versionan porque son archivos grandes; se pueden colocar en `~/Pictures/corvosetup-wallpapers`. No se conservaron URLs verificables de las siete descargas originales, por lo que el instalador no descarga sustitutos arbitrarios.

## Verificacion

La comprobacion estatica, que no instala nada, se ejecuta con:

```bash
bash tests/static-checks.sh
```

Despues de una instalacion real puede usarse:

```bash
bash scripts/verify.sh
```
