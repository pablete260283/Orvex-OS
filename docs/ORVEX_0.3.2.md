# ORVEX OS 0.3.2 — Biblioteca cinematográfica

Implementación sobre feature/orvex-0.3.1, sin fusionar PR #7 ni main. Referencia: imagen adjunta `image(20261026-062817).png`, recibida del usuario para Issue #8. La imagen se usa como referencia de composición, sin redistribuir sus ilustraciones comerciales.

## Cambios funcionales

La pantalla nativa conserva las dos secciones superiores, perfil y configuración. El fondo ocupa todo el escenario 16:9; se redujo la capa opaca y se añadieron degradados horizontales y verticales. Título, descripción limitada a dos líneas, plataforma, tiempo observado y acción de lanzamiento están sobre el fondo. Debajo aparece un carrusel de carátulas verticales 2:3 con selección ampliada y borde turquesa. Las carátulas conservan su proporción mediante PreserveAspectFit: nunca se fuerza el recorte. El fondo se recorta proporcionalmente para cubrir el viewport. La imagen entrante se carga antes de la transición; los recursos inválidos y ausentes usan el fondo base, sin conservar el arte de otro título. Movimiento reducido también desactiva el escalado animado.

El carrusel usa los registros reales de InstalledLibrary/SQLite. Dolphin, PCSX2 y ejecutables PC mantienen sus adaptadores, confirmación inicial y supervisión de sesiones. No se cambió el esquema ni se tocaron ROMs, configuraciones o partidas. Enter abre la ficha y su acción Jugar usa el lanzador real; también existe Jugar/Continuar en el hero. Flechas desplazan la selección; abajo abre la biblioteca completa con búsqueda y filtros. Esc vuelve. El scroll principal no muestra barra de escritorio. La versión visible ahora es 0.3.2.

## Carátulas y fondos personales

Configuración → Biblioteca → seleccionar juego → Carátula/Fondo. El selector local existente permite elegir PNG/JPEG/WebP. ORVEX decodifica y valida límites, muestra una vista previa y exige **Confirmar y aplicar** antes de escribir la asociación en SQLite. Cancelar no cambia el juego; reemplazar exige otra confirmación. La copia aprobada queda en la caché personal y se recupera al reiniciar. No se incluyen imágenes comerciales ni claves en Git.

La búsqueda remota de imágenes no está implementada: requiere proveedor configurado y permisos de uso. El selector de archivos local es la vía funcional actual; no se presentan resultados ficticios como búsquedas. Ver docs/ARTWORK_PROVIDERS.md. El preview HTML histórico sigue siendo demostrativo y no representa esta actualización nativa ni ejecuta juegos locales.

## Pruebas ejecutadas en Linux

Comando reproducible (tras instalar requirements.txt):

```sh
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software PYTHONPATH=src python -m unittest discover -s tests -v
```

63 ejecuciones Python/Qt y 9 pruebas JavaScript correctas. La colección incluye repeticiones heredadas de RealUiTests; no son 63 escenarios únicos. Resultados completos en validation/0.3.2/tests.txt y javascript.txt. Se incluyen regresiones de importación, proceso C controlado real, fin de sesión, SQLite, aprobación/reemplazo de imágenes, filtro infantil, Dolphin y PCSX2. Los tests de emuladores validan adaptadores y comandos con fixtures, no emulación comercial.

Nueva prueba QML: importa ejecutables controlados en la biblioteca real, genera imágenes de prueba propias, aprueba recursos, verifica proporción 2:3, navegación de carrusel, apertura/cierre de ficha y renderiza 1920×1080 y 3840×2160. Las capturas native-1920.webp y native-3840.webp son ventanas Qt reales con aplicaciones controladas e imágenes gráficas de prueba; **no son pruebas de tus juegos ni un mock de navegador**. El fondo gráfico de prueba permite comprobar composición y legibilidad, pero la semejanza estética final con fotografía comercial requiere tu revisión con tus recursos.

## Validación Windows pendiente

1. Descargar feature/orvex-0.3.2 (Code → Download ZIP), extraer; usar el mismo Python 3.12/PySide6 6.8.3 y procedimiento README. Conservar el directorio de datos personal existente.
2. Abrir ORVEX con `python -m orvex` con `PYTHONPATH=src` (PowerShell: `$env:PYTHONPATH="src"`), como indica README. Confirmar recuperación de biblioteca, favoritos, carátulas y fondos.
3. Seleccionar Def Jam (Port), DBZ Budokai Tenkaichi 3 (PS2), Mario Kart Wii y New Super Mario Bros Wii; Army of Two si está disponible. Verificar fondo asociado, carátula completa, texto legible, selección y retorno desde ficha.
4. Asociar/cancelar/reemplazar imágenes desde Configuración; reiniciar y comprobar persistencia. Probar un título sin fondo y movimiento reducido.
5. Pulsar Jugar y confirmar lanzamiento cuando corresponda; cerrar el juego, comprobar regreso y duración. No afirmar compatibilidad nueva sin esta prueba física.
6. Revisar 1080p/4K y navegación por teclado/mouse. Mando físico sigue pendiente: los eventos Qt de teclado no certifican DualSense ni emparejamiento. No se añadió integración de mando en esta entrega.

Pendientes del Issue #8: búsqueda remota autorizada, fila de aplicaciones (no existe servicio de aplicaciones instalado), navegación física con mando y aceptación visual del usuario. El carrusel nativo ya funciona sobre la biblioteca real. No considerar cerrado el issue hasta completar estos puntos y la revisión.
