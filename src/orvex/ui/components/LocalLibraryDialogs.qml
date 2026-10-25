import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
Item {
    id: manager
    required property var backend
    property string imageGame: ""
    property string imageRole: "cover"
    function openImport(){importPopup.open()}
    function selectArtwork(gameId,role){imageGame=gameId;imageRole=role;imagePicker.open()}
    FileDialog { id: executablePicker; title: "Selecciona el ejecutable instalado"; fileMode: FileDialog.OpenFile; onAccepted: executable.text=selectedFile.toString() }
    FileDialog { id: imagePicker; title: "Selecciona una imagen que tengas derecho a utilizar"; nameFilters: ["Imágenes (*.png *.jpg *.jpeg *.webp)"]; onAccepted: manager.backend.prepareArtwork(manager.imageGame,manager.imageRole,selectedFile.toString()) }
    Popup {
        id: importPopup; objectName: "importPopup"; x: 410; y: 180; width: 1100; height: 700; modal: true; focus: true; padding: 40
        background: Rectangle { color: "#10202d"; radius: 22; border.color: "#a8f3de" }
        Column { Keys.onEscapePressed: {if(manager.backend.pendingLaunch.id)manager.backend.cancelLaunch();else if(manager.backend.pendingArtwork.id)manager.backend.cancelArtwork();else importPopup.close()} spacing: 22; width: parent.width
            Text { text: "Importar juego instalado"; font.pixelSize: 38; color: "#edf5f8" }
            Text { text: "Se guardará una referencia. Importar no ejecuta el archivo.
Windows: .exe nativo · Linux: ELF ejecutable · sin scripts ni argumentos."; font.pixelSize: 22; color: "#9fb4c4" }
            TextField { id: gameName; objectName: "importName"; width: parent.width; height: 60; font.pixelSize: 25; placeholderText: "Nombre del juego" }
            TextField { id: platform; objectName: "importPlatform"; width: parent.width; height: 60; font.pixelSize: 25; placeholderText: "Plataforma (por ejemplo, PC Windows o PC Linux)" }
            Row { spacing: 20
                TextField { id: executable; objectName: "importExecutable"; width: 735; height: 60; font.pixelSize: 21; placeholderText: "Ruta absoluta del ejecutable"; selectByMouse: true }
                ActionButton { width: 240; text: "Examinar…"; onClicked: executablePicker.open() }
            }
            Text { text: manager.backend.operationMessage; width: parent.width; wrapMode: Text.WordWrap; color: "#a8f3de"; font.pixelSize: 22; height: 75 }
            Row { spacing: 25
                ActionButton { objectName: "importSave"; width: 440; text: "Guardar sin ejecutar"; accent: true; onClicked: if(manager.backend.importGame(gameName.text,platform.text,executable.text)){importPopup.close();gameName.clear();executable.clear()} }
                ActionButton { width: 300; text: "Cancelar"; onClicked: importPopup.close() }
            }
        }
    }
    Popup {
        objectName: "launchConfirmation"; enter: Transition {} exit: Transition {} onOpened: cancelFirstLaunch.forceActiveFocus(); x: 410; y: 210; width: 1100; height: 600; padding: 40; modal: true; focus: true; closePolicy: Popup.NoAutoClose
        visible: !!manager.backend.pendingLaunch.id
        background: Rectangle { color: "#10202d"; radius: 22; border.color: "#a8f3de" }
        Column { Keys.onEscapePressed: {if(manager.backend.pendingLaunch.id)manager.backend.cancelLaunch();else if(manager.backend.pendingArtwork.id)manager.backend.cancelArtwork();else importPopup.close()} spacing: 28; width: parent.width
            Text { text: "Confirmar lanzamiento"; color: "#edf5f8"; font.pixelSize: 38 }
            Text { text: manager.backend.pendingLaunch.title || ""; color: "#a8f3de"; font.pixelSize: 30 }
            Text { text: manager.backend.pendingLaunch.path || ""; width: parent.width; wrapMode: Text.WrapAnywhere; font.pixelSize: 23; color: "#edf5f8" }
            Text { text: "Ejecuta solo archivos que conozcas y en los que confíes.
ORVEX no verifica que un ejecutable esté libre de software malicioso.
Se supervisa el proceso directo, sin detectar procesos hijos de un launcher."; width: parent.width; wrapMode: Text.WordWrap; font.pixelSize: 23; color: "#a7b9c8" }
            Row { spacing: 24
                ActionButton { id: acceptFirstLaunch; objectName: "confirmLaunch"; KeyNavigation.right: cancelFirstLaunch; KeyNavigation.left: cancelFirstLaunch; width: 440; accent: true; text: "Confirmar y ejecutar"; onClicked: manager.backend.confirmLaunch() }
                ActionButton { id: cancelFirstLaunch; objectName: "cancelLaunch"; KeyNavigation.right: acceptFirstLaunch; KeyNavigation.left: acceptFirstLaunch; width: 300; text: "Cancelar"; onClicked: manager.backend.cancelLaunch() }
            }
        }

    }
    Popup {
        objectName: "artworkConfirmation"; x: 410; y: 150; width: 1100; height: 780; padding: 40; modal: true; focus: true; closePolicy: Popup.NoAutoClose
        visible: !!manager.backend.pendingArtwork.id
        background: Rectangle { color: "#10202d"; radius: 22; border.color: "#a8f3de" }
        Column { Keys.onEscapePressed: {if(manager.backend.pendingLaunch.id)manager.backend.cancelLaunch();else if(manager.backend.pendingArtwork.id)manager.backend.cancelArtwork();else importPopup.close()} spacing: 24; width: parent.width
            Text { text: manager.backend.pendingArtwork.replacing?"Reemplazar recurso gráfico":"Asociar recurso gráfico"; font.pixelSize: 38; color: "#edf5f8" }
            Image { width: parent.width; height: 330; source: manager.backend.pendingArtwork.preview || ""; fillMode: Image.PreserveAspectFit }
            Text { text: manager.backend.pendingArtwork.source || ""; width: parent.width; wrapMode: Text.WrapAnywhere; color: "#edf5f8"; font.pixelSize: 21 }
            Text { text: "Se guardará solo en tu biblioteca personal. Confirma que puedes utilizar esta imagen.
No se descargan coincidencias ni se reemplazan recursos automáticamente."; width: parent.width; wrapMode: Text.WordWrap; color: "#a7b9c8"; font.pixelSize: 22 }
            Row { spacing: 24
                ActionButton { objectName: "confirmArtwork"; width: 440; accent: true; text: "Confirmar y aplicar"; onClicked: manager.backend.confirmArtwork() }
                ActionButton { width: 300; text: "Cancelar"; onClicked: manager.backend.cancelArtwork() }
            }
        }

    }
}
