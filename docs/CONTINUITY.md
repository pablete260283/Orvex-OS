# Continuidad · ORVEX 0.3

Rama feature/orvex-0.3, basada en 9a0d7cc del PR #4. Estado y límites vigentes: ORVEX_0.3.md. El último commit de esta rama en GitHub es el checkpoint verificable. No fusionar main.

54 pruebas Python/Qt aprobadas. Ejecutar requirements-dev.txt, unittest discover -s tests -v con PYTHONPATH=src y QT_QPA_PLATFORM=offscreen; Ruff check/format gradual. Capturas deben exportarse fuera del checkout con ORVEX_CAPTURE_DIR.

Siguiente acción: probar administrador QML/Windows (selección y edición, eliminación con/sin historial), actualizar HTML a 0.3, completar exportación de diagnóstico y conectar proveedor de metadatos con credenciales autorizadas. Después, detectar/configurar PPSSPP o Dolphin y ejecutar un recurso de prueba autorizado. No descargar ROM/BIOS ni afirmar funcionamiento sin ejecución real. Conservar logo y experiencia de consola.
