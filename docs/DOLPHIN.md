# Dolphin · implementación preparada para validación real

Base: PR #5, rama feature/orvex-0.3. PR #3/#4 siguen siendo dependencias históricas sin fusionar. No se fusiona main.

Configuración → Biblioteca → Dolphin/carpetas permite guardar el ejecutable y la carpeta principal existente. Subcarpetas exactas Wii y GameCube. Ejemplo: D:\ORVEX\ROMs\Wii y D:\ORVEX\ROMs\GameCube. No hay ruta impuesta ni movimiento/copia de archivos. Escanear ahora indexa extensiones ISO/GCM/GCZ/RVZ/WIA/WBFS/CISO; la plataforma se infiere de la carpeta y el nombre del archivo, no son metadatos verificados. No se comprueba integridad de discos ni compatibilidad de cada juego. Revisión automática cada 10 segundos, solo en Adulto, sin proceso activo. Carpetas grandes pueden bloquear temporalmente la UI durante el escaneo síncrono.

DolphinAdapter.detect busca configuración, PATH y ubicaciones ProgramFiles/LOCALAPPDATA comunes. La UI permite introducir manualmente la ruta; selección de archivo y lista interactiva de detección pendientes. configure valida archivo nativo y nombre Dolphin.exe/dolphin-emu: es validación estructural, no certificación de identidad/versionado de la instalación. Nunca ejecuta durante detección/escaneo.

Indexación persistente en tabla dolphin_roms (creación aditiva, sin cambiar versión del esquema principal). Cada título conserva identidad propia aunque comparta ejecutable. real_games.executable utiliza un identificador interno para preservar su restricción UNIQUE histórica; el adaptador resuelve el ejecutable real antes de validar y confirmar. No editar manualmente ese identificador. Edición completa de referencias de emulador requiere pulido posterior. Una referencia retirada conserva su índice y no se reimporta automáticamente.

Lanzamiento: programa Dolphin, argumentos separados --batch --exec ruta-absoluta. Sin shell. Se vuelve a comprobar existencia de ROM y ejecutable al solicitar y confirmar. Primera ejecución exige confirmación; las siguientes permiten un clic mientras ejecutable/parámetros no cambien. Se reutilizan QProcess, estados y sesiones existentes; duración del proceso directo, sin inventar progreso de campaña. Infantil no muestra títulos sin edad verificada.

## Validación

56 pruebas Python/Qt aprobadas: suite anterior y dos casos de detección estructural, escaneo, clasificación por carpeta, comandos, duplicados, persistencia y errores. La prueba usa una fixture C propia renombrada para validar rutas y archivos con contenido simulado; NO ejecuta Dolphin ni discos reales. La fixture del lanzador existente sí verifica proceso/sesiones reales de prueba. Logs dolphin-tests.txt.

No hay Dolphin/ROM de prueba autorizada en el entorno. No se declara completada la integración real hasta validación compatible en Windows. No se descargaron emuladores, juegos, ROMs, BIOS ni firmware. No se alteran perfiles de mandos de Dolphin.

## Validar en Windows

1. Descargar la rama feature/orvex-0.3 completa. setup-windows.cmd y run-windows.cmd (Python 3.12/PySide6 6.8.3 ya utilizados por el usuario).
2. Instalar o extraer Dolphin desde https://dolphin-emu.org/download/ si falta. ORVEX no instala nada automáticamente; autorizar cualquier instalación del sistema por separado.
3. Abrir Dolphin una vez y verificar allí un juego propio/autorizado y sus controles. Cerrar Dolphin.
4. Copiar ese archivo a la subcarpeta Wii o GameCube dentro de la carpeta elegida.
5. Configuración → Biblioteca → Dolphin/carpetas: ruta absoluta de Dolphin.exe, carpeta principal; guardar y escanear.
6. Volver a Videojuegos: comprobar título/plataforma, pulsar Continuar/Jugar y revisar la confirmación. Debe abrir el juego directamente. Cerrar el juego; revisar tiempo y última sesión. Reabrir ORVEX y comprobar persistencia.
7. Copiar un segundo juego: esperar 10 segundos o escanear manualmente. Repetir escaneo no debe duplicar. Renombrar/mover ROM puede crear otra referencia; reconciliación de movimientos pendiente.
8. Registrar versión Dolphin/Windows, extensión, resultado de arranque, controles, duración y errores. Si falla, consultar Sistema/Diagnóstico. La ejecución de Bloc de notas/Bloody Roar II comunicada antes no certifica Dolphin.

## Controles y fuentes

Se utilizan los mandos que el usuario ya configuró en Dolphin, sin reescribir sus archivos. Xbox y DualSense requieren configuración como mandos/emulación apropiada en Dolphin; Wiimote real utiliza la opción y conectividad documentadas por Dolphin. No se implementa pareo automático ni se afirma compatibilidad física probada.

Fuentes oficiales consultadas: https://github.com/dolphin-emu/dolphin/blob/master/Readme.md (CLI --batch/--exec), https://dolphin-emu.org/docs/faq/ (formatos), https://en.dolphin-emu.org/docs/guides/configuring-controllers/ (mandos). Permisos de acceso, configuraciones, compatibilidad y requisitos de hardware deben verificarse en el PC.
