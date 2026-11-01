# Persistencia 0.5 y recuperación

## Migración aditiva 5 → 6

El Store conserva migraciones 1–5 y añade la 6 en una transacción. No recrea tablas históricas ni modifica ROMs, ejecutables, imágenes, INIs de emuladores o perfiles de mando. Activa claves foráneas, valida columnas requeridas y rechaza versiones futuras o bases dañadas sin reiniciarlas. Un fallo intermedio revierte el esquema y user_version.

Antes de migrar un archivo no vacío crea junto a él `preferences.sqlite3.pre-v5-<id>.bak` (la versión puede ser anterior a 5). Copiar con SQLite backup evita snapshots inconsistentes. Conservar estos respaldos; contienen información personal y las mismas rutas que la base original.

El esquema 6 añade perfiles persistentes, catálogo, extensión de juegos, propuestas y actividad; `play_sessions.profile_id` es nullable. Favoritos, preferencias, mandos, journals e historial anteriores se preservan. Las sesiones nuevas registran el perfil de inicio; las antiguas no se reasignan.

**La aplicación 0.4 sin cambios rechaza una base 6 por ser futura.** Compatibilidad significa preservación de datos y funcionamiento de los módulos anteriores en 0.5, no lectura retroactiva del esquema 6. Nunca bajar user_version a mano. Las pruebas ejecutan el Store auténtico del commit base para verificar tanto el rechazo de 6 como la lectura de una copia restaurada de 5.

## Probar sin tocar la biblioteca habitual

Descargar `feature/orvex-0.5-foundation` y extraer en una carpeta diferente. Python 3.12 de 64 bits y PySide6 6.8.3 siguen siendo la configuración Windows de referencia. No hay EXE autónomo ni distribución Linux.

PowerShell, desde la raíz:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH="src"
.\.venv\Scripts\python.exe -m orvex --data-dir "$env:LOCALAPPDATA\ORVEX-Foundation-Review"
```

Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PYTHONPATH=src .venv/bin/python -m orvex --data-dir /tmp/orvex-foundation-review
```

Esto crea una biblioteca vacía aislada. Para revisar datos existentes: cerrar ORVEX y los juegos; copiar **toda** su carpeta de datos a otro directorio; abrir ese destino con `--data-dir`. No ejecutar las dos instancias contra la misma base ni lanzar juegos durante una revisión de migración. No ejecutar sin `--data-dir` si se quiere evitar actualizar la base habitual.

## Recuperar a 0.4 sin destruir la base 0.5

1. Cerrar ORVEX y juegos. Conservar íntegra la carpeta 0.5, respaldo previo y archivos asociados. No borrar ni renombrar la única copia.
2. Crear una carpeta de recuperación distinta. Restaurar el respaldo pre-v5 a un archivo nuevo `preferences.sqlite3` usando `Store.restore_copy`, que valida integridad y se niega a sobrescribir destinos existentes.
3. Volver al código 0.4 validado y abrir esa nueva carpeta con una copia de sus recursos personales. 0.4 no tiene `--data-dir`; para uso operativo de su carpeta habitual, guardar primero toda la carpeta actual y colocar la copia restaurada con ORVEX cerrado. Este reemplazo manual no se automatiza.
4. El respaldo previo no contiene incorporaciones posteriores a la migración. La base 0.5 original se conserva para retomarlas; no hay conversión inversa ni fusión automática.

Ejemplo de recuperación técnica desde el entorno 0.5 (rutas de prueba a sustituir):

```python
from orvex.core.store import Store
Store.restore_copy("copia.pre-v5-id.bak", "carpeta-nueva/preferences.sqlite3")
```

`backup_to` también escribe solo archivos nuevos y exige que no haya transacción activa. Una copia SQLite puede variar bytes de cabecera: se verifica contenido lógico, integridad y versión, no igualdad binaria engañosa. Corrupción o un esquema que declara versión 6 sin sus columnas produce error legible, conservando el original.
