# ORVEX OS 0.2 — resultados de pruebas

Estado: implementación preparada para revisión, sin merge automático. Fecha de entrega: 24 de octubre de 2026 (America/Santiago).

## Ejecutado realmente

| Suite | Resultado | Evidencia |
|---|---|---|
| Python / Qt / SQLite | 22 pruebas aprobadas | `validation/qt-0.2.txt` |
| Modelo JavaScript | 6 pruebas aprobadas | `validation/js-model-0.2.txt` |
| HTML en motor Chromium real | 10 recorridos aprobados | `validation/browser-0.2.txt` |
| Sintaxis | Python compileall y Node --check aprobados | Comandos indicados en README |

**38 comprobaciones automáticas aprobadas** en estas tres suites. Los recorridos de navegador contienen múltiples aserciones y no se equiparan a 38 escenarios independientes de extremo a extremo.

Python: 3.12.14. Qt/PySide6: 6.8.3. Plataforma Qt offscreen y backend software, Linux x86_64. Node: 24.22.1. Playwright de desarrollo: 1.62.1. Navegador probado: QtWebEngine 6.8.3 / Chromium 122 bajo Linux, cargando el archivo local `file://`.

Se utilizaron dependencias de desarrollo del entorno y dos bibliotecas gráficas Linux extraídas a un directorio temporal para ejecutar el host de prueba. No se añadieron dependencias de producción ni se modificó el equipo del usuario. El host emite avisos sobre GPU/Vulkan/udev del entorno sin pantalla; no se usan para afirmar aceleración de hardware. Las pruebas Qt no registraron advertencias QML.

## Cobertura

- Cuatro rutas originales; teclado, mouse, búsqueda escrita, desplegable de plataformas y estado vacío.
- Apertura/cierre de fichas, avisos Jugar/Ver · DEMO y restauración del foco y de la carátula seleccionada.
- Filtros combinados y normalización de acentos/mayúsculas; tipos Serie/Película/Documental en multimedia.
- Alta/baja de favoritos, aislamiento por perfil y persistencia; migración de una base SQLite 0.1 con preferencias existentes.
- Cambio inmediato de perfil, cierre de fichas adultas, ausencia de títulos/portadas/resultados/opciones/recomendaciones inapropiados; rechazo de edad ausente o inválida.
- Seis categorías de ajustes, movimiento reducido y distinción de funciones futuras.
- Ocho SVG de marca válidos, icono, recursos de catálogo y logotipo sin deformación.
- HTML: navegación real, búsqueda, filtros, fichas, favoritos tras recarga, perfiles, ajustes y ausencia de excepciones JavaScript.
- **Cero solicitudes HTTP externas** durante los recorridos del archivo HTML. Datos, arte, scripts y estilos están incrustados.
- Renderizado Qt de siete estados y HTML de seis estados en 1920×1080 y 3840×2160. Se revisaron visualmente bibliotecas, fichas y perfil infantil. Se incluyen capturas representativas WebP sin pérdida en `preview/v0.2/`; las suites regeneran los PNG de todos los estados probados.

Una regresión detectada al actualizar favoritos reiniciaba el índice de GridView: quedó corregida manteniendo la selección en el bridge. Se comprueba el retorno al segundo título y la recuperación del foco después de cambiar favoritos.

## Reproducir

Las pruebas Python y del modelo JS se ejecutan con los comandos del README. Para el navegador se puede usar Playwright Chromium instalado en el equipo de desarrollo:

```sh
npm install
npx playwright install chromium
node tests/test_web_browser.cjs
```

Alternativamente, en un entorno Linux con PySide6 y sus bibliotecas QtWebEngine disponibles:

```sh
QT_QPA_PLATFORM=offscreen \
QTWEBENGINE_CHROMIUM_FLAGS='--no-sandbox --disable-gpu --disable-dev-shm-usage' \
ORVEX_WEBENGINE_PYTHON=.venv/bin/python \
node tests/test_web_browser.cjs
```

Este host se usa solo en el entorno aislado de pruebas; no es una opción de ejecución del producto. El script abre y cierra su propio proceso. La opción `--no-sandbox` fue necesaria para el host de desarrollo aislado; no se incorpora al launcher ni al HTML.

## Pendiente y límites

- Windows físico, Edge/Chrome de escritorio actuales y televisor real: pendientes. La prueba Chromium/Linux no se presenta como prueba Windows.
- Fuentes y DPI del equipo objetivo, GPU, tiempo de cuadro, latencia y consumo: pendientes; renderizar 4K no certifica rendimiento.
- El almacenamiento `file://` de navegadores puede variar según política/ruta/perfil. Se probó recarga en QtWebEngine y la degradación a memoria con almacenamiento bloqueado mediante el modelo JS.
- Navegación con mandos físicos, reproducción, emulación y Bluetooth no se implementaron ni probaron.
- Los perfiles no tienen autenticación ni PIN y no protegen el catálogo del acceso al código fuente.
- GitHub Actions está preparado para ejecución manual, pero no se ejecutó. Main y la privacidad se conservan; el PR requiere aprobación antes de fusionarse.
