# ORVEX OS — Kit de identidad visual v1

## Estado
Propuesta vectorial simplificada basada en el concepto visual aprobado por el usuario.
**No es una extracción vectorial exacta** de la imagen generada: los trazos y la tipografía
se reconstruyeron manualmente para producir recursos escalables y editables.

## Identidad
- Marca: ORVEX OS.
- Símbolo: anillo geométrico interrumpido con corte diagonal y acento angular.
- Estilo: minimalista, tecnológico, legible en TV.
- Turquesa: `#00C9CF`.
- Plata clara: `#E8EDF2`.
- Plata secundaria: `#AABAC3`.
- Grafito: `#0B0F14`.
- Superficie secundaria: `#1E2732`.

## Archivos
- `svg/`: logos vectoriales editables y escalables.
- `png/`: rasterizaciones transparentes 1x, 2x y 4x, excepto iconos de app que llevan fondo.
- `ORVEX-brand-preview.png`: hoja de revisión.
- `work-handoff.md`: instrucciones para integrar en Work.

## Reglas de uso
- Priorizar `orvex-horizontal-dark.svg` sobre fondos grafito.
- La variante `light` usa el mismo símbolo sin fondo para que se pueda ubicar sobre
  superficies claras, con tipografía oscura de alto contraste.
- No deformar el símbolo, ni añadir brillos, biseles o sombras en el producto.
- Conservar un área libre mínima de 1/4 de la altura del símbolo.
- Usar SVG en QML cuando la integración esté verificada; preparar PNG para fallback.
- Las fuentes del SVG son texto editable (`DejaVu Sans` o fallback); para reproducción
  tipográfica idéntica en distintas máquinas, convertir textos a contornos al exportar
  la versión final de producción.

## Pendiente de validación
Revisar visualmente estos vectores frente al logo aprobado antes de fijarlos como
identidad definitiva en el repositorio.
