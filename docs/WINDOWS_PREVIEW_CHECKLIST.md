> La prueba vigente de la aplicación real y de la vista HTML está en [REAL_LAUNCH_CHECKLIST.md](REAL_LAUNCH_CHECKLIST.md). El siguiente contenido es historial de la vista visual.

# Recorrido vigente · nueva navegación

1. Abrir preview/ORVEX-0.2.html: debe arrancar en Videojuegos y mostrar solo dos pestañas.
2. Recorrer recientes; comprobar fondo, título, estadísticas y porcentaje desconocido en Órbita.
3. Continuar jugando · DEMO abre ficha; volver conserva selección.
4. Biblioteca completa desplaza a búsqueda/filtros; abrir y volver conserva contexto.
5. Multimedia muestra selección y biblioteca equivalente, sin progreso ficticio de reproducción.
6. Icono de persona abre menú: elegir Infantil oculta títulos adultos en todas las superficies.
7. Engranaje abre configuración: probar fondos y movimiento reducido, recargar para persistencia.

Pendiente de ejecución en Windows físico por el usuario. Los recorridos Linux automatizados están en CONSOLE_NAVIGATION_0.2.md.

---
Registro de recorridos anteriores (pueden mencionar Inicio):

# Revisión guiada de ORVEX 0.2 desde Windows

1. En la rama `feature/orvex-0.2`, descarga `preview/ORVEX-0.2.html` usando Download raw file, o descarga el ZIP de esa rama y extrae el HTML.
2. Abre el archivo local con Edge/Chrome. No requiere instalar Python ni Linux.
3. Inicio → Explorar biblioteca. Busca `orbita`: debe aparecer Órbita. Selecciona PC y luego Arcade: este último no debe devolver coincidencias.
4. Limpia filtros. Abre una carátula, agrega un favorito y vuelve. Debe conservarse la carátula y cualquier búsqueda/filtro anterior. Activa Solo favoritos.
5. En Multimedia filtra Serie. Abre una ficha y verifica sinopsis y clasificación. Ver/Jugar · DEMO debe mostrar únicamente un aviso.
6. Cambia de Adulto a Infantil. Solo deben aparecer General/7+. No deben aparecer La señal, La última luna, Órbita ni Neon Drift; buscar esos títulos no debe devolverlos y las recomendaciones también deben filtrarse.
7. Revisa las seis categorías de configuración. Cambia Reducir movimiento y recarga el archivo; el ajuste y los favoritos deben conservarse si el navegador permite almacenamiento local.
8. Prueba Tab, Shift+Tab, flechas, Enter, Esc y F11. Repite con mouse. Prueba la ventana maximizada a 1080p y, si está disponible, en pantalla 4K.

Registrar navegador/versión, resolución, resultado y captura si algo falla. Mantener la ruta del HTML al probar persistencia. Una política restrictiva de archivos locales o una sesión privada puede impedir el guardado: la vista debe informar y continuar durante la sesión.

Los perfiles son demostrativos, cambiables sin PIN. No usar esta versión como protección parental real.

## Nueva revisión: fondos y progreso

En Inicio, enfoca Aurora, Órbita y Neon Drift: deben cambiar el título destacado y el fondo. Órbita muestra avance sin porcentaje conocido; los tres muestran tiempo, fecha y estado de demostración. Continuar · DEMO abre la ficha. En Videojuegos abre Bosque de luz para ver No iniciado. En Multimedia enfoca títulos para comprobar sus fondos.

En Configuración → Interfaz prueba Dinámico, Fijo (elige un título) y Predeterminado; recarga para comprobar persistencia. Activa movimiento reducido y repite. Un fondo fijo adulto no debe mostrarse en Infantil.
