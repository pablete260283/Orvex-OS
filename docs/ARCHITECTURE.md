# Arquitectura ORVEX OS 0.2

Se mantiene Qt 6/QML, PySide6 6.8.3 y SQLite. No se añaden dependencias de producción. El kit ORVEX provisional permanece intacto.

| Módulo | Responsabilidad |
|---|---|
| `core/demo.json` | Único catálogo ficticio para Qt y generación HTML; datos separados de servicios |
| `core/library.py` | Filtrado de perfil, normalización, búsqueda, opciones y favoritos; sin Qt ni dispositivos |
| `core/store.py` | Preferencias existentes y favoritos SQLite por perfil |
| `core/bridge.py` | Adaptador QObject: rutas, contexto por biblioteca/perfil, detalle y señales |
| `ui/Main.qml` | Cabecera, utilidades, navegación y escalado 1920×1080 lógico |
| `ui/pages/LibraryPage.qml` | Búsqueda, filtros, estado vacío y cuadrícula reutilizada en ambas bibliotecas |
| `ui/pages/DetailPage.qml` | Ficha reutilizada, favoritos y acciones de demostración |
| `ui/pages/SettingsPage.qml` | Seis categorías, preferencias reales y marcadores futuros |
| `ui/components/` | Botones, menú y carátulas compartidas |
| `adapters/` | Contratos futuros: controles, emuladores y multimedia; no se instancian |
| `web/library.js` | Modelo de sesión equivalente para el HTML, con almacenamiento adaptable |
| `web/app.js`, `web/style.css` | Vista y navegación de la demostración web |
| `scripts/build_web_preview.py` | Incrusta datos, arte, logo, scripts y CSS en un HTML offline |

## Datos y migración

Se conserva `settings(key PRIMARY KEY, value JSON)` y la ruta Qt de datos de usuario de 0.1, cuyo componente histórico es `Entertainment Preview`. La aplicación expone ORVEX OS como nombre visible. Se añade `favorites(profile, item_id, PRIMARY KEY(profile,item_id))` y se marca `user_version=2`. No se borran preferencias ni se sobreescriben metadatos de medios.

Se guardan perfil activo, movimiento reducido y favoritos. Los filtros y la posición de navegación se mantienen durante la sesión, por biblioteca y perfil; no se promete persistencia de esos filtros entre reinicios. El HTML usa claves separadas `orvex-v2-profile` y `orvex-v2-favorites`; conserva `orvex-preview-motion` de la vista anterior.

## Navegación

El bridge expone acciones lógicas: navegar, seleccionar índice, abrir/cerrar ficha, cambiar perfil y modificar filtros/favoritos. La vista Qt resuelve foco, flechas y Tab; un futuro adaptador de mandos podrá invocar estas acciones sin añadir lógica de catálogo. La selección reside en el bridge y no se actualiza a partir de los reinicios automáticos del modelo GridView, para mantenerla al cambiar favoritos.

Las fichas no reconstruyen el contexto de la biblioteca. Al cerrar se recupera la carátula seleccionada. Cambiar perfil cierra cualquier ficha anterior y activa el contexto de ese perfil, sin arrastrar consultas adultas al infantil.

## Perfil infantil

La política de demostración admite únicamente edades enteras 0–7. General se representa con 0. La comprobación se aplica antes de construir resultados, recomendaciones, opciones de filtro y fichas. Edades ausentes, negativas, textuales o booleanas se ocultan. Favoritos independientes por perfil. No hay PIN ni autenticación: no es una frontera de seguridad. El catálogo original es inspeccionable en el código/HTML.

## Paridad y límites

Qt y HTML comparten el catálogo y los gráficos originales, pero utilizan implementaciones de modelo distintas, ambas probadas. No se promete igualdad de píxeles: fuentes y controles nativos pueden diferir. El renderizado 4K valida composición, no rendimiento ni soporte de un televisor particular. Los contratos de hardware siguen sin implementarse.

## Fondos y progreso demostrativo

Ver `VISUAL_PROGRESS_0.2.md`: proveedor de progreso inyectable, fixtures separados, modos persistentes y componente de fondo compartido con precarga/fundido. El porcentaje es opcional y no se infiere desde tiempo o logros.

## Rediseño de consola

`ConsolePage.qml` reutiliza LibraryPage dentro de un contenedor vertical con carrusel horizontal, ficha contextual y acceso a biblioteca. Solo existen dos pestañas visibles: rutas 1 (Videojuegos) y 2 (Multimedia). Ruta 3 se abre desde engranaje. Ruta histórica 0 redirige a 1 para compatibilidad de llamadas; no existe pantalla Inicio. El perfil se elige en un popup, no alterna automáticamente.

`showcase` es independiente de búsqueda/filtros: recientes de videojuegos ordenados por sesión, o selección multimedia sin fingir historial de visionado. `openTitle(id)` permite abrir desde el carrusel sin perder el contexto filtrado. La cuadrícula sigue usando índices. Qt y HTML restauran selección y desplazamiento al volver.

`core/artwork.py` resuelve carátula y fondo por separado desde `artwork.json`, restringidos a recursos locales con procedencia/derechos y permiso de redistribución registrado. Qt usa URLs locales; el generador HTML incrusta ambos roles. El contrato MetadataProvider no realiza llamadas. El catálogo se etiqueta `catalog_source=demo`, `installed=false`; un futuro inventario instalado será una fuente distinta. Ver ARTWORK_PROVIDERS.md.

## Biblioteca real y proceso directo

La entrega vigente se detalla en REAL_LAUNCH.md. Store migra a esquema 3 con real_games/play_sessions; InstalledLibrary valida rutas nativas sin ejecutarlas, consulta inventario y agrega sesiones observadas. Launcher es QObject/QProcess no bloqueante; confirma identidad SHA-256, captura started/finished/errorOccurred y usa reloj monotónico. Bridge expone origen real/demo, importación, pendingLaunch, confirm/cancel y estado; la UI usa LocalLibraryDialogs para revisión explícita. El app entrypoint mantiene QLockFile durante la instancia y evita cerrar la ventana con un proceso supervisado.

LocalArtwork decodifica/copía imágenes raster a caché personal y mantiene un candidato pendiente hasta confirmar. La identidad oficial y el manifiesto demo no se reemplazan. Nada de la biblioteca personal se incrusta en HTML. La fuente de progreso demo no se aplica a títulos local-UUID; estos solo tienen tiempo observado y percent=None. La barra requiere verifiedPercent explícito y no aparece en esta entrega para campaña.
