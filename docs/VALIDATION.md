# Resultados de validación · 0.1

Fecha de entrega: 24 de octubre de 2026 (America/Santiago).

Entorno: Linux x86_64; Python 3.12.14; PySide6/Qt 6.8.3; Qt platform offscreen; Qt Quick backend software.

## Aplicación principal

8 pruebas unittest: PASS (ejecución real, no simulación del QML).

- Integridad del catálogo de seis títulos y existencia de sus portadas.
- Persistencia SQLite tras reinicio de conexión.
- Actualización de claves y parámetros SQL con contenido especial.
- Navegación por las cuatro rutas, retorno y recorrido circular.
- Selección de contenido, aviso modal, bloqueo de navegación detrás del aviso y cierre.
- Cambio de preferencia desde teclado a través del bridge y SQLite.
- Navegación y selección con eventos reales de mouse en la ventana Qt.
- Renderizado de las cuatro pantallas en 1080p y 4K, sin advertencias QML.

Se revisaron visualmente las capturas nativas. Ver `preview/`.

## Límites

No son pruebas en TV ni certificación de rendimiento. No se probó GPU, Windows físico, audio, emuladores, DRM ni Bluetooth. El pipeline GitHub está preparado; el resultado local no certifica una ejecución en GitHub.

## Vista HTML

JavaScript comprobado sintácticamente con Node. No se ejecutó validación DOM ni renderizado en navegador: Chromium no estaba disponible y su descarga falló. Tampoco se utilizó QtWebEngine: falta una biblioteca del host. Estas limitaciones no afectan las ocho pruebas de la aplicación QML.
