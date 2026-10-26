# Primera biblioteca y lanzamiento real

## Base de trabajo

La base aprobada es main `e8a2f164db76b757c57b9db15fc54685754c8ad0`. El PR #3 está abierto en `d5d0f88a85727c916bd75a8dd1e92d7ed1e54ce6`, sin fusionar. Esta nueva etapa se entrega en feature/orvex-real-launch con un commit descendiente directo de main, sin merge del PR #3. Se reaplican los componentes de navegación/fondos solicitados expresamente en esta etapa; no se presupone aprobación de aquella revisión visual. El logo se conserva.

## Implementado

- Dos secciones superiores, menú de perfil y ajustes por icono; carrusel horizontal con selección contextual, fondo precargado y transiciones, biblioteca completa al bajar. Reutiliza LibraryPage/DetailPage/SettingsPage y servicios existentes.
- Qt abre la biblioteca real vacía; demo es un origen distinto seleccionable. Importar registra nombre, plataforma y ejecutable canónico en SQLite; no inicia procesos. Previene duplicados por ruta.
- Lanzamiento directo QProcess sin shell ni argumentos. Primer lanzamiento requiere confirmar el archivo. SHA-256 revalidado, nueva confirmación si cambia; no es un análisis antimalware ni una frontera de seguridad frente a un atacante local que modifique archivos durante el lanzamiento.
- Seguimiento de started/finished/errorOccurred. Sesiones UTC con duración monotónica en milisegundos, código y estado; total y última sesión en interfaz. El cierre de la ventana se bloquea mientras se supervisa un proceso. QLockFile evita otra instancia del launcher sobre la misma biblioteca.
- Imágenes locales PNG/JPG/WebP: decodificación Qt, límites 20 MiB, 8192 px y 32 MP; copia PNG propia en caché personal. Vista previa y confirmación antes de asociar o reemplazar; cancelar elimina el archivo provisional. Predeterminados originales si faltan imágenes. No se importan SVG locales con posibles referencias externas.
- Búsqueda/filtros/favoritos también sobre títulos locales, con contexto separado del demo. Los importados carecen de clasificación verificada y se ocultan en Infantil. No se ofrece control parental seguro.
- El HTML conserva navegación visual y datos claramente demo; explicita que no puede importar o lanzar ejecutables. Las barras de avance se ocultan sin un porcentaje verificado, incluso en la presentación demo.

## Persistencia

Migración aditiva esquema 3, conservando settings/favorites y ubicación histórica. real_games guarda id local UUID, nombre, plataforma, ruta canónica, huella confirmada, rutas de cover/backdrop y fecha. play_sessions guarda inicio/fin UTC, duración, estado y exit_code. No se escribe en demo.json ni demo_progress.json. Las imágenes del usuario quedan junto a su base de datos, fuera del repositorio. Los registros de sesiones que estaban running al reiniciar pasan a interrupted con duración desconocida no acreditada; no se usa tiempo de pared para inventar juego.

Las preferencias del HTML permanecen en localStorage; no comparten SQLite ni un inventario real. No se exportan rutas personales ni fotos dentro del HTML.

## Alcance del lanzador

Se admiten .exe nativos Windows y ELF Linux ejecutables de hasta 512 MiB. No se añaden parámetros, permisos, scripts, asociaciones de archivos, URI Steam, Wine/Proton ni emuladores. La plataforma registrada es metadato del usuario, no una promesa de compatibilidad. Un archivo con cabecera válida puede fallar; QProcess informa el error y la biblioteca permanece. La confirmación se recuerda solo tras started. Se valida el ejecutable en cada solicitud; el hash de archivos grandes puede introducir una pausa de UI en esta primera implementación.

Se supervisa **un proceso directo**. No se puede deducir la vida de procesos hijos/delegados, juegos ya abiertos o launchers que se desconectan. El tiempo es duración del proceso, puede incluir menús/carga y no certifica juego activo. No hay porcentaje real de campaña, lectura de saves ni logros. Futuro ProgressProvider deberá declarar qué porcentaje puede verificar y su procedencia. Las sesiones fallidas tras started se registran con error y duración observada; failed-to-start no crea una sesión jugada. No se cierra ni finaliza a la fuerza un juego desde un botón de ORVEX. Un apagado forzado del host puede interrumpirlo y perder la duración pendiente.

## Validación ejecutada

61 comprobaciones aprobadas:

| Grupo | Cantidad | Entorno/evidencia |
|---|---:|---|
| Python/Qt | 41 | Linux, Python 3.12, PySide6 6.8.3, QML offscreen/software |
| Modelo JS | 7 | Node 24 |
| Recorridos navegador | 13 | Chromium 122 QtWebEngine 6.8.3/Linux, Playwright CDP |

Los 11 nuevos tests Python incluyen importación sin ejecución, reinicio de biblioteca, confirmación/cancelación, cambio de archivo, proceso real con ruta con espacios, duración/finalización/repetición, fallo de inicio, exit 7, duplicados/rutas inválidas/scripts rechazados, perfil/demo separados, exclusión de lanzamiento concurrente, imágenes confirmadas/canceladas/reemplazadas/persistentes e interrupción sin tiempo inventado. Dos recorridos Qt verifican el formulario y los botones de confirmación con mouse, estadísticas reales y bloqueo del cierre mientras está activo. El selector nativo FileDialog está implementado; los tests rellenan su ruta equivalente en el formulario, no certifican el diálogo del sistema operativo.

Fixture: tests/fixtures/controlled_app.c, código propio. Se compila mediante cc exclusivamente en TemporaryDirectory, escribe un marcador allí, espera 250 ms y finaliza con código configurable. Ningún juego comercial/ROM/BIOS/ejecutable precompilado se incluye. La importación deja el marcador ausente; solo la confirmación seguida de arranque lo crea.

Logs: docs/validation/real-launch-{qt,js,browser}.txt. Capturas reales en preview/real-launch (vacío, formulario, confirmación, sesión observada, imagen, ficha y 4K); HTML/demo actuales en preview/real-launch/web-*.webp; preview/v0.2 conserva capturas históricas. No hubo advertencias QML ni excepciones JS ni tráfico HTTP externo en las pruebas. Build HTML reproducible. Las cifras anteriores en otros documentos son historial.

Pendiente: ejecución Windows física (.exe), Edge/Chrome Windows, selector nativo Windows, SmartScreen/UAC, rutas con políticas empresariales, GPU/DPI/TV físicos, rendimiento, mandos, juegos comerciales y aplicaciones que requieren servicios/argumentos/Steam/DRM. No se certifica que cualquier juego funcione. Sin gastos, workflows ni servicios de pago.

## Recursos y proveedores

Sin imágenes oficiales de terceros dentro del repositorio. Se conserva artwork.json/resolve_art y el contrato MetadataProvider; LocalArtwork gestiona exclusivamente imágenes elegidas y confirmadas por el usuario. No hay búsqueda remota ni aplicación automática de coincidencias. La autorización para usar imágenes personales recae en su selección/confirmación; no se publica su caché. Las coincidencias futuras tendrán que ser propuestas, revisadas y confirmadas antes de reemplazar metadatos/arte. Ver ARTWORK_PROVIDERS.md.

## Pendientes de producto

Inventario automático, editar/eliminar referencias, argumentos y adaptadores de plataformas, seguimiento de procesos delegados, clasificación verificable/PIN, progreso de campaña verificable, métricas en vivo, caché remota y recuperación de duración tras un cierre forzado. Esta entrega es el primer lanzador nativo manual, no el sistema operativo completo.
