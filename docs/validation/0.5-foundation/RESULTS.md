# Validación · ORVEX 0.5 Foundation

Código basado en `0f6c76112884723e42bb893179fb6bdcf5f06b1c`. Entorno local Linux, Python 3.12, PySide6 6.8.3, backend Qt offscreen/software. Las bases y ejecutables de prueba se crean en TemporaryDirectory, capturas fuera del checkout. Ninguna biblioteca o configuración personal se usa en estas pruebas.

| Ejecución nueva | Resultado |
| --- | --- |
| Línea base antes de implementar | 96 Python/Qt OK (49,620 s) y 9 JavaScript OK. Logs baseline-*.txt. |
| Suite final local | **118 Python/Qt OK, cero omisiones** (48,677 s). linux-python.txt. |
| JavaScript final | **9 OK**, cero fallos/omisiones. linux-javascript.txt. |
| Ruff 0.11.13 | check OK, format --check OK (39 archivos incluidos por adopción gradual). |
| Diff | git diff --check OK. |
| Actions en el commit base | Run 40817976423 SUCCESS; evidencia histórica, no sustituye CI del código 0.5. |
| Actions 0.5 | Consultar Checks del PR nuevo y sus logs. El resultado remoto se registrará tras ejecutar Linux/Windows; no se presume aprobado por configurar YAML. |

## Cobertura nueva (22 pruebas, además de las 96 previas)

- 13 de catálogo/perfiles: cinco tipos y relación serie/episodio, reinicio, normalización Windows/deduplicación, búsqueda/filtros, favoritos/actividad por perfil, clasificación conservadora con casos compartidos JS, herencia infantil y ausencia de datos restringidos, propuestas/aprobación/conflicto/rechazo, rollback SQL, JSON inválido, contrato PIN denegado por defecto, importación sin Qt y CLI real; reporte no destructivo de colisiones introducidas por importadores anteriores.
- 5 de migración: conservación de juegos/arte/preferencias/perfiles de mando/journal/sesiones, fallo inyectado con rollback completo, transacciones anidadas, backups/restauración sin sobrescritura, corrupción y versiones incoherentes, lectura real del respaldo con Store 0.4. Snapshot propio tests/fixtures/store_v04_snapshot.py extraído sin cambios del commit base, SHA256 `950a0611452ff938327b64fd9170fd3f7f46dc3e09be62808ab5b1605baa94f7`.
- 4 de integración: **proceso nativo propio compilado y ejecutado realmente**, confirmación y perfil capturado al inicio, finalización/duración/persistencia; escáneres Dolphin/PCSX2 y argumentos mediante archivos ISO propios NO arrancables, sin ejecutar emulación; rechazo de lanzador inexistente; entrada GUI real en proceso aislado con --data-dir.

Las 96 regresiones conservadas incluyen navegación/foco, búsqueda/teclado virtual, biblioteca, configuración, sesiones, controladores y menú rápido. Las pruebas Qt emplean eventos sintetizados y fixtures; no equivalen a pulsar un mando físico.

Durante desarrollo una comprobación nueva de backup exigía igualdad binaria del archivo; falló porque SQLite backup modifica contadores de cabecera. Se corrigió la prueba para verificar contenido lógico, integridad, versión y apertura con Store 0.4. No se relajó la conservación de datos. La suite final anterior es posterior a esa corrección.

## Reproducir

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software ORVEX_REQUIRE_NATIVE_FIXTURE=1 ORVEX_CAPTURE_DIR=/tmp/orvex-foundation-captures PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
node --test tests/test_web_model.cjs
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```

En Windows el workflow habilita el MSVC preinstalado para que la fixture nativa sea obligatoria; usa Python 3.12 y Qt 6.8.3. Conserva las cinco pruebas adicionales a escala 150 %. El job Linux usa Python 3.11. Ambos publican capturas como artefactos. No se han contratado runners ni servicios externos.

## Pendientes físicos / límites

La evidencia comunicada por el usuario para 0.4 (Windows/DualSense/Dolphin/Mario Kart Wii, PS/HOME, pausa/reanudación/retorno/sesión) se registra como **manual histórica**. No se ha repetido en hardware para 0.5. Pendientes: PC del usuario y biblioteca real, mandos físicos, TV/DPI/GPU, Dolphin/PCSX2 y juegos comerciales; la pausa universal sigue sin certificarse. No se han descargado ROMs/BIOS. No hay reproducción multimedia, proveedor remoto ni autenticación PIN real en este sprint.
