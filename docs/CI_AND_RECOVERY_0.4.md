# ORVEX 0.4 — CI y recuperación por lanzamiento

Base remota auditada: ae0f70fd96f642278dfe1be2b74ce66d4337850e. Su padre es 3b06f2d5a2c7f04ba10c9a4f1691c16a51fefdc5; ambos cambios de CI ya estaban presentes. Este ciclo trabaja sobre PR #13, sin tocar main ni fusionar dependencias.

## Diagnóstico de Actions

Los runs 40807997102 y 40808098790 existían, pero su lista de jobs estaba vacía. La anotación pública de 40808098790 confirmó un workflow inválido: `runner.temp` en el entorno del job. GitHub aún no ha asignado un runner en ese contexto; la expresión debe usarse en el entorno de un paso. No era evidencia de tests ejecutados ni un fallo de permisos/billing. Referencia oficial: https://docs.github.com/en/actions/reference/workflows-and-actions/contexts .

Commit 89522a7d92b43b342a5eda0377de03b4960da324 movió el entorno al paso de pruebas. Desde entonces Actions crea jobs Linux y Windows reales. El filtro de pull_request ahora incluye feature/orvex-0.3.3, que es la base de PR #13; push sigue cubriendo feature/orvex-0.4-controller-manager. Concurrency comparte grupo entre push y PR de la misma rama para cancelar el duplicado. Se mantiene `contents: read`; las pruebas no necesitan escritura en el repositorio. No se cambió configuración de cuenta, visibilidad, facturación ni main.

## Fallos Windows detectados por ejecución real

Primer job: 123233386330, run 40808615997. Antes de corregir: 79 ejecuciones, 11 fallos, 4 errores y 31 skips por fixture Linux.

- Qt elegía un estilo nativo que no admite los backgrounds personalizados. ORVEX configura Basic antes de cargar QML, tanto en el entrypoint como al importar el paquete para las pruebas directas. No se silencian los warnings. Fuente Qt: https://doc.qt.io/qt-6.8/qquickstyle.html .
- El checkout convertía SVG a CRLF y cambiaba hashes y bytes embebidos. `.gitattributes` fija LF para recursos y código; PNG/WebP siguen siendo binarios. Los tests de integridad conservan sus hashes.
- Los tests de migraciones usaban `with sqlite3.connect(...)`, que confirma transacciones pero no cierra la conexión. Se añadió `closing()` además del contexto transaccional; esto libera handles para limpiar temporales en Windows. No se borran bases del usuario.

## Cobertura nativa Windows

La fixture C de ORVEX usa Sleep en Windows y usleep en Linux. Se compila dentro de un TemporaryDirectory, con MSVC ya instalado en windows-2022 o cc en Linux. El workflow obtiene el entorno MSVC con vswhere/vcvars64; no instala un compilador ni descarga juegos. En CI, `ORVEX_REQUIRE_NATIVE_FIXTURE=1` impide que una ausencia de compilador produzca skips silenciosos. Las copias y alias conservan la extensión .exe en Windows. Estas pruebas comprueban procesos reales controlados, sesiones y restauración; no son pruebas de emulación ni hardware físico. El primer intento nativo Windows encontró comparaciones textuales entre rutas cortas `RUNNER~1` y canónicas `runneradmin`, y una fixture ELF usada en Windows: se normalizó el retorno de la fixture con `resolve()` y el ejecutable inválido se genera como PE o ELF según sistema, sin omitir el caso de error.

## Inspección visual que amplía las comprobaciones

El run 40809675229 pasó 82 pruebas en ambos sistemas y 9 pruebas JS por job, sin skips nativos. Sin embargo, al descargar e inspeccionar sus capturas Windows se detectaron cuadros en lugar de glifos: el backend offscreen no encontraba las fuentes del sistema. No se presenta ese artefacto como validación visual correcta.

Se añadió ui_runtime.ensure_application_font: registra fuentes existentes de Windows mediante QFontDatabase antes de renderizar QML/SVG y comparte la inicialización con las pruebas. No instala, descarga ni redistribuye fuentes. Un test adicional comprueba glifos latinos/españoles mediante QFontMetrics; se repite la captura para inspección visual. Fuente: https://doc.qt.io/qt-6.8/qfontdatabase.html .

