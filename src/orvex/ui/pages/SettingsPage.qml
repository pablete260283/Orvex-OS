import QtQuick
import "../components"
Item {
    id: settings
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
        Text { x: 45; y: 115; width: 1220; text: settings.category===0 ? "FUNCIONAL · Preferencias guardadas en SQLite" : settings.category===3 ? "FUNCIONAL · Filtros y favoritos por perfil" : settings.category===4 ? "DEMO · Filtro infantil hasta 7+. Sin autenticación ni PIN.
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
        ActionButton { x: 45; y: 300; width: 650; visible: settings.category===0; text: "Reducir movimiento: "+(settings.backend.reducedMotion ? "Sí" : "No"); onClicked: settings.backend.toggleMotion() }
        ActionButton { x: 45; y: 300; width: 650; visible: settings.category===3; text: "Limpiar filtros de las bibliotecas"; onClicked: {settings.backend.clearFilters();settings.message="Filtros restablecidos. Tus favoritos se conservan."} }
        Row { x: 45; y: 330; spacing: 30; visible: settings.category===4
            ActionButton { width: 350; text: "Adulto · demo"; selected: settings.backend.profile==="adult"; onClicked: settings.backend.setProfile("adult") }
            ActionButton { width: 350; text: "Infantil · demo"; selected: settings.backend.profile==="child"; onClicked: settings.backend.setProfile("child") }
        }
        Text { x: 45; y: 500; width: 1200; text: settings.message; color: "#a8f3de"; font.pixelSize: 24; wrapMode: Text.WordWrap }
    }
}
