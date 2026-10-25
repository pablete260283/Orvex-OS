# ORVEX OS 0.2 — Alcance de desarrollo

Estado: planificación de implementación; no se afirma que las funciones estén construidas.

## Objetivo
Evolucionar el prototipo visual 0.1 aprobado hacia una interfaz de consola más completa, sin simular capacidades reales como si estuvieran implementadas.

## Entrega 0.2
1. Fichas de detalle para videojuegos y contenido multimedia, con portada, descripción, plataforma/tipo, estado de disponibilidad y botón de demostración claramente identificado.
2. Biblioteca navegable con búsqueda y filtros por plataforma, tipo y favoritos; usar catálogo de prueba y mantenerlo separado de la lógica real.
3. Perfiles de demostración Adulto/Infantil; ocultar títulos y portadas no adecuados para el perfil infantil, incluso en búsquedas y recomendaciones. El PIN y la protección real deben declararse pendientes hasta tener implementación segura.
4. Ajustes organizados por categorías (interfaz, controles, audio, biblioteca, perfiles), distinguiendo opciones operativas de marcadores futuros.
5. Navegación por teclado y mouse sin regresiones, con arquitectura preparada para mandos.
6. Paridad visual entre Qt/QML y HTML offline; mantener el kit gráfico ORVEX OS provisional v1.
7. Tests automatizados, capturas 1080p/4K, validación documentada y procedimiento de prueba Windows.

## Reglas innegociables
- GitHub es la fuente única de verdad. Cada cambio debe quedar en esta rama y proponerse por Pull Request.
- Mantener main estable; no mezclar hasta revisión del usuario.
- Preservar 0.1 y la identidad ya aprobada; logo provisional para perfeccionar después.
- Arquitectura modular, SQLite para preferencias, Qt6/QML + PySide6, vista HTML independiente.
- Sin ROMs, BIOS, contenido protegido, credenciales ni servicios de pago.
- Metadatos de medios: sugerencias automáticas solo con confirmación del usuario; nunca sobreescribir datos originales sin autorización.
- 'Un clic y a jugar' es objetivo futuro, no funcionalidad ya disponible en 0.2.
- Documentar explícitamente lo implementado, lo simulado y lo pendiente.

## Criterios de aceptación
La vista previa debe permitir explorar biblioteca, filtrar, entrar y salir de fichas, cambiar entre perfiles demo y navegar ajustes sin romper las cuatro secciones originales. Probar los filtros y la ocultación infantil en Qt y HTML. Presentar capturas, pruebas y Pull Request antes de solicitar aprobación.
