# ORVEX OS — integración del kit de identidad

Estado: integración provisional aprobada por el usuario y conservada en 0.2. El rediseño definitivo permanece pendiente.

## Recursos y revisión

Se revisaron la hoja de revisión y las instrucciones incluidas en el ZIP. Se conservan intactos los ocho SVG, los 24 PNG y la guía original en `src/orvex/ui/assets/brand/`. `SHA256.json` registra sus hashes. La hoja original está en `docs/brand/brand-kit-preview.png`.

El SVG horizontal tiene lienzo 610×165 y todos los elementos quedan dentro de sus límites. Incluye espacio transparente a la derecha: se conserva para respetar las proporciones entregadas. El símbolo mantiene el anillo segmentado, el corte diagonal y el acento angular. No se han redibujado formas, añadido brillos ni animaciones.

Los SVG son la reconstrucción simplificada del kit, no una extracción exacta de un diseño anterior. El texto sigue editable y utiliza DejaVu Sans con fallback: su métrica puede variar entre equipos. Convertir texto a contornos correspondería a una exportación final posterior a aprobación, no se realiza en esta entrega.

## Uso

- Cabecera común a las cuatro pantallas: `orvex-horizontal-dark.svg`, 350×94,67 unidades lógicas, proporción 610:165 y PreserveAspectFit. SVG rasterizado a 1220×330 para mantener definición hasta 4K. Sin mover el menú, el héroe ni las tarjetas.
- Icono de aplicación y favicon: `orvex-app-icon-dark.svg`; el símbolo independiente queda disponible en `svg/orvex-symbol-dark.svg`.
- QML y HTML tienen respaldo PNG del mismo kit. El HTML incrusta los mismos bytes del SVG y funciona sin rutas externas.
- Paleta de la marca: grafito #0B0F14, plata #E8EDF2/#AABAC3 y turquesa #00C9CF. Se mantiene la paleta del launcher aprobado: no se rediseñan controles ni fondos.
- Marca completa ORVEX OS en ventana, metadatos de aplicación, HTML y documentación. El nombre anterior solo queda en referencias históricas.

## Compatibilidad

Qt 6/QML, PySide6 y SQLite permanecen. No hay dependencias nuevas ni servicios. Se mantiene internamente la ubicación de preferencias de 0.1 (`Entertainment Preview`) para no perder ajustes existentes; el nombre visible y applicationName pasan a ORVEX OS. No se renombra el repositorio ni se cambia su privacidad.
