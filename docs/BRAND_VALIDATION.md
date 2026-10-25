# Validación de identidad ORVEX OS

Entorno real: Linux x86_64, Python 3.12.14, PySide6/Qt 6.8.3, offscreen y backend software.

## Ejecutado

- 11 pruebas unittest aprobadas (8 previas y 3 de identidad). Salida: `brand-test-output.txt`.
- Cuatro pantallas renderizadas en 1920×1080 y 3840×2160, sin advertencias QML; navegación por teclado y mouse y persistencia SQLite.
- En cada pantalla/resolución: SVG cargado, estado listo y relación de aspecto pintada 610:165; sin uso inesperado del fallback.
- Ocho SVG válidos con QSvgRenderer. Icono produce un pixmap 256×256 no vacío. Nombre y displayName ORVEX OS, ubicación de preferencias compatible con 0.1.
- Verificación byte a byte de los recursos copiados contra el kit adjunto; hashes guardados con los assets.
- HTML: logotipo, fallback y favicon incrustados; comprobación de bytes del logo/fallback contra originales y título correcto. Sintaxis JavaScript verificada con Node; compilación sintáctica de Python aprobada.
- Revisión visual de cabecera y cuatro pantallas 1080p y de la composición/cabecera 4K. No se observó recorte ni deformación. Las capturas WebP incluidas son conversiones sin pérdida de las capturas Qt. Los PNG 1080p/4K se regeneran con las pruebas.

## Pendiente

- Revisión y aprobación visual del usuario; no se aprueba automáticamente ni se integra en main.
- Ejecución física en Windows/televisor, DPI, tipografía instalada y apariencia del icono en la barra de tareas de Windows.
- Renderizado y navegación del HTML en Edge/Chrome reales. Este entorno no dispone de navegador ejecutable; QtWebEngine tampoco puede cargarse por bibliotecas del host ausentes. La comprobación estática no sustituye estas pruebas.
- Ejecución del workflow en GitHub; no se inicia para evitar consumo de minutos sin autorización.
