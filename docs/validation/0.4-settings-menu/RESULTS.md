# Validación Configuración / menú de juego

Base 03558a6, PR #13.

- Suite local Linux/Python 3.12/PySide6 6.8.3: 93 pruebas Python/Qt OK, cero skips.
- JavaScript: 9 OK. Ruff: OK, formato gradual de 26 archivos: OK.
- Tras ajustes de aprobación/diálogos: 14 pruebas de gestión, mando y menú OK; comprobación final específica en local-settings-menu.txt.
- Escala 150 %: 6 pruebas de Configuración/Controller Manager OK en Qt offscreen Linux; no es Windows físico.
- Capturas locales inspeccionadas: seis secciones, selector abierto/cerrado con 60 nombres largos, vacío, 960×540, teclado, explorador, emuladores, gestor y menú. Recursos de prueba propios; no se incorporan imágenes de juegos comerciales ni perfiles del usuario.
- El workflow del commit ejecuta ambos runners y la tarea Windows añade Configuración a escala 150 %. Su resultado debe comprobarse en los Checks del PR; la actualización del cuerpo del PR conserva el enlace al run real. No inferir éxito desde el YAML.
- En Windows la prueba nativa exige una ventana C Win32 propia, WM_CLOSE por PID y marcador de cierre normal. En Linux ese mismo test comprueba la degradación explícita de WindowControl, sin fingir Win32.
- Guía/joystick y desconexión: lectores simulados mediante el enrutador de producción. Ninguna prueba acredita un mando físico.
- Pausa/reanudación efectiva de Dolphin/PCSX2/comerciales, fullscreen exclusivo, restricciones de foco de Windows e interferencia de Steam Input permanecen pendientes. La política de pausa solo lee el INI aprobado; no consulta el estado interno del emulador.

Ver ../../SETTINGS_AND_QUICK_MENU.md.
