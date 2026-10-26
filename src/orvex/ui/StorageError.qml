import QtQuick
import QtQuick.Window
import QtQuick.Controls
Window {
    width: 960; height: 560; visible: true; color: "#0b1320"; title: "ORVEX OS · Biblioteca no disponible"
    Column { anchors.fill: parent; anchors.margins: 40; spacing: 25
        Text { text: "No se pudo abrir la biblioteca"; color: "#a8f3de"; font.pixelSize: 32 }
        Text { width: parent.width; text: storageError; wrapMode: Text.WrapAnywhere; color: "#edf5f8"; font.pixelSize: 20 }
        Text { width: parent.width; text: "Archivo: "+storagePath+"\nNo se ha eliminado ni reemplazado. Conserva el archivo y las copias .bak. Si pertenece a una versión futura, abre ORVEX con esa versión."; wrapMode: Text.WrapAnywhere; color: "#adbdc9"; font.pixelSize: 19 }
        Button { text: "Cerrar"; onClicked: Qt.quit(); focus: true }
    }
}
