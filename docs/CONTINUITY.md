# Continuidad de ORVEX

Rama: feature/orvex-real-launch. Base remota al retomar: a2bec127ed92311d9cb51ea0de6dcd3e1269a7e5 (PR #4). Correcciones locales identificables: 16706fc; el commit remoto de auditoría que contiene este documento es el punto vigente (consultar HEAD de la rama). No fusionar main ni PR #3 sin aprobación.

Implementado: GameLauncher con Disponible/Preparando/Ejecutando/Finalizado/Error; parámetros como array JSON persistido, literal y confirmado junto con SHA-256. Se mantiene importación sin ejecución, sesiones observadas y recursos locales confirmados. Conserva interfaz de consola y HTML exclusivamente visual.

Auditoría: Bridge.catalog eliminado; 45 casos compartidos Python/JS, incluidos 7.0 y valores inválidos. Política infantil acepta solo números integrales finitos 0–7, nunca bool/cadenas. Migraciones transaccionales 0→1→2→3→4, copia SQLite antes de migrar, rechazo de versión futura sin downgrade, comprobación de integridad y ventana de error sin borrar datos. JSON inválido conserva su valor y usa fallback. Recuperación de sesiones solo tras bloqueo de instancia.

Pruebas: 74 comprobaciones aprobadas: 52 Python/Qt, 9 Node y 13 recorridos Chromium/QtWebEngine Linux, Ruff check/format en siete módulos auditados. Capturas temporales fuera del checkout mediante ORVEX_CAPTURE_DIR (rechaza rutas internas); selectores visuales estables sustituyen coordenadas; manejo de flechas de biblioteca unificado. Logs audit-*.txt. Capturas anteriores versionadas siguen siendo históricas.

GitHub Actions: cero ejecuciones al revisar. Workflow manual actualizado con Ruff, timeout y artefactos fuera del checkout. No se despachó: cuota gratuita de repositorio privado no verificable. Ejecución remota pendiente; comprobaciones locales no equivalen a Actions aprobado.

Pendientes: Windows físico, mandos físicos y prueba inicial de entrada; no se afirma compatibilidad DualSense/Xbox/Wiimote. No hay hardware disponible y se priorizó estabilidad. Seguimiento de procesos hijos, progreso real de campaña y proveedores remotos siguen pendientes. Los perfiles demo no son control parental seguro.

Retomar: instalar requirements-dev.txt; ejecutar ruff check . y ruff format --check .; unittest discover -s tests -v con QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software PYTHONPATH=src; node --test tests/test_web_model.cjs. Navegador requiere Playwright/Chromium o QtWebEngine con dependencias gráficas. Windows: setup-windows.cmd y run-windows.cmd; importar ejecutable conocido con parámetros [] y confirmar. No repetir investigación ni reconstruir UI.
