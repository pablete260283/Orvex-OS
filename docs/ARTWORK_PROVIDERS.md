# Recursos visuales y proveedores · decisión 2026-10-25

## Investigación de referencias reales

Se revisaron las páginas oficiales de Ghost of Tsushima, God of War Ragnarök y Marvel’s Spider-Man 2 como referencias de carátulas y fondos. Contienen arte oficial; no se ha encontrado una licencia abierta o permiso expreso para redistribuir esas imágenes dentro del repositorio/HTML. No se descargan, copian, incluyen ni enlazan sus imágenes en la aplicación. Los nombres solo aparecen en esta investigación; no se presentan como juegos instalados.

Fuentes primarias consultadas:

- https://www.playstation.com/en-us/games/ghost-of-tsushima/
- https://www.playstation.com/en-us/games/god-of-war-ragnarok/
- https://www.playstation.com/en-us/games/marvels-spider-man-2/
- https://www.playstation.com/en-bh/legal/website-terms-of-use/
- https://www.playstation.com/en-hk/legal/copyright-and-trademark-notice/
- https://api-docs.igdb.com/
- https://www.steamgriddb.com/faq
- https://www.steamgriddb.com/terms (no contenido legible devuelto; no se infiere permiso)

Los avisos de PlayStation reservan derechos de los propietarios y sus términos no transfieren propiedad al descargar. Nuestra decisión conservadora de no redistribuir se basa en la ausencia de autorización comprobada; no constituye una declaración de que ningún uso legítimo sea posible.

IGDB ofrece búsqueda, covers y artworks, autenticación mediante credenciales Twitch y condiciones para uso no comercial; el uso comercial requiere tratar con IGDB. Su documentación admite caché y pide atribución visible en el contexto de acuerdos comerciales. Acceso a API y derechos de las imágenes deben verificarse por separado antes de incluir o distribuir recursos. SteamGridDB permite encontrar arte comunitario; no se ha verificado una autorización general de los titulares para redistribuirlo. No se han creado cuentas, usado tokens ni contratado servicios.

## Implementación entregada

Se conservan las seis ilustraciones SVG originales de ORVEX usadas por el catálogo ficticio. El nuevo manifiesto `core/artwork.json` declara carátula, fondo, proveedor, procedencia, derechos y redistribución para cada una. Los dos iconos utilitarios SVG también son trazados originales del proyecto. Logo provisional intacto. No son recreaciones de carátulas oficiales.

`resolve_art` acepta SVG, PNG, JPG y WebP locales dentro de assets, requiere procedencia/derechos y redistribución verdadera, y rechaza rutas externas, archivos ausentes y escapes del directorio. Estos campos registran una revisión humana: no prueban automáticamente una licencia. Qt carga las URLs aprobadas, y el generador offline incrusta ambos roles sin dependencias externas.

Para sustituir un recurso autorizado: guardar el archivo en assets, añadir su licencia/prueba de autorización y atribución, registrar ambos roles en el manifiesto y asignar la clave `art` al título. Reconstruir HTML y ejecutar pruebas. No hay selector de archivos ni descargador automático en esta fase.

## Adaptador futuro

1. Implementar MetadataProvider.search(title) y artwork(provider_id), manteniendo provider_id, plataforma y edición para evitar homónimos. Usar las tres referencias anteriores como casos de resolución; no inventar IDs.
2. Obtener credenciales fuera del repositorio/HTML; mantener secretos en servicio de metadatos o entorno local de confianza. No empaquetar client_secret en una vista web.
3. Validar términos vigentes, licencia de imágenes, atribución, caché, límites y permisos de distribución por proveedor/recurso. Si solo se autoriza uso local, guardar caché personal fuera del repositorio y excluirla del exportador offline.
4. Descargar solo tras esa validación; controlar origen, formatos, tamaño, errores y retirada. Conservar fallback original si falta imagen. Producir cover/backdrop y evidencia de derechos explícita para el resolver.
5. Mantener inventario instalado y catálogo demo separados; los metadatos no demuestran instalación ni disponibilidad jugable. Ningún porcentaje de progreso se deriva de imágenes o metadatos.

Pendiente: adaptadores de red, credenciales, caché personal, atribución de terceros en UI e inventario real. El contrato y la carga local aprobada funcionan; no se presenta una API real conectada.
