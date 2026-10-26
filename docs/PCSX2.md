# ORVEX 0.3.1 · PCSX2 y consolidación Dolphin

Rama feature/orvex-0.3.1 sobre a34dbce4b06186b4d3d33137b0613012daa229c1 (PR #5). Issue #6 leído. No se fusionó main ni PR anteriores.

Implementado: PCSX2Adapter separado sobre indexador común, registro de adaptadores extensible, configuración del ejecutable/carpeta y escaneo PS2. Ruta raíz existente configurable; usa PS2, Wii y GameCube según adaptador. Formatos iniciales PS2: ISO/BIN/CHD/CSO/GZ. No se interpreta CUE ni se garantiza validez del disco por extensión. Deduplicación por ruta y persistencia SQLite, sin mover/copiar juegos. Se reutilizan confirmación, hash, QProcess y sesiones. Comando PCSX2 Qt: -fullscreen -batch -- ruta-absoluta, argumentos separados sin shell. Versiones antiguas/plugin no se certifican.

Gestor en Configuración → Biblioteca → Emuladores/carpetas: seleccionar dolphin o pcsx2, introducir ruta y raíz, guardar, escanear. Backend expone estado de configuración. El gestor utiliza un popup oscuro con mensaje claro. Dolphin conserva su comando y tabla anteriores. Resultado de escaneo: encontrados/nuevos/existentes/errores. Un error de archivo se cuenta sin detener todo el lote. Pendiente progreso por archivo, contador de ignorados y trabajo asíncrono: el escaneo todavía es síncrono y puede bloquear temporalmente. No considerar cerrado el criterio sin bloqueo del issue #6.

Perfiles: se puede asociar una ruta INI existente al juego seleccionado; persistencia en preferencias por ID. No se modifica el archivo. La asociación es una referencia administrativa; activación automática/perfiles por lanzamiento todavía pendiente, indicada explícitamente en UI. Los mandos siguen siendo los ya configurados en cada emulador. No se crea ni sobrescribe un perfil Wii horizontal/Nunchuk/motion ni se interpreta automáticamente qué requiere cada juego.

## Instalación y prueba Windows

1. Descargar la rama completa; ejecutar setup-windows.cmd si corresponde y run-windows.cmd.
2. Instalar/extraer PCSX2 oficial desde https://pcsx2.net/downloads/ . ORVEX no descarga ni instala automáticamente.
3. Completar el asistente de PCSX2, seleccionar BIOS obtenida de tu propia consola y verificar un juego propio allí primero. No se incluyen ni descargan BIOS/juegos.
4. Configurar DualSense por USB en Settings/Controllers de PCSX2, activar SDL y revisar mapeo. Probar primero sin duplicar Steam Input/DS4Windows; añadir Steam Input solo si se necesita, evitando doble entrada. Giroscopio/acelerómetro/touchpad no se certifican por asociación de un INI.
5. Colocar el archivo de juego en la subcarpeta PS2 de la raíz elegida. En ORVEX configurar pcsx2 con ruta de pcsx2-qt.exe (también nombres pcsx2, pcsx2-qtx64, pcsx2-avx2, pcsx2-sse4), guardar y escanear.
6. Volver a Videojuegos; Jugar, confirmar primera ejecución, comprobar arranque directo y cerrar normalmente. Revisar duración/persistencia al reiniciar. Si falta BIOS/configuración, completar en PCSX2; ORVEX solo puede mostrar el fallo del proceso, no diagnosticar automáticamente todos los avisos internos del emulador.
7. Repetir con Dolphin y los tres juegos ya validados; comprobar que los mandos/perfiles existentes no cambian. Registrar versión y resultados antes de aceptar 0.3.1.

## Evidencia y límites

Issue #6 registra validación manual comunicada por Pablo: Mario Kart Wii, Mario Strikers Charged y New Super Mario Bros Wii desde ORVEX/Dolphin; DualSense USB/SDL, inclinación en Mario Kart y touchpad como ratón mediante Steam Input con Steam abierto. No es una prueba automatizada ni certifica PCSX2.

58 tests Python/Qt en Linux aprobados. Los dos casos PCSX2 nuevos usan mock de validación del ejecutable y archivos de prueba: funcionan sin compilador Linux, pero NO ejecutan PCSX2. Comprueban ruta/comando, clasificación, deduplicación, contadores, persistencia y errores. El resto conserva pruebas de Dolphin y del lanzador con fixture C. PCSX2 real, Windows 0.3.1 y mando físico pendientes. No se han ejecutado Actions ni servicios de pago.

Fuentes oficiales consultadas: https://github.com/PCSX2/pcsx2-net-www/blob/main/docs/advanced/cli.md ; https://pcsx2.net/docs/configuration/controllers/ ; https://pcsx2.net/docs/setup/bios/ . CLI actual verificada documentalmente, no mediante una instalación real aquí.
