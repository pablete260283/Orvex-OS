# Configuración y menú durante juegos — Issue #14

Rama: `feature/orvex-0.4-controller-manager`, PR #13. Base verificada `03558a6a498caf2e2c9c7ae50eeebf755245d57b`. No se modifica main ni se fusionan dependencias.

## Reproducción y corrección

Se revisó la captura Windows del usuario con Just Dance 2020. Se reprodujo el selector con un juego de prueba: el modelo tenía un elemento pero el texto de la fila no se dibujaba. DarkCombo dependía de `parent.text` dentro de su contentItem; se referencia ahora el delegado por ID y se obtiene el texto con `ComboBox.textAt(index)`. La prueba verifica también el Text renderizado, no solo el modelo. Con 60 títulos, la altura queda limitada a 328 unidades lógicas (cinco filas), con selección, scroll, confirmar, cancelar y devolución del foco. No se cambia la biblioteca de Pablo.

Se conservan las seis categorías. El panel usa scroll y campos con altura legible, botones dimensionados y navegación explícita categoría → contenido → categorías. Las opciones no implementadas de Audio se describen como futuras sin interruptores ficticios. Biblioteca carga automáticamente el registro seleccionado y conserva las acciones reales de edición, ocultamiento, metadatos locales, imágenes y retirada confirmada. No se borran archivos de juegos ni partidas.

El teclado virtual de edición trabaja con un borrador: Guardar aplica al campo, Volver/Cancelar conserva el original; Guardar edición persiste en SQLite. El explorador de archivos propio sustituye los selectores nativos en las acciones de importación/imágenes/perfiles, con navegación de carpetas, unidades, filtro por extensión y entrada de ruta mediante teclado virtual. La lectura de directorios está restringida al perfil Adulto. Muestra hasta 1000 entradas y permite acceso directo por ruta. No ejecuta ni modifica archivos.

## Menú rápido implementado

Ventana Qt independiente, oscura y siempre encima (cuando el gestor de ventanas lo permite), con tres opciones principales:

1. Continuar jugando.
2. Cerrar juego y volver a ORVEX.
3. Configuración de controles.

El estado se separa en `closed`, `menu`, `controls`, `confirm-close` y `waiting-close`. HOME nunca cierra directamente. El cierre exige confirmación y solicita `WM_CLOSE` a una ventana perteneciente al PID supervisado; el juego puede pedir guardar o rechazar el cierre. No hay terminación forzada ni escalada por timeout. La sesión y la restauración del Controller Manager se completan solo cuando termina realmente el proceso. Un fallo de envío conserva el juego y muestra una explicación. Un cierre externo limpia el menú y vuelve a la biblioteca.

Configuración de controles abre los ajustes reales sin finalizar el juego. El inventario puede consultarse; los cambios de configuración externa/perfiles permanecen bloqueados mientras hay un juego en ejecución. El layout del mando para ORVEX y el atajo sí pueden configurarse. No es un editor de mapeos Dolphin en vivo.

## Botón de sistema y atajos

Se reutiliza SDL2 si ya existe una biblioteca disponible; no se descarga una DLL. Un único lector elige SDL mapeado o la alternativa XInput/WinMM/joydev, para no enviar la misma entrada dos veces. Se añade GUIDE solo cuando SDL lo reporta. No se interpreta el bit reservado 0x0400 de XInput como Guide.

Atajo inicial XInput/SDL: mantener Back/View + Start/Menu aproximadamente un segundo. En Configuración → Controles → Menú de juego se puede aprender otra combinación de botones expuestos por el backend. Primero hay que soltar los botones. HOME/Guide y combinaciones son de flanco con espera, sin repetición, y exigen neutral tras desconexión/error. F10 funciona cuando ORVEX tiene foco; no se registra como hook global de teclado.

SDL no garantiza que Windows, Steam Input o el driver expongan PS/Guide/HOME. WinMM y joydev solo ofrecen índices crudos; no se atribuye un índice a HOME de una familia sin evidencia. El lector SDL tampoco certifica identidad física ni emparejamiento. La navegación se prueba con eventos semánticos y lectores simulados, diferenciada del hardware.

