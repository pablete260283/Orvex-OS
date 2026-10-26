# ORVEX OS 0.3.3 — Interfaz minimalista y navegación de consola

Issue #10. Base remota: feature/orvex-0.3.2, commit aad301462374ebb72188ae7150d6948ff4afa5af (PR #9). Rama nueva feature/orvex-0.3.3, sin fusionar dependencias ni main.

## Ocho requisitos

1. **Una biblioteca:** se retira la pantalla secundaria y el botón Biblioteca completa. El carrusel principal contiene todos los registros permitidos, sin límite de ocho. ListView reutiliza delegados con caché acotada y mantiene el elemento enfocado a la vista; búsqueda para catálogos grandes. El antiguo componente LibraryPage permanece en el código como componente no instanciado, sin perder servicios de filtros/favoritos.
2. **Una confirmación coherente:** se retira Jugar/Continuar del hero. Mover foco cambia únicamente selección y fondo. Confirmar una carátula abre la ficha existente con foco inicial en Jugar; el lanzamiento conserva la confirmación de confianza cuando corresponde. Navegar nunca ejecuta archivos.
3. **Orden reciente:** última sesión real descendente; títulos nunca jugados después, por nombre normalizado e ID como desempate. Sin timestamps inventados. La notificación del lanzador actualiza el modelo al terminar y el retorno a la ventana refresca los datos. No se reescriben sesiones para ordenar. La búsqueda respeta ese orden.
4. **Iconos superiores:** búsqueda, perfil y ajustes sin fondos ni marcos de botón. Un indicador turquesa bajo el icono muestra el foco. Recorrido explícito izquierda/derecha entre pestañas e iconos; abajo vuelve al carrusel. Perfil tiene navegación circular Adulto/Infantil y retorno al carrusel.
5. **Sesiones discretas:** ni hero ni ficha muestran tiempo o fecha de sesiones. Los registros, historial técnico, diagnóstico, duración y persistencia continúan funcionando. No cambia el esquema SQLite.
6. **Búsqueda contextual:** lupa SVG abre overlay modal, con letras, números, ñ, vocales acentuadas, ü, puntuación básica, espacio, borrar, limpiar, resultados y cancelar. Se usa solo dirección/confirmar/volver. Resultados actualizados al escribir, sin coincidencias, límite de 120 caracteres y elipsis de textos largos. Resultados cierra el teclado y enfoca una carátula; si no hay resultados vuelve a la lupa. Cancelar/Volver restaura la consulta anterior. Cada sección/perfil conserva su estado de búsqueda y el filtro infantil se aplica antes de mostrar resultados/fondos/fichas.
7. **Marca:** se retira TU BIBLIOTECA LOCAL, conservando el SVG oficial y su proporción.
8. **Consola real:** se conservan fondo cinematográfico, degradados, carátulas 2:3 y aprobación local de recursos. Los adaptadores PC, Dolphin y PCSX2 no se sustituyen. La versión visible y del paquete es 0.3.3.

## Entrada de mando y control remoto

Nuevo paquete `orvex.controls`, separado de biblioteca/emuladores. No instala drivers ni modifica perfiles de Dolphin o PCSX2.

- **Windows:** consulta XInput primero (A/B y D-pad/joystick). Si no hay dispositivo XInput usa WinMM (POV/joystick y botones). La alternativa WinMM asume por defecto el orden Sony Square/Cross/Circle/Triangle; Configuración → Controles permite cambiar a botones estándar 1/2 y guarda la preferencia en SQLite. No es una afirmación de compatibilidad física con todos los DualSense ni de emparejamiento automático.
- **Linux:** lectura no bloqueante de joydev `/dev/input/js*`, ejes habituales 0/1 y 6/7, botones 0/1. Reintenta conexión y cierra descriptores al salir. No modifica permisos; si el sistema no expone joydev o usa otro mapa hace falta configurar/validar ese dispositivo.
- **Control remoto:** el recorrido funciona con eventos de dirección y Enter/Escape; también se traducen Qt Select/Back. No se implementa Bluetooth/IR ni se garantiza el mapa de un dispositivo no probado.
- **Seguridad de interacción:** confirmar/volver se activan por pulsación, sin repetición automática del mando; las direcciones admiten repetición. Se exige estado neutral al inicio y al volver de un juego o perder foco. No se envían eventos cuando no hay ventana Qt enfocada o cuando el juego supervisado está ejecutándose. No se inyectan controles en los emuladores.

Las operaciones habituales de explorar, buscar, abrir ficha, favoritos, jugar, confirmar y regresar tienen recorrido sin teclado/ratón para estos mapas. Importar rutas y administrar archivos sigue siendo una operación técnica en Configuración, no se añadió un teclado universal para formularios de administración.

## Pruebas ejecutadas

Linux, Python 3.12.14 del entorno con PySide6 6.8.3, render software/offscreen. **70 ejecuciones Python/Qt, 9 pruebas JavaScript, Ruff y comprobación de formato correctas.** Resultados en `docs/validation/0.3.3/`. GitHub Actions se revisó (workflow_dispatch); no se activó ni se consumió su cuota.

