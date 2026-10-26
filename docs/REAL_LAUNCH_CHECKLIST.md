# Prueba guiada · primera ejecución real

## Windows (pendiente de prueba física)

1. Descargar y extraer el ZIP de feature/orvex-real-launch completo. Instalar Python 3.11+ de 64 bits si falta; ejecutar setup-windows.cmd y luego run-windows.cmd.
2. Verificar biblioteca real vacía, dos secciones y logo. Probar Tab/flechas y mouse.
3. Elegir una aplicación .exe conocida y de confianza ya instalada; importar nombre/plataforma/ruta. Confirmar que no se abrió al guardar. No usar un instalador como prueba.
4. Cerrar y volver a abrir ORVEX: debe conservar la referencia.
5. Continuar jugando: revisar nombre/ruta y cancelar. El proceso no debe iniciarse. Volver a solicitar y confirmar: debe abrir la aplicación.
6. Cerrar esa aplicación; comprobar tiempo y última sesión. El tiempo corresponde al proceso directo. Un launcher comercial puede delegar en otro proceso; no asumir seguimiento correcto.
7. Repetir lanzamiento sin cambios: ya no pide primera confirmación. Archivo modificado exige otra confirmación. Ruta ausente informa error, sin borrar la biblioteca.
8. Abrir ficha, Asociar carátula y fondo. Cancelar una vez; confirmar después y comprobar persistencia al reiniciar. Usar imágenes que puedas utilizar.
9. Cambiar a demo: no deben aparecer referencias reales mezcladas ni ejecutarse al pulsar acciones demo. Infantil debe ocultar todos los importados sin edad verificada.
10. Intentar cerrar ORVEX mientras la aplicación está supervisada: debe pedir cerrar primero el juego, sin terminarlo automáticamente.

La confirmación no evita todos los riesgos de un ejecutable desconocido. No se ha ejecutado esta lista en Windows físico; registrar versión de Windows/Python/Qt, aplicación usada, comportamiento y errores.

## Linux (ejecutado automáticamente)

```sh
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p 'test_real*.py' -v
```

Requiere compilador cc para construir la fixture propia temporal. No cambia permisos de juegos ni ejecuta comerciales. Ver REAL_LAUNCH.md y logs para resultados. Para revisar la UI real usar la aplicación normal desde un escritorio Linux.

## HTML

Abrir preview/ORVEX-0.2.html con Edge/Chrome, revisar carrusel, fondo/foco, biblioteca inferior, multimedia, perfil/engranaje. Sus acciones explican que el HTML no importa ni ejecuta juegos. No emplearlo como prueba del lanzador nativo.