## Recuperación segura por propietario

Se detectó que el cierre de un lanzamiento nuevo podía ejecutar `recover(finished=True)` sobre un journal pendiente de otro proceso. Ahora cada aplicación temporal crea un `transaction_id`; solo su ControllerManager propietario puede marcar inicio/PID y finalizar esa transacción. Una sesión nativa posterior no cambia el journal anterior. Los journals anteriores sin ID siguen siendo recuperables al reiniciar con sus comprobaciones conservadoras; nunca se reclaman como propios.

El reintento manual tampoco ignora un PID conocido que sigue activo. Confirmar que Dolphin está cerrado permite resolver una fase `starting` sin PID, pero no fuerza escritura sobre un archivo cambiado o un proceso vivo. Si la escritura/lectura del journal falla al cerrar, el lanzador libera el proceso y deja un error recuperable en Diagnóstico en lugar de permanecer ocupado.

Las nuevas pruebas portables verifican journal ajeno, PID vivo, token incorrecto, intento manual y error SQLite. Se mantienen la copia previa, integridad del snapshot, comparación del archivo y protección de índices SDL variables. La aplicación temporal continúa desactivada por defecto y con el alcance limitado descrito en ORVEX_0.4_CONTROLLER_MANAGER.md. No se aplicó un perfil al Dolphin real del usuario.

## Entrada y reconexión

WindowsPad y LinuxJoystick generan un token de conexión exclusivamente para navegación. No se usa como identidad física persistente. Al abrir/cambiar/desconectar una fuente, el enrutador exige estado neutral antes de Confirmar. Un error de lectura cancela la repetición y también exige neutral al recuperarse; el diagnóstico de entrada llega a Configuración/Sistema. La prueba usa un lector simulado y el enrutador de producción. No acredita reconexión física de un DualSense, Joy-Con o Wiimote.

## Alcance pendiente

La prueba manual comunicada por Pablo con Joy-Con derecho, Dolphin y Wii Sports (Accel/Gyro SDL sin BetterJoy/DSU) se conserva como evidencia reportada. El INI real no está en el repositorio. La activación segura de perfiles Dolphin [Profile] con SDL variable, identidad USB/Bluetooth, PCSX2/ports y varios jugadores siguen pendientes; no se inventaron mapeos. El escaneo de ROMs aún es síncrono y la obtención remota de carátulas de #8 no se ha implementado en este ciclo.

Tras registrar las fuentes, el run [40810250925](https://github.com/pablete260283/Orvex-OS/actions/runs/40810250925) sobre af0ea3bf9613f812afad3a3cd49b282324e0c5d6 pasó **83 pruebas Python/Qt y 9 JS en cada sistema, sin skips**; Ruff y formato también pasaron. Se descargó el artefacto Windows 12869982826 y se inspeccionaron las capturas del gestor y del carrusel: texto español y logo legibles. Las imágenes reducidas incluidas en validation/0.4-ci son capturas Windows reales con aplicaciones y mando de prueba, no hardware.

Además, una prueba posterior encontró que el diagnóstico técnico podía exponer el nombre de un perfil personal al cambiar a Infantil. Se restringieron diagnóstico/mensajes de operación al adulto y se emitió la notificación al cambiar de perfil para actualizar QML inmediatamente. La prueba se conserva antes (fallo) y después (correcta). Los perfiles demo continúan sin autenticación/PIN; esto no es control parental seguro.

Resultados, commits y enlaces de las ejecuciones: docs/validation/0.4-ci. Las capturas de runners son de Qt offscreen y datos controlados, no de juegos del usuario. Las pruebas físicas siguen diferenciadas de las automáticas.

## Carrera detectada en la comprobación final

Run 40811017258 encontró una aserción temporal inestable en Linux: la fixture de 250 ms podía finalizar antes de verificar el bloqueo de cierre de ventana. Se reemplaza esa suposición por una señal explícita de liberación en la fixture C, con tiempo máximo y liberación en teardown. El producto no cambia y el proceso sigue siendo nativo real.