```sh
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software PYTHONPATH=src python -m unittest discover -s tests -v
node --test tests/test_web_model.cjs
ruff check .
ruff check --config "include=['*.py']" src/orvex/controls tests/test_controller.py
```

La suite incluye ejecuciones heredadas repetidas de RealUiTests; el total de ejecuciones no equivale a escenarios únicos. Se sustituyen los tests de la pantalla secundaria retirada por los nuevos recorridos del carrusel/búsqueda; se conservan las pruebas de servicios, filtros infantiles, SQLite y lanzadores.

Pruebas nuevas verificables:

- Catálogo de 15 aplicaciones controladas, sin truncar; orden por dos sesiones de prueba, desempate determinista y conservación tras reabrir SQLite.
- Estructuras ABI XInput/JOYINFOEX, máscaras, POV y zonas muertas; decodificador joydev con eventos binarios simulados.
- Enrutador real con lector de mando simulado: repetición de direcciones, no repetición de confirmar, bloqueo durante ejecución y estado neutral al volver.
- Ventana QML real: subir desde carátula a lupa, teclado virtual completo mediante eventos semánticos del mismo enrutador de producción, acentos, borrar, espacio, limpiar, resultados, cancelación, foco al volver, navegación perfil/ajustes y búsqueda aislada por sección.
- **Proceso real:** importar ejecutable C controlado, abrir ficha, confirmar primer lanzamiento, esperar su finalización, guardar duración y volver al carrusel usando el enrutador. El lector se simula; el proceso y SQLite son reales. No se confunde esto con prueba física de mando.
- Regresiones de importación, recursos aprobados, persistencia, errores, Dolphin/PCSX2 con fixtures y comandos. No se ejecutaron esos emuladores reales en este entorno.
- Capturas de ventanas Qt a 1920×1080 y 3840×2160, con recursos de prueba propios y catálogo demo identificado para búsqueda multimedia. No son capturas Windows ni evidencia de juegos comerciales probados.

El HTML histórico permanece sin cambios y demostrativo. No ejecuta juegos ni incorpora este nuevo adaptador nativo.

## Validación pendiente en Windows, DualSense y control remoto

No hay mando físico ni escritorio Windows en este entorno. **La aceptación de operación 100% con mando sigue pendiente de estas pruebas físicas.** No debe marcarse el issue como aceptado solo por las pruebas automatizadas.

1. Descargar feature/orvex-0.3.3 (Code → Download ZIP), extraer y usar Python 3.12/PySide6 6.8.3 como en 0.3.2. Conservar datos personales existentes. PowerShell:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\python -m pip install -r requirements.txt
   $env:PYTHONPATH="src"
   .\.venv\Scripts\python -m orvex
   ```

2. Conectar DualSense USB ya configurado en Windows. Sin teclado ni ratón, usar cruceta/joystick, Cross y Circle. Verificar ambos botones antes de ejecutar un juego; si WinMM entrega otro orden elegir Estándar en Configuración → Controles. Si Steam Input produce además eventos de teclado, evitar un mapeo duplicado durante la prueba. No cambiar perfiles de emuladores para probar ORVEX.
3. Confirmar que las carátulas de toda la biblioteca siguen disponibles. Pulsar arriba → lupa; buscar por letras/acentos, borrar, espacio, limpiar, ver resultados, cancelar y comprobar foco. Probar consulta sin resultados y un nombre largo. Cambiar Videojuegos/Multimedia y perfil; verificar que Infantil no exponga contenido sin clasificación válida (los perfiles siguen siendo demo sin PIN).
4. Seleccionar y lanzar Def Jam (Port/PC), DBZ BT3 (PCSX2), Mario Kart Wii y NSMBW (Dolphin), Army of Two si está disponible. Una carátula solo abre la ficha; confirmar Jugar inicia el proceso según la confianza ya guardada. Cerrar desde cada juego y comprobar retorno. Mantener Cross pulsado al volver no debe lanzar de nuevo.
5. Jugar otro título, cerrar, comprobar que pasa al primer lugar; reiniciar ORVEX y verificar orden y biblioteca. Revisar sesiones desde Configuración → Sistema aunque no sean visibles en el hero/ficha.
6. Repetir búsqueda/confirmación/volver con control remoto si está disponible. Anotar modelo, conexión, API expuesta, botones y cualquier fallo de foco; capturar Windows 1080p y validar 4K si se dispone de pantalla. No se afirma compatibilidad universal ni emparejamiento automático.

## Pendientes y continuidad

Aceptación visual y hardware Windows; mapas especiales de otros mandos/remotos; Bluetooth/IR y mandos simultáneos; no se alteró la integración de controles dentro de emuladores. Mantener PR independiente basado en 0.3.2, sin fusionar main ni cerrar automáticamente Issue #10.

Fuentes primarias usadas para los adaptadores:

- https://learn.microsoft.com/en-us/windows/win32/xinput/getting-started-with-xinput
- https://learn.microsoft.com/en-us/windows/win32/api/xinput/ns-xinput-xinput_gamepad
- https://learn.microsoft.com/en-us/windows/win32/api/joystickapi/ns-joystickapi-joyinfoex
- https://github.com/torvalds/linux/blob/master/Documentation/input/joydev/joystick-api.rst
