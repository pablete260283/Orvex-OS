# Continuidad del proyecto

Nombre actual: ORVEX OS (antes JARVIS Entertainment OS).
Entrega: 0.2 Visual Preview en feature/orvex-0.2; 0.1 se conserva como base histórica.
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

Implementado: bibliotecas buscables/filtrables, favoritos por perfil, fichas, perfiles demo, seis categorías de ajustes y vista HTML autónoma. Ver ORVEX_0.2_STATUS.md y ORVEX_0.2_VALIDATION.md para el estado verificado.
No implementado: distribución Linux, lanzamiento de juegos, reproducción, controles físicos, Bluetooth, perfiles y almacenamiento de medios.
Próximo paso: revisar 0.2 y validar Windows/TV físicos. No fusionar el PR sin aprobación.