## Pausa y foco: límites explícitos

No existe una orden universal y verificable de pausa para todos los juegos. No se usa NtSuspendProcess/SIGSTOP, no se alternan F10/Space a ciegas y no se alteran archivos de Dolphin/PCSX2.

La integración disponible delega la pausa/reanudación al mecanismo nativo de pérdida/recuperación de foco cuando ya está habilitado por el usuario:

- Dolphin: `[Interface] PauseOnFocusLost=True` en el INI activo.
- PCSX2 Qt: `[UI] PauseOnFocusLoss=true` en el INI activo.
- PC nativo: sin mecanismo general; el juego puede continuar.

En Emuladores y carpetas se puede aprobar la referencia al INI existente. ORVEX lo lee y valida, nunca lo cambia; vuelve a comprobar la opción al abrir el menú. La pérdida de foco se produce al activar la ventana del menú y se solicita el foco del juego al Continuar. **Un INI habilitado no demuestra que el emulador esté pausado:** no se observa su estado interno, las rutas activas pueden diferir, y NetPlay/versiones/fullscreen pueden cambiar el comportamiento. El mensaje no declara «pausado» sin confirmación.

Windows puede rechazar SetForegroundWindow y un juego en pantalla completa exclusiva puede ocultar una ventana externa. No hay inyección gráfica ni bloqueo global de entradas HID: si el emulador permite entrada en segundo plano, el mando podría llegar también al juego. Estos puntos requieren validación física; no se presenta la superposición como universal. En Linux/Wayland, el backend de cierre/foco externo queda explícitamente no disponible en esta entrega y muestra la alternativa de volver al juego y cerrarlo desde su menú.

## Pruebas y capturas

Las pruebas nuevas recorren seis categorías con el enrutador de producción, comprueban edición/SQLite, teclado virtual, selector vacío y con 60 títulos, textos renderizados, foco y retorno. Capturas Qt a 1920×1080, 1280×720 y 960×540. El workflow Windows incluye además una ejecución de Configuración con `QT_SCALE_FACTOR=1.5`. Capturas en el directorio temporal del runner; solo la selección revisada se versiona.

Pruebas del menú: apertura, tres acciones, cancelar cierre, envío rechazado, salida externa, persistencia del atajo, neutral/desconexión, GUIDE SDL simulado, bits reservados XInput y lectura conservadora del INI sin cambios. El proceso de sesión es una aplicación C propia. En Windows se compila una ventana Win32 propia y se comprueba **WM_CLOSE real y su salida normal**, con validación de PID. En Linux se comprueba degradación explícita; no se simula que Win32 se ejecutó allí.

La pausa física y el foco sobre Dolphin/PCSX2/juegos comerciales siguen pendientes. La prueba comunicada por Pablo de Joy-Con derecho + Wii Sports con acelerómetro/giroscopio se conserva como evidencia manual anterior; este ciclo no usa ni reemplaza su INI.

## Fuentes técnicas primarias consultadas

- Qt ComboBox: https://doc.qt.io/qt-6.8/qml-qtquick-controls-combobox.html
- SDL2 GameControllerButton: https://wiki.libsdl.org/SDL2/SDL_GameControllerButton
- SDL2 background events: https://wiki.libsdl.org/SDL2/SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS
- Microsoft XINPUT_GAMEPAD (bits reservados): https://learn.microsoft.com/en-us/windows/win32/api/xinput/ns-xinput-xinput_gamepad
- Microsoft WM_CLOSE: https://learn.microsoft.com/en-us/windows/win32/winmsg/wm-close
- Microsoft SetForegroundWindow (restricciones): https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow
- Dolphin MAIN_PAUSE_ON_FOCUS_LOST: https://github.com/dolphin-emu/dolphin/blob/master/Source/Core/Core/Config/MainSettings.cpp
- Dolphin pérdida de foco/NetPlay: https://github.com/dolphin-emu/dolphin/blob/master/Source/Core/DolphinQt/MainWindow.cpp
- PCSX2 lectura UI/PauseOnFocusLoss: https://github.com/PCSX2/pcsx2/blob/master/pcsx2-qt/QtHost.cpp

