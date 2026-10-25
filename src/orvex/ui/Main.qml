import QtQuick
import QtQuick.Window
import "components"
Window {
    id: window
    width: 1440; height: 810; visible: true
    minimumWidth: 960; minimumHeight: 540
    title: "ORVEX 0.1 · Visual Preview"
    color: "#0b1320"
    property int page: 0
    property int zone: 0
    property int selected: 0
    property string notice: ""
    readonly property var entries: backend.catalog.filter(function(e) { return page === 2 ? e.kind === "media" : e.kind === "game" })
    function navigate(p) { page=p; selected=0; zone=0; notice=""; stage.forceActiveFocus() }
    function activate() {
        if (page === 3) { backend.toggleMotion(); return }
        notice = entries[selected].title + " · Demostración visual. La reproducción y el lanzamiento estarán disponibles en una próxima fase."
    }
    Item {
        id: stage
        width: 1920; height: 1080
        scale: Math.min(window.width/1920, window.height/1080)
        anchors.centerIn: parent
        focus: true
        Keys.onPressed: function(event) {
            if (window.notice !== "") {
                if ([Qt.Key_Escape, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space].indexOf(event.key) >= 0) window.notice=""
                event.accepted=true
                return
            }
            if (event.key === Qt.Key_Right || event.key === Qt.Key_Left) {
                var delta = event.key === Qt.Key_Right ? 1 : -1
                if (window.zone === 0) window.navigate((window.page+delta+4)%4)
                else window.selected=(window.selected+delta+window.entries.length)%window.entries.length
            } else if (event.key === Qt.Key_Down || event.key === Qt.Key_Tab) window.zone=1-window.zone
            else if (event.key === Qt.Key_Up) window.zone=0
            else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) { if(window.zone===1) window.activate(); else window.zone=1 }
            else if (event.key === Qt.Key_Escape) { if(window.notice) window.notice=""; else window.navigate(0) }
            else if (event.key === Qt.Key_F11) { window.visibility=window.visibility===Window.FullScreen ? Window.Windowed : Window.FullScreen }
            else { event.accepted=false; return }
            event.accepted=true
        }
        Rectangle { anchors.fill: parent; color: "#0b1320" }
        Text { x: 92; y: 55; text: "O R V E X"; color: "#eff9f6"; font.pixelSize: 31; font.weight: Font.Bold }
        Text { x: 94; y: 99; text: "ENTERTAINMENT OS"; color: "#7a939e"; font.pixelSize: 12; font.letterSpacing: 3 }
        Row { x: 560; y: 57; spacing: 12
            Repeater { model: ["Inicio", "Videojuegos", "Multimedia", "Configuración"]
                NavItem { required property int index; required property string modelData; width: index===3 ? 210 : 170; label: modelData; selected: window.page===index; highlighted: window.zone===0 && selected; onActivated: window.navigate(index) }
            }
        }
        Rectangle { x: 1622; y: 61; width: 196; height: 49; radius: 24; color: "#192632"
            Text { anchors.centerIn: parent; text: "P  /  Perfil demo"; color: "#c5d4df"; font.pixelSize: 18 }
        }
        Item { x: 92; y: 165; width: 1736; height: 505; visible: window.page!==3
            Rectangle { anchors.fill: parent; radius: 28; color: "#142a3a" }
            Image { anchors.fill: parent; source: "assets/"+(window.page===2 ? "ocean" : "aurora")+".svg"; fillMode: Image.PreserveAspectCrop }
            Rectangle { anchors.fill: parent; gradient: Gradient { orientation: Gradient.Horizontal; GradientStop { position: 0; color: "#ff0c1a26" } GradientStop { position: .55; color: "#c00c1a26" } GradientStop { position: 1; color: "#000c1a26" } } }
            Text { x: 48; y: 44; text: window.page===0 ? "TU ESPACIO. TU MOMENTO." : window.page===1 ? "BIBLIOTECA / VIDEOJUEGOS" : "BIBLIOTECA / MULTIMEDIA"; color: "#a8f3de"; font.pixelSize: 16; font.letterSpacing: 3 }
            Text { x: 44; y: 100; text: window.page===0 ? "Todo listo para
tu próxima aventura." : window.page===1 ? "Grandes mundos.
Un solo lugar." : "Historias que
te llevan más lejos."; color: "#f1f7f8"; font.pixelSize: 64; font.weight: Font.DemiBold; lineHeight: 1.08 }
            Text { x: 48; y: 278; text: window.page===2 ? "Películas, series y momentos para compartir." : "Tus juegos y entretenimiento, a tu manera."; color: "#b7c7d3"; font.pixelSize: 24 }
            Rectangle { x: 48; y: 348; width: 330; height: 62; radius: 31; color: "#a8f3de"
                Text { anchors.centerIn: parent; text: window.page===0 ? "Explorar biblioteca  →" : "Explorar títulos  ↓"; color: "#10262b"; font.pixelSize: 21; font.weight: Font.DemiBold }
                MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: { if(window.page===0) window.navigate(1); window.zone=1 } }
            }
            Text { x: 48; y: 449; text: "VISTA PREVIA 0.1    /    TODO EL CONTENIDO ES FICTICIO"; color: "#91a9b5"; font.pixelSize: 13; font.letterSpacing: 1.8 }
            Text { x: 1400; y: 425; text: window.page===2 ? "PLANETA AZUL" : "A U R O R A"; color: "#e0f7ef"; font.pixelSize: 26; font.letterSpacing: 3 }
        }
        Text { x: 94; y: 705; visible: window.page!==3; text: window.page===0 ? "Descubre tu próximo favorito" : window.page===1 ? "Todos tus videojuegos" : "Tu colección multimedia"; color: "#e5edf3"; font.pixelSize: 29; font.weight: Font.DemiBold }
        Text { x: 1575; y: 717; visible: window.page!==3; text: window.entries.length+" títulos de muestra"; color: "#8399ab"; font.pixelSize: 18 }
        Row { x: 92; y: 762; spacing: 44; visible: window.page!==3
            Repeater { model: window.entries
                MediaCard { required property var modelData; required property int index; entry: modelData; highlighted: window.zone===1 && window.selected===index; onActivated: { window.zone=1; window.selected=index; window.activate() } }
            }
        }
        Item { x: 94; y: 210; visible: window.page===3
            Text { text: "Hecho para tu forma de jugar."; color: "#eff5f9"; font.pixelSize: 58; font.weight: Font.DemiBold }
            Text { y: 90; text: "Configuración de la vista previa"; color: "#8ea5b8"; font.pixelSize: 24 }
            Rectangle { y: 180; width: 1730; height: 150; radius: 22; color: "#162331"; border.width: window.zone===1 ? 2 : 0; border.color: "#a8f3de"
                Text { x: 35; y: 32; text: "Reducir movimiento"; color: "#ecf5f9"; font.pixelSize: 28 }
                Text { x: 35; y: 85; text: "Preferencia guardada en este equipo. La interfaz 0.1 no incluye animaciones."; color: "#92a9bb"; font.pixelSize: 21 }
                Rectangle { x: 1530; y: 45; width: 135; height: 60; radius: 30; color: backend.reducedMotion ? "#a8f3de" : "#324351"; Text { anchors.centerIn: parent; text: backend.reducedMotion ? "Sí" : "No"; font.pixelSize: 23; color: "#0b1721" } }
                MouseArea { anchors.fill: parent; onClicked: backend.toggleMotion() }
            }
            Text { y: 410; text: "En las próximas fases"; color: "#e5edf3"; font.pixelSize: 29 }
            Repeater { model: ["Mandos y Bluetooth", "Audio y salidas múltiples", "Bibliotecas y almacenamiento"]
                Rectangle { required property string modelData; required property int index; x: index*585; y: 480; width: 555; height: 170; radius: 22; color: "#121f2e"
                    Text { x: 30; y: 35; text: modelData; color: "#c9d9e5"; font.pixelSize: 24 }
                    Text { x: 30; y: 105; text: "PENDIENTE DE INTEGRACIÓN"; color: "#7c94a8"; font.pixelSize: 15; font.letterSpacing: 1.5 }
                }
            }
        }
        Text { x: 94; y: 1044; text: "← → Navegar     ↓ Explorar     Enter Seleccionar     Esc Volver     F11 Pantalla completa"; color: "#7891a5"; font.pixelSize: 17 }
        Text { x: 1550; y: 1044; text: "0.1  /  VISUAL PREVIEW"; color: "#a8f3de"; font.pixelSize: 15; font.letterSpacing: 2 }
        Rectangle { anchors.fill: parent; visible: window.notice!==""; color: "#d908101c"
            MouseArea { anchors.fill: parent; onClicked: window.notice="" }
            Rectangle { anchors.centerIn: parent; width: 1000; height: 300; radius: 28; color: "#1b2c3c"; border.color: "#9ce7d4"
                Text { x: 45; y: 38; text: "Contenido de demostración"; color: "#a8f3de"; font.pixelSize: 30 }
                Text { x: 45; y: 100; width: 910; text: window.notice; wrapMode: Text.WordWrap; color: "#eff5f9"; font.pixelSize: 25 }
                Text { x: 45; y: 240; text: "Esc o clic para cerrar"; color: "#99afc0"; font.pixelSize: 20 }
            }
        }
    }
}
