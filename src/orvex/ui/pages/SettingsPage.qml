import QtQuick
import QtQuick.Controls
import "../components"
Item {
    id: settings
    signal importRequested()
    signal artworkRequested(string gameId,string role)
    property string selectedGame: ""
    property var backend
    property int category: 0
    property string message: ""
    readonly property var categories: ["Interfaz","Controles","Audio","Biblioteca","Perfiles","Sistema"]
    function enter() { choices.itemAt(category).forceActiveFocus() }
    opacity: visible ? 1 : 0
    Behavior on opacity { NumberAnimation { duration: settings.backend.reducedMotion ? 0 : 120 } }
    Text { text: "Configuración"; color: "#edf5f8"; font.pixelSize: 46; font.weight: Font.DemiBold }
    Column { y: 110; spacing: 18
        Repeater { id: choices; model: settings.categories
            ActionButton { required property string modelData; required property int index; width: 350; text: modelData; selected: settings.category===index; onClicked: {settings.category=index;settings.message=""} }
        }
    }
    Rectangle { x: 410; y: 110; width: 1320; height: 660; radius: 26; color: "#132332"
        Text { x: 45; y: 38; text: settings.categories[settings.category]; color: "#edf5f8"; font.pixelSize: 38 }
        Text { visible: settings.category!==3; x: 45; y: 115; width: 1220; text: settings.category===0 ? "FUNCIONAL · Preferencias guardadas en SQLite" : settings.category===3 ? "FUNCIONAL · Filtros y favoritos por perfil" : settings.category===4 ? "DEMO · Filtro infantil hasta 7+. Sin autenticación ni PIN.
El cambio de perfil es libre: no es un control parental seguro." : settings.category===5 ? "FUNCIONAL · ORVEX OS 0.2 Visual Preview
Qt 6 / QML · PySide6 · SQLite
Biblioteca local y catálogo demo separados. Sin servicios externos." : "FUTURO · Esta categoría no controla dispositivos.
La integración se desarrollará en una próxima fase."; color: settings.category===1 || settings.category===2 ? "#bdac8c" : "#9cb5c7"; font.pixelSize: 26; wrapMode: Text.WordWrap; lineHeight: 1.5 }
        Row { x: 45; y: 395; spacing: 18; visible: settings.category===0
            Repeater { model: ["dynamic","fixed","default"]
                ActionButton { required property string modelData; width: 360; text: modelData==="dynamic" ? "Fondo dinámico" : modelData==="fixed" ? "Fondo fijo" : "Predeterminado"; selected: settings.backend.backgroundMode===modelData; onClicked: settings.backend.setBackgroundMode(modelData) }
            }
        }
        Row { x: 45; y: 485; spacing: 12; visible: settings.category===0 && settings.backend.backgroundMode==="fixed"
            Repeater { model: settings.backend.backgroundOptions
                ActionButton { required property var modelData; width: 135; text: modelData.title; selected: settings.backend.fixedBackground===modelData.id; onClicked: settings.backend.setFixedBackground(modelData.id) }
            }
        }
        ActionButton { objectName: "reducedMotion"; x: 45; y: 300; width: 650; visible: settings.category===0; text: "Reducir movimiento: "+(settings.backend.reducedMotion ? "Sí" : "No"); onClicked: settings.backend.toggleMotion() }
        ActionButton { x: 45; y: 300; width: 650; visible: false; text: "Limpiar filtros de las bibliotecas"; onClicked: {settings.backend.clearFilters();settings.message="Filtros restablecidos. Tus favoritos se conservan."} }
        Row { x: 45; y: 330; spacing: 30; visible: settings.category===4
            ActionButton { width: 350; text: "Adulto · demo"; selected: settings.backend.profile==="adult"; onClicked: settings.backend.setProfile("adult") }
            ActionButton { width: 350; text: "Infantil · demo"; selected: settings.backend.profile==="child"; onClicked: settings.backend.setProfile("child") }
        }
        Column { x: 40; y: 110; spacing: 14; visible: settings.category===3; width: 1220
            ActionButton { text: "Emuladores / carpetas…"; onClicked: dolphinSetup.open() }
            ActionButton { text: "Importar juego"; onClicked: settings.importRequested() }
            ComboBox { id: games; width: 1100; model: settings.backend.managedGames; textRole: "title"; onActivated: {var e=model[currentIndex];settings.selectedGame=e.id;editName.text=e.name;editPlatform.text=e.platform;editPath.text=e.executable;editArgs.text=e.arguments} }
            Row { spacing: 15
                TextField { id: editName; width: 550; placeholderText: "Nombre" }
                TextField { id: editPlatform; width: 550; placeholderText: "Plataforma" }
            }
            TextField { id: editPath; width: 1120; placeholderText: "Ruta del ejecutable" }
            TextField { id: editArgs; width: 1120; placeholderText: "Argumentos JSON" }
            Row { spacing: 15
                ActionButton { width: 260; text: "Guardar edición"; onClicked: settings.backend.editGame(settings.selectedGame,editName.text,editPlatform.text,editPath.text,editArgs.text) }
                ActionButton { width: 260; text: "Ocultar"; onClicked: settings.backend.hideGame(settings.selectedGame,true) }
                ActionButton { width: 260; text: "Mostrar"; onClicked: settings.backend.hideGame(settings.selectedGame,false) }
            }
            Row { spacing: 15
                ActionButton { width: 260; text: "Carátula…"; onClicked: settings.artworkRequested(settings.selectedGame,"cover") }
                ActionButton { width: 260; text: "Fondo…"; onClicked: settings.artworkRequested(settings.selectedGame,"backdrop") }
                ActionButton { width: 260; text: "Metadatos…"; onClicked: metadataEditor.open() }
            }
        }
        ActionButton { x: 900; y: 580; visible: settings.category===3; text: "Quitar de biblioteca…"; onClicked: removal.open() }
        Popup { id: dolphinSetup; x: 50; y: 20; width: 1150; height: 800; modal: true
            background: Rectangle {color: "#142333";radius: 18; border.color: "#a8f3de"}
            Column { spacing: 20; width: parent.width
                Label { color: "#edf5f8"; text: "Emuladores · Dolphin (Wii/GameCube), PCSX2 (PS2)" }
                ComboBox { id: emulatorChoice; width: 1050; model: ["dolphin","pcsx2"] }
                TextField { id: dolphinPath; width: 1050; placeholderText: "Ruta del ejecutable del emulador" }
                TextField { id: romRoot; width: 1050; placeholderText: "Carpeta principal de ROMs (contiene Wii y GameCube)" }
                ActionButton { text: "Guardar configuración"; onClicked: settings.backend.configureEmulator(emulatorChoice.currentText,dolphinPath.text,romRoot.text) }
                ActionButton { text: "Escanear ahora"; onClicked: settings.backend.scanEmulator(emulatorChoice.currentText) }
                Text { width: 1050; wrapMode: Text.Wrap; text: settings.backend.operationMessage; color: "#edf5f8" }
                Text { color: "#edf5f8"; text: "Selecciona primero un juego en Biblioteca para asociar su perfil." }
                TextField { id: profileReference; width: 1050; placeholderText: "Perfil INI existente (no se modifica)" }
                ActionButton { text: "Asociar perfil"; onClicked: settings.backend.associateControlProfile(settings.selectedGame,profileReference.text) }
                ActionButton { text: "Cerrar"; onClicked: dolphinSetup.close() }
            }
        }
        Popup { id: metadataEditor; x: 100; y: 20; width: 1100; height: 600; modal: true
            Column { spacing: 20; width: parent.width
                Label { text: "Propuesta local JSON. No es una búsqueda en Internet." }
                TextArea { id: proposal; width: 1000; height: 180; text: '{"description":"","genre":"","year":2026,"edition":"","source":"local"}' }
                ActionButton { text: "Revisar propuesta"; onClicked: review.text=settings.backend.proposeMetadata(settings.selectedGame,proposal.text) }
                TextArea { id: review; width: 1000; height: 150; readOnly: true }
                ActionButton { text: "Confirmar reemplazo"; onClicked: {settings.backend.confirmMetadata();metadataEditor.close()} }
            }
        }
        Popup { id: removal; x: 120; y: 150; width: 1000; height: 350; modal: true
            Column { spacing: 20
                Label { text: "Quitar referencia. Nunca se borrarán juegos ni partidas." }
                CheckBox { id: keepHistory; checked: true; text: "Conservar historial de sesiones" }
                ActionButton { text: "Confirmar retirada"; onClicked: {settings.backend.removeGame(settings.selectedGame,keepHistory.checked);removal.close()} }
                ActionButton { text: "Cancelar"; onClicked: removal.close() }
            }
        }
        ScrollView { x: 40; y: 220; width: 1200; height: 380; visible: settings.category===5
            TextArea { text: settings.backend.operationMessage+"\n\n"+settings.backend.diagnosticReport; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; font.pixelSize: 18 }
        }
        Text { x: 45; y: 500; width: 1200; text: settings.message; color: "#a8f3de"; font.pixelSize: 24; wrapMode: Text.WordWrap }
    }
}
