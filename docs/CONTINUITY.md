# Continuidad · ORVEX 0.3

Rama feature/orvex-0.3, basada en 9a0d7cc del PR #4. Estado y límites vigentes: ORVEX_0.3.md. El último commit de esta rama en GitHub es el checkpoint verificable. No fusionar main.

54 pruebas Python/Qt aprobadas. Ejecutar requirements-dev.txt, unittest discover -s tests -v con PYTHONPATH=src y QT_QPA_PLATFORM=offscreen; Ruff check/format gradual. Capturas deben exportarse fuera del checkout con ORVEX_CAPTURE_DIR.

Siguiente acción: probar administrador QML/Windows (selección y edición, eliminación con/sin historial), actualizar HTML a 0.3, completar exportación de diagnóstico y conectar proveedor de metadatos con credenciales autorizadas. Después, detectar/configurar PPSSPP o Dolphin y ejecutar un recurso de prueba autorizado. No descargar ROM/BIOS ni afirmar funcionamiento sin ejecución real. Conservar logo y experiencia de consola.

## Checkpoint Dolphin

Implementación del adaptador, índice por ROM, carpeta configurable, escaneo manual/periódico y lanzamiento mediante supervisor común. Ver DOLPHIN.md y validation/dolphin-tests.txt. 56 pruebas Python/Qt. Aún NO validado Dolphin real: siguiente acción prioritaria ejecutar el procedimiento Windows con juego propio/autorizado y registrar versión/resultados. Pulir selector de ejecutable/detección en UI, edición de referencias de emulador y escaneo asíncrono después. No confundir fixtures unitarias con emulación real.

## 0.3.1 PCSX2

Rama feature/orvex-0.3.1; detalle vigente PCSx2: docs/PCSX2.md. Adaptador/indexador/registro común y comandos PCSX2 preparados; 58 tests Python/Qt. Próxima acción: probar PCSX2 Qt y regresión Dolphin en Windows. No afirmar PCSX2 funcionando hasta ejecución real. Completar escaneo asíncrono y aplicación segura de perfil por juego; la asociación actual solo guarda referencia sin tocar perfiles.

## 0.3.2 — Issue #8

