# Arquitectura ORVEX OS 0.2

Se mantiene Qt 6/QML, PySide6 6.8.3 y SQLite. No se añaden dependencias de producción. El kit ORVEX provisional permanece intacto.

| Módulo | Responsabilidad |
|---|---|
| `core/demo.json` | Único catálogo ficticio para Qt y generación HTML; datos separados de servicios |
| `core/library.py` | Filtrado de perfil, normalización, búsqueda, opciones y favoritos; sin Qt ni dispositivos |
| `core/store.py` | Preferencias existentes y favoritos SQLite por perfil |
| `core/bridge.py` | Adaptador QObject: rutas, contexto por biblioteca/perfil, detalle y señales |
| `ui/Main.qml` | Cabecera, Inicio, navegación y escalado 1920×1080 lógico |
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