## Ejecutar en Windows

Descargar la rama `feature/orvex-0.4-controller-manager`, extraer y ejecutar setup-windows.cmd (Python 3.12 de 64 bits), luego run-windows.cmd. Conservar la carpeta de datos personal; no es necesario recrear SQLite. Configuración se abre con el engranaje; confirmar entra al contenido y a desplegables/campos. Para jugar se mantiene la validación del primer ejecutable. Para el menú usar GUIDE si está expuesto, el atajo aprendido o F10 con foco ORVEX. No cambiar un perfil Dolphin funcional para probar el menú.

## Regresión adicional al finalizar un juego

Se reprodujo un cierre externo mientras estaba abierto el gestor desde el menú: el estado volvía a Videojuegos, pero controllerManager.opened permanecía true. SettingsPage ahora cierra sus diálogos al ocultarse y el retorno cancela teclado/explorador pendientes sin guardar. Una prueba nueva ejecuta una sesión real controlada, abre el gestor por el enrutador, finaliza el proceso y exige biblioteca enfocada y diálogo cerrado. Once pruebas específicas pasan después de la corrección.

La primera CI de este ciclo (40816150762) quedó esperando la cancelación de un runner Windows sin pasos ejecutados y bloqueó el run PR 40816154776 por concurrencia de rama. El grupo de concurrencia incluye ahora el SHA del head: sigue deduplicando push/PR del mismo código y permite validar un commit posterior sin esperar una cancelación ajena. Esto no convierte un job bloqueado en éxito; los resultados finales se registran en el PR.

## Segunda comprobación Windows y decisión sobre historial

Run 40816638345: Linux pasó 94 Python/Qt y 9 JS; Windows completó 94 casos con un error de compilación de la nueva fixture GUI (93 correctos). No se presenta ese run como verde. Se pasa user32.lib explícitamente al enlazador mediante /link y se conserva stdout/stderr del compilador si falla, en lugar de ocultar el diagnóstico. La siguiente CI debe ejecutar nuevamente la ventana real y el escalado.

Se reprodujo además que Enter/Confirmar no alternaba el CheckBox de historial. Se añadió activación explícita y foco visible; cada apertura restablece Conservar historial y enfoca Cancelar. Una prueba antes/después comprueba alternar y cancelar sin retirar el juego ni tocar archivos. Doce pruebas de Configuración/menú pasan tras los cambios.

## Validación Windows obtenida

Run [40817124951](https://github.com/pablete260283/Orvex-OS/actions/runs/40817124951), commit 5d880aa38bfd5a812bc80583c7772828ce4b7d0d: ambos jobs SUCCESS. Linux ejecutó 95 Python/Qt y 9 JS; Windows 95 Python/Qt, 9 JS y cinco pruebas adicionales de Configuración a escala 150 %, sin skips. La ventana C Win32 recibió WM_CLOSE y terminó normalmente: se ejecutó la prueba, no un mock de esa API. Las pruebas de mando/pausa interna siguen siendo simulaciones/política de configuración, no hardware ni emulación física.

Se descargó e inspeccionó el artefacto Windows 12873027623 (menú, Biblioteca y escalado): texto visible, selección y cinco filas correctas. Las tres capturas Windows se guardan aquí junto con los resultados. La última corrección visual amplía el campo de familia para mostrar Joy-Con derecho completo y muestra el detalle del dispositivo en texto separado; dos pruebas del gestor pasan localmente. Los Checks del último commit deben confirmarlo nuevamente.

Al reconfigurar una ruta de emulador, el lector libera sus handles SDL antes de cerrar el subsistema del inventario anterior y se reconstruye sobre el inventario nuevo. La señal de ciclo de vida y el orden de liberación se prueban con sustitutos controlados, sin atribuir una desconexión física. La configuración se rechaza mientras hay un proceso supervisado. Siete pruebas focalizadas de entrada/ciclo de vida pasan localmente.
