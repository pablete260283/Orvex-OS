> Entrega posterior: [REAL_LAUNCH.md](REAL_LAUNCH.md) describe biblioteca y ejecución nativa, pruebas vigentes y rama nueva. Este documento conserva el historial de la etapa visual.

> Actualización posterior: la navegación de dos secciones y validación vigente se documentan en [CONSOLE_NAVIGATION_0.2.md](CONSOLE_NAVIGATION_0.2.md). El contenido siguiente conserva el registro de la entrega anterior.

# ORVEX 0.2 — Fondos y seguimiento demostrativo

Implementación para revisión; no fusionar sin aprobación. Mantiene las bibliotecas, perfiles, favoritos y ajustes de la entrega aprobada.

## Implementado en Qt y HTML

- Fondo dinámico según el título enfocado o señalado con el mouse, tanto videojuegos como multimedia; la ficha utiliza el fondo de su contenido.
- Dos capas de imagen precargada, fundido de 280 ms y degradados oscuros. Movimiento reducido elimina el fundido. Qt agrupa cambios rápidos con 100 ms de espera. Al cambiar de perfil se descarta la imagen anterior para no mostrar un fondo adulto en Infantil.
- Modos dinámico, fijo y predeterminado desde Configuración → Interfaz. El modo predeterminado vuelve al fondo grafito sin imagen. El modo fijo permite elegir un recurso del catálogo permitido al perfil; un fondo adulto guardado se sustituye por grafito en Infantil.
- Preferencias `background_mode` y `background_fixed` en SQLite, conservando el esquema/preferencias existentes. HTML guarda claves equivalentes en localStorage; no comparte la base Qt.
- Inicio: Continuar jugando, ordenado por última sesión; título destacado, porcentaje/barra, tiempo, última sesión y estado. Las tarjetas abren la ficha; el acceso Continuar · DEMO también abre la ficha y no lanza juegos.
- Fichas de juegos: progreso demostrativo completo. Estados No iniciado / En progreso / Completado. Un juego de ejemplo no tiene porcentaje; se muestra Sin porcentaje disponible y no se inventa un valor. Los contenidos multimedia no reciben progreso de videojuego.

## Separación de datos y arquitectura

`core/demo_progress.json` contiene exclusivamente fixtures, sin lecturas de partidas ni servicios. `core/progress.py` define ProgressProvider y DemoProgressProvider; el bridge permite inyectar otro proveedor en el futuro. Un registro puede carecer de porcentaje, tiempo o fecha. No se deduce avance desde horas jugadas, ni desde un número genérico de logros. Partidas, logros y plataformas necesitarán adaptadores validados por cada caso.

Los fixtures se comparten entre perfiles para demostrar la interfaz; no representan historial personal real. La disponibilidad de títulos sigue filtrada por perfil. Los datos reales futuros deberán identificar su fuente y no mezclarse silenciosamente con fixtures. En 0.2 no se escribe progreso real en SQLite.

El builder HTML incrusta los mismos fixtures y los SVG originales. Los fondos son ilustraciones geométricas originales de demostración del proyecto, sin imágenes ni carátulas de terceros. No se ha cambiado el logotipo provisional ni la licencia global del repositorio.

## Validación

- 27 pruebas Python/Qt: suites anteriores más recientes, foco destacado, modo fijo persistente, edad/privacidad del fondo, ausencia de porcentaje y ficha multimedia sin progreso de juego.
- 7 pruebas de modelo JavaScript: incluidas persistencia de fondos, recientes y porcentaje desconocido.
- 11 recorridos de navegador real QtWebEngine/Chromium Linux: incluyen foco/cambio de fondo, información de avance y preferencia fija tras recargar. El HTML sigue sin solicitudes HTTP externas ni excepciones JavaScript.
- Capturas nativas y HTML a 1080p/4K; resultados en `docs/validation/visual-*.txt`.
- Se conservan los límites de la validación previa: pendiente Windows/Edge/Chrome/TV físicos, DPI y medición de fluidez/tiempos de cuadro sobre hardware objetivo. Las pruebas verifican lógica y renderizado; no certifican ausencia de todos los parpadeos en cualquier dispositivo.
- No se ejecutaron workflows en GitHub ni servicios de pago.