Rama feature/orvex-0.3.2 basada en e138f8414be2d887f516d25828d02c2303e6c836 (PR #7). Rediseño nativo con fondo visible, degradados, carátulas 2:3 sin recorte, selección ampliada, versión corregida y lanzamiento real conservado. Ver docs/ORVEX_0.3.2.md y validation/0.3.2 para pruebas/capturas. La identidad final requiere revisión del usuario. Próxima acción: validación Windows con biblioteca del usuario y sus fondos; luego proveedor remoto autorizado y navegación física con mando. No fusionar automáticamente. El commit de este checkpoint se identifica por `feat: cinematic native library for ORVEX 0.3.2` en GitHub.

## 0.3.3 — Issue #10

Base GitHub aad301462374ebb72188ae7150d6948ff4afa5af (feature/orvex-0.3.2 / PR #9). Rama feature/orvex-0.3.3. Carrusel único completo, reciente real descendente, hero sin botones redundantes/sesiones/rótulo, iconos sin marcos con foco, búsqueda contextual modal con teclado virtual. Entrada separada en orvex.controls: XInput/WinMM Windows, joydev Linux, Select/Back remoto. No se toca contenido ni esquema; sesiones y diagnóstico conservados. Ver docs/ORVEX_0.3.3.md y validation/0.3.3. Identificar el commit por `feat: minimal console navigation and controller search for ORVEX 0.3.3`. Siguiente acción: validar sin teclado/ratón en Windows con DualSense y biblioteca del usuario, registrar capturas/resultados y resolver mapas de hardware si es necesario. No fusionar ni declarar aceptación física automáticamente.

## 0.4 — Controller Manager, Issue #12 (avance parcial)

Base remota 48d83a7d3ee374a7a5577d8714bc9b85783abea1 / feature/orvex-0.3.3 / PR #11; rama feature/orvex-0.4-controller-manager. Lectura de issues #6, #8, #10 y #12 y PR #7/#9/#11. Se corrigió la edición de nombre de ROM indexada y se simplificaron argumentos de importación. Implementados inventario SDL/XInput, copia de INI a caché personal, identidad conservadora y selección por juego/versión, plataforma/motor y jugador. Aplicación temporal Dolphin opt-in limitada a configuración completa sin SDL variable, con copia/journal/restauración y detección de conflicto. Sin perfil real de Joy-Con, sin validación física ni Windows: no afirmar solución universal. Próxima acción: obtener copia del INI Joy-Con que Pablo probó, validar identidad física y mecanismo correcto de Dolphin sin índice volátil; verificar ACL/uso externo y restauración real. Ver docs/ORVEX_0.4_CONTROLLER_MANAGER.md y validation/0.4. No fusionar ni cerrar el issue. Commit identificable por `feat: controller profile inventory and guarded recovery`.

## Ciclo CI y estabilización 0.4

Base ae0f70fd96f642278dfe1be2b74ce66d4337850e conserva los dos commits CI indicados por el usuario. Se corrigió YAML inválido por runner.temp en env de job; Actions ahora ejecuta runners reales. Commits verificables: 89522a7 (workflow), 335783c (Qt Basic/LF/handles SQLite/propiedad de journal), 762ca03 (fixture C nativa Windows MSVC), de79f42 (rutas canónicas y reconexión), af0ea3b (fuentes Windows offscreen). Run 40810250925: Linux y Windows SUCCESS, 83 Python/Qt + 9 JS cada uno, cero skips. Artefacto Windows inspeccionado visualmente y capturas legibles guardadas en validation/0.4-ci. La corrección posterior de aislamiento infantil del diagnóstico tiene test que falló antes y pasó después. Ver CI_AND_RECOVERY_0.4.md para pruebas y límites. Siguiente prioridad: escaneo no bloqueante y aplicación Dolphin del perfil real con identidad verificable; no inventar el INI de Joy-Con ni activar configuraciones sin validación. No fusionar PR #13 ni modificar main. Este ciclo no requiere que Pablo ejecute pruebas manuales para demostrar la CI; hardware físico y emuladores comerciales permanecen fuera de la evidencia automática.

CI final f82822d detectó carrera temporal en test_real_ui (el proceso de 250 ms podía finalizar antes de comprobar ventana ocupada). Se añadió handshake de archivo solo a fixture de prueba, con límite de espera y liberación en teardown; no se amplían esperas del producto. Repetir ambos runners antes de declarar verde el último commit.

## Ciclo Configuración / menú de juego (#14)

Base remota 03558a6; cambios en la rama actual y PR #13, sin merge/main. Se reprodujo y corrigió el delegado vacío de DarkCombo y se añadieron navegación de seis categorías, campos/teclado virtual, selector acotado, explorador de archivos Qt y menú rápido con tres acciones. Controlador independiente con cierre Win32 WM_CLOSE por PID, sesiones/restauración a la finalización real y degradación sin pausa segura. SDL GUIDE cuando disponible, atajo aprendido persistente y neutral tras desconexión; no hooks HID globales ni índices HOME inventados. Solo se lee el INI aprobado para pausa por foco; no se modifica configuración funcional. Ver SETTINGS_AND_QUICK_MENU.md, capturas/resultados en validation/0.4-settings-menu. La integración física sobre Dolphin/PCSX2/fullscreen/Steam Input y la pausa efectiva aún requieren evidencia, no cerrar #14 como universal. Último commit de este ciclo identificable por `feat: controller settings navigation and guarded in-game menu`. Próxima acción tras CI: validar superposición/foco y pausa nativa con configuraciones existentes en Windows; mantener los perfiles volátiles bloqueados.

Corrección posterior: diálogo del gestor quedaba abierto tras salida del juego desde Configuración. Commit identificable por `fix: close settings dialogs on session return`; 11 pruebas específicas OK, incluida regresión nueva. Concurrencia CI incluye SHA del head para que una cancelación antigua del runner Windows sin pasos no bloquee el nuevo commit. Ver Checks del PR para resultado real del head; no inferir éxito del workflow.

Run 40816638345: Linux 94+9 OK, Windows 93/94 correctos y error compilando fixture GUI. Ajuste posterior identificable por `fix: activate history choice from controller and link Win32 fixture`; 12 pruebas locales focalizadas OK. No dar por validado Windows hasta revisar el nuevo head. Se preserva error anterior en validation/0.4-settings-menu; no se omite la prueba Win32.
