> Entrega posterior: [REAL_LAUNCH.md](REAL_LAUNCH.md) describe biblioteca y ejecución nativa, pruebas vigentes y rama nueva. Este documento conserva el historial de la etapa visual.

# ORVEX 0.2 · Navegación de consola para revisión

## Decisiones e implementación

Se elimina Inicio de la UI y el arranque va a Videojuegos. La cabecera contiene solo Videojuegos/Multimedia y dos iconos SVG propios: perfil y engranaje. El menú de perfil permite elegir Adulto/Infantil; mantiene la advertencia demo sin PIN. Configuración sigue con sus seis categorías y preferencias SQLite existentes.

Videojuegos muestra un carrusel horizontal de sesiones demo recientes, fondo con precarga y fundido, título/sinopsis, porcentaje opcional, barra, horas y última sesión. Continuar jugando · DEMO abre la ficha; Jugar · DEMO mantiene el aviso sin lanzar contenido. La biblioteca completa está más abajo dentro de la misma pantalla y reutiliza búsqueda, filtros, favoritos y fichas. Las flechas/Tab/Enter y mouse permiten recorrer ambos niveles.

Multimedia utiliza la misma jerarquía con selección de películas/series, sin inventar progreso ni historial de reproducción. Su acción abre la ficha demostrativa. Los filtros no alteran el carrusel: su contexto y selección de biblioteca se conservan al regresar de la ficha.

Se mantienen fondos dinámico/fijo/predeterminado, movimiento reducido, logo provisional y política infantil hasta 7+. Los datos de progreso siguen en fixtures separados y el contrato de proveedor admite porcentaje ausente. Todo el catálogo se identifica como demo y no instalado. Imágenes reales: investigación y decisión en ARTWORK_PROVIDERS.md; no hay arte oficial de terceros dentro del repositorio.

## Ejecutar la entrega

Windows sin instalar: descargar `preview/ORVEX-0.2.html` (Download raw file), abrir en Edge/Chrome, F11 opcional. No requiere red ni archivos adicionales. El guardado depende de las políticas de localStorage para file:// y de conservar la ruta. Aplicación PySide6: instrucciones Windows/Linux del README conservadas.

Revisión sugerida: enfocar Órbita para ver fondo y porcentaje desconocido; abrir y volver; bajar con Biblioteca completa; buscar y filtrar; abrir ficha y comprobar retorno; cambiar a Multimedia; abrir perfil y elegir Infantil; abrir engranaje e Interfaz para probar modos de fondo y movimiento reducido.

## Validación realmente ejecutada

- 30 tests Python/Qt: consultas, perfiles, favoritos, SQLite/migración, fondos/progreso, carga de recursos aprobados y rechazo de rutas inválidas, arranque, rutas por teclado, mouse, menú de perfil, fichas y retorno.
- 7 tests Node del modelo: búsqueda, filtros, favoritos por perfil, estado, almacenamiento, progreso opcional y fondos persistentes.
- 12 recorridos en Chromium 122 de QtWebEngine 6.8.3/Linux con Playwright CDP: dos pestañas, navegación, recientes, detalle, demo, filtros, favoritos, persistencia, infantil, configuración, retorno/scroll y menú por teclado; sin excepciones JS ni solicitudes HTTP externas.
- Capturas reales Qt y HTML a 1920×1080 y 3840×2160. Logo mantiene proporciones. Composición revisada visualmente, textos y acciones sin solapamientos en las pantallas capturadas.

Total: 49 comprobaciones aprobadas. Logs `docs/validation/navigation-{qt,js,browser}.txt`. Evidencia WebP en preview/v0.2, regenerable con tests (PNG local) y Pillow para conversión lossless.

Pruebas pendientes: Windows físico/Edge/Chrome nativos, TV real, DPI/GPU y medición de fluidez en hardware objetivo, mandos físicos. No se certifica rendimiento de consola desde el renderizado software. Sin integración de proveedores, juegos instalados, streaming, reproducción ni autenticación parental. La identidad y composición quedan pendientes de revisión visual del usuario.

## Compatibilidad

Se conserva PySide6 6.8.3/Qt 6/QML/SQLite sin dependencias nuevas. Se reutilizan LibraryPage, DetailPage, SettingsPage, MediaCard y DynamicBackground. Solo cambia la organización de navegación; las pruebas de rutas se actualizan al nuevo contrato aprobado de dos pestañas. Los resultados de entregas anteriores quedan como historial, no describen esta cabecera.
