# Arquitectura y validación técnica

## Decisión

Qt Quick/QML se mantiene como interfaz principal, con PySide6 6.8.3 fijado como versión reproducible probada. No se afirma que sea la última versión. Qt for Python ofrece oficialmente carga de QML y exposición de datos desde Python: https://doc.qt.io/qtforpython-6/tutorials/qmlapp/qmlapplication.html

SQLite es una biblioteca transaccional integrada, sin servidor: https://www.sqlite.org/about.html . Es suficiente para preferencias locales en esta fase. Se comprobó escritura, actualización y lectura después de cerrar/reabrir la base.

Se validó la ejecución real de Qt/QML en Linux sin pantalla, con backend software y capturas; queda pendiente validar aceleración gráfica, tiempos de cuadro, DPI real y ejecución en Windows/TV físicos. El escalado 4K conserva coordenadas lógicas y arte vectorial. Una captura 4K valida composición y renderizado, no rendimiento de un equipo objetivo.

PySide6/Qt tienen términos LGPL/GPL/comerciales según módulo y distribución. Antes de empaquetar binarios se revisarán obligaciones y avisos: https://doc.qt.io/qtforpython-6/licenses.html . No se incorporan componentes experimentales ni servicios de IA al producto.

## Límites de módulos

| Ruta | Responsabilidad |
|---|---|
| `ui/Main.qml` | Composición, rutas y acciones lógicas de navegación |
| `ui/components/` | Elementos de menú y tarjetas reutilizables |
| `ui/assets/` | Ilustraciones vectoriales originales de demostración |
| `core/store.py` | Preferencias SQLite y lectura del catálogo demo |
| `core/bridge.py` | Contrato QObject de datos/ajustes para QML |
| `adapters/emulators.py` | Contrato futuro de lanzamiento; sin implementación |
| `adapters/controls.py` | Contrato futuro de entrada; sin detección ni pareo |
| `adapters/multimedia.py` | Contrato futuro de reproducción; sin implementación |
| `preview/ORVEX-0.1.html` | Vista secundaria autónoma para revisión del diseño |

No hay llamadas del QML a procesos, dispositivos ni redes. La vista HTML no será el núcleo del sistema Linux: duplica la presentación de esta entrega y debe verificarse cuando cambie el diseño. Las portadas son originales y no prueban emuladores ni streaming.

## Datos

`settings(key PRIMARY KEY, value JSON)`; esquema SQLite versión 1. No se escribe dentro del árbol de instalación. No hay importación ni inferencia de metadatos. El futuro catálogo y las correcciones de usuario deben mantenerse separados del demo. Los contratos de integración no se instancian en 0.1.
