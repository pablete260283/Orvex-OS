# ORVEX 0.5 · Sprint 1 Foundation

Versión de desarrollo `0.5.0a1`, basada exactamente en `0f6c76112884723e42bb893179fb6bdcf5f06b1c` (0.4 validada por el usuario). Rama `feature/orvex-0.5-foundation`. No reemplaza ni fusiona PR #13. La revisión de 0.5 se dirige a la rama 0.4 para mostrar únicamente este sprint.

## Implementación y límites

| Tarea | Implementación verificable |
| --- | --- |
| ORV-050-01 | Worktree y rama independientes desde el SHA validado; versión identificable y `--data-dir` para revisión aislada. |
| ORV-050-02 | Línea base ejecutada de nuevo: 96 Python/Qt y 9 JavaScript, antes de modificar código. |
| ORV-050-03 | `foundation.models.Content`: juegos, películas, series, episodios y aplicaciones; IDs estables, título alternativo, origen, formato, clasificación, estado, metadatos, arte y relación serie/episodio. |
| ORV-050-04 | Esquema 6 aditivo, respaldo previo, transacciones anidadas y restauración a un destino nuevo; pruebas con datos de esquema 5 y lector auténtico 0.4. |
| ORV-050-05 | Catálogo offline independiente de Qt: registro, deduplicación, consulta, búsqueda, filtros, favoritos y actividad por perfil. CLI ejecutable. |
| ORV-050-06 | Contratos tipados para proveedores, imágenes, reproducción y aplicaciones; puente funcional al GameLauncher existente. Sin nuevos proveedores ni reproductores. |
| ORV-050-07 | Perfiles persistentes, política conservadora y aislamiento de actividad/favoritos. Contrato de autorización adulta; implementación sin PIN deniega crear perfiles protegidos. |
| ORV-050-08 | Pruebas unitarias/integración/regresión, Ruff y workflow Linux/Windows. Resultados nuevos en validation/0.5-foundation. |

Este sprint construye servicios, no rediseña la consola. La GUI conserva los juegos importados, Dolphin/PCSX2, controles, menú durante juegos y sesiones existentes. Aún no presenta el nuevo catálogo multimedia en la interfaz ni reproduce películas. El HTML sigue siendo una vista visual autónoma sin acceso a ejecutables locales. No hay progreso de campaña inventado.

## Capas y propiedad de datos

- `ui/` y `core.bridge`: presentación Qt; recibe FoundationServices, y el lanzamiento pasa por LegacyGameGateway con permiso antes del lanzador existente.
- `foundation/catalog.py`, `profiles.py`, `models.py`: dominio sin dependencia Qt. No importan controladores, lanzan procesos ni contactan la red al registrar.
- `foundation/repository.py` y `core/store.py`: SQLite. `real_games` sigue siendo la fuente de verdad de los juegos reales; no se copian registros al nuevo catálogo. `game_catalog_details` añade solo campos que faltaban.
- `content_items`: nuevos tipos y referencias; claves canónicas de origen, relación de episodios y metadatos JSON. Registrar una referencia a un juego/aplicación no crea automáticamente un adaptador ejecutable.
- `controls/`, `runtime/` y GameLauncher: conservados; las sesiones nuevas capturan el perfil al iniciar, no al cerrar. Las históricas sin dueño conservan NULL y no se asignan arbitrariamente a un perfil.

Los favoritos reutilizan `favorites(profile,item_id)` con los IDs históricos `adult` y `child`. La actividad nueva es específica del perfil. Los informes globales antiguos no se convierten en actividad personal verificada.

El registro compara orígenes locales normalizados, incluido Windows, y evita duplicar registros existentes. Los importadores antiguos continúan intactos: si incorporan después una referencia que ya existía en content_items, `find_duplicates` informa el conflicto sin fusionar ni borrar datos. Resolver esa coincidencia requiere una futura revisión explícita; no se oculta este límite.

## Permisos y aprobación

El servicio filtra antes de devolver títulos, opciones, carátulas, búsqueda, favoritos, fichas o recientes. Un episodio hereda también la restricción de su serie. Edad inválida, desconocida, booleana, fraccionaria o fuera de rango se oculta al infantil. Política numérica Python compartida con LibraryService y contrastada con los mismos casos JavaScript existentes.

Los IDs de perfil identifican contexto local, **no autentican**. La selección de perfiles de la GUI 0.4 sigue siendo demostrativa. `NoPinAuthorizer` deniega las acciones protegidas nuevas; no implementa un PIN ficticio. Crear perfiles mediante servicio requiere un autorizador adulto inyectado. El hash, bloqueo de intentos, protección de secretos y conexión de PIN a la interfaz quedan para otro sprint. No es control parental seguro frente a un usuario con acceso local a archivos/código.

Los cambios de metadatos/arte se guardan como propuestas con proveedor y huella del registro original. Solo aprobación adulta explícita aplica cambios, mezclando los campos nuevos de metadatos sin borrar los demás; una propuesta obsoleta se rechaza. Cambios hechos desde la GUI antigua también invalidan la huella. No se descargan imágenes ni se asumen licencias; los contratos incluyen edición, atribución y licencia para una futura integración autorizada.

## Uso local del catálogo

Tras instalar las dependencias existentes, desde la raíz en PowerShell:

```powershell
$env:PYTHONPATH="src"
.\.venv\Scripts\python.exe -m orvex.foundation --database "$env:TEMP\orvex-foundation.sqlite3" register --kind movie --title "Vídeo propio" --source-type local --source-ref "D:\Videos\propio.mp4" --age 7
.\.venv\Scripts\python.exe -m orvex.foundation --database "$env:TEMP\orvex-foundation.sqlite3" --profile child list --kind movie
.\.venv\Scripts\python.exe -m orvex.foundation --database "$env:TEMP\orvex-foundation.sqlite3" duplicates
```

En Linux usar `PYTHONPATH=src .venv/bin/python -m orvex.foundation --database /tmp/orvex-foundation.sqlite3 ...`. La CLI no inicia procesos ni reproductores. Usar una base de prueba independiente y cerrar ORVEX antes de administrar una copia de su base. La CLI es una herramienta local confiable, no una API autenticada.

## Siguiente sprint

Conectar el catálogo unificado a la GUI sin duplicar la biblioteca real; implementar autenticación adulta real antes de exponer administración protegida; integrar reproducción local y proveedor autorizado por adaptadores. Mantener el perfil Joy-Con funcional del usuario y la pausa Dolphin validada en su escenario, sin extrapolar a otros motores.
