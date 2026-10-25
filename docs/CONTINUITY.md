# Continuidad del proyecto

Nombre actual: ORVEX OS (antes JARVIS Entertainment OS).
Entrega: 0.1 Visual Preview.
Prioridad: revisar visualmente el diseño sin instalar Linux. Qt/QML es la interfaz principal; la vista HTML es secundaria.

## Requisitos que se mantienen

- Experiencia de consola: biblioteca unificada y selección de un título para jugar, ocultando emuladores en el uso normal.
- Componentes maduros y probados; sin integraciones experimentales en el producto principal.
- Núcleo, interfaz, controles, emuladores y multimedia separados.
- Futuras entradas por mandos, pareo/reconexión Bluetooth y audio para varias salidas.
- Importación de archivos con validación, duplicados, progreso y control del usuario sobre metadatos.
- Perfiles y control parental con contenido infantil filtrado; detalles por confirmar antes de implementar.
- No incluir ROMs, BIOS ni firmware. No asumir costos ni modificar la configuración del equipo sin autorización.

## Estado verificable

Implementado: cuatro pantallas, teclado/mouse, catálogo ficticio, avisos de demo y una preferencia SQLite. Ocho pruebas locales aprobadas y capturas nativas 1080p/4K.
No implementado: distribución Linux, lanzamiento de juegos, reproducción, controles físicos, Bluetooth, perfiles y almacenamiento de medios.
Próximo paso: revisión visual, pantallas de detalle y estados vacíos; validar Windows/TV físicos.
