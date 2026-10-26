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
