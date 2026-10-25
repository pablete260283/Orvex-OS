import QtQuick
import QtQuick.Window
import "components"
import "pages"
Window {
    id: window
    width: 1440; height: 810; minimumWidth: 960; minimumHeight: 540; visible: true
    title: "ORVEX OS 0.2 · Visual Preview"; color: "#0b1320"
    readonly property int page: backend.page
    readonly property bool brandReady: brandLogo.status===Image.Ready
    function navigate(p) { backend.navigate(p); if(nav.itemAt(p)) nav.itemAt(p).forceActiveFocus() }
    function enter() { if(page===1 || page===2) library.enter(); else if(page===3) settings.enter(); else explore.forceActiveFocus() }
    function focusNext(forward) { var item=window.activeFocusItem; if(item) item.nextItemInFocusChain(forward).forceActiveFocus(Qt.TabFocusReason) }
    Shortcut { sequence: "Escape"; onActivated: { if(backend.detailOpen) detail.close(); else window.navigate(0) } }
    Shortcut { sequence: "F11"; onActivated: window.visibility=window.visibility===Window.FullScreen ? Window.Windowed : Window.FullScreen }
    Item {
        id: stage; width: 1920; height: 1080; anchors.centerIn: parent; scale: Math.min(window.width/1920,window.height/1080)
        Keys.onPressed: function(event) {
            if(event.key===Qt.Key_Right || event.key===Qt.Key_Down) window.focusNext(true)
            else if(event.key===Qt.Key_Left || event.key===Qt.Key_Up) window.focusNext(false)
            else { event.accepted=false; return }
            event.accepted=true
        }
        Rectangle { anchors.fill: parent; color: "#0b1320" }
        DynamicBackground { anchors.fill: parent; art: backend.backgroundArt; reduced: backend.reducedMotion; profile: backend.profile }
        Item { id: shell; anchors.fill: parent; enabled: !backend.detailOpen; visible: !backend.detailOpen
            Image { id: brandLogo; objectName: "brandLogo"; x: 92; y: 42; width: 350; height: 350*165/610; source: "assets/brand/svg/orvex-horizontal-dark.svg"; sourceSize: Qt.size(1220,330); fillMode: Image.PreserveAspectFit; onStatusChanged: if(status===Image.Error && source.toString().endsWith(".svg")) source="assets/brand/png/orvex-horizontal-dark-4x.png" }
            Row { x: 560; y: 57; spacing: 12
                Repeater { id: nav; model: ["Inicio","Videojuegos","Multimedia","Configuración"]
                    NavItem { required property int index; required property string modelData; width: index===3 ? 210 : 170; label: modelData; selected: backend.page===index; onActivated: window.navigate(index)
                        Keys.onRightPressed: window.navigate((index+1)%4)
                        Keys.onLeftPressed: window.navigate((index+3)%4)
                        Keys.onDownPressed: window.enter()
                    }
                }
            }
            ActionButton { id: profileButton; objectName: "profileButton"; x: 1538; y: 57; width: 290; text: backend.profileLabel+" · demo ⇄"; onClicked: backend.setProfile(backend.profile==="adult" ? "child" : "adult") }
            Item { id: home; x: 92; y: 165; width: 1736; height: 860; visible: backend.page===0
                opacity: visible ? 1 : 0
                Behavior on opacity { NumberAnimation { duration: backend.reducedMotion ? 0 : 120 } }

                Rectangle { width: 1736; height: 450; gradient: Gradient { orientation: Gradient.Horizontal; GradientStop {position:0;color:"#ff0c1a26"} GradientStop {position:1;color:"#000c1a26"} } }
                Text { x: 48; y: 44; text: "CONTINUAR JUGANDO · DATOS DEMO"; color: "#a8f3de"; font.pixelSize: 17; font.letterSpacing: 3 }
                Text { objectName: "heroTitle"; x: 44; y: 98; text: backend.featured.title || "Tu próxima aventura"; color: "#f1f7f8"; font.pixelSize: 64; font.weight: Font.DemiBold }
                Text { x: 48; y: 310; visible: false; text: backend.featured.progress ? backend.featured.progress.statusLabel+" · "+backend.featured.progress.percentLabel : "Explora tu biblioteca"; color: "#b7c7d3"; font.pixelSize: 24 }
                ActionButton { id: explore; x: 48; y: 340; width: 350; text: "Explorar biblioteca →"; accent: true; onClicked: {window.navigate(1);library.enter()} }
                ProgressInfo { x: 48; y: 190; width: 1000; visible: !!backend.featured.progress; record: backend.featured.progress || ({}) }
                ActionButton { x: 430; y: 340; width: 350; text: "Continuar · DEMO"; onClicked: {for(var i=0;i<backend.entries.length;i++)if(backend.entries[i].id===backend.featured.id){backend.openDetail(i);break}} }
                Text { y: 493; text: "Continuar jugando · Sesiones demostrativas"; color: "#e5edf3"; font.pixelSize: 29; font.weight: Font.DemiBold }
                Row { y: 550; spacing: 44
                    Repeater { model: backend.page===0 ? backend.entries : []
                        MediaCard { required property var modelData; required property int index; entry: modelData; onActiveFocusChanged: if(activeFocus)backend.focusItem(modelData.id); onHoveredChanged: if(hovered)backend.focusItem(modelData.id); onActivated: backend.openDetail(index) }
                    }
                }
            }
            LibraryPage { id: library; objectName: "libraryPage"; x: 92; y: 180; width: 1736; height: 825; visible: backend.page===1 || backend.page===2; backend: shellBackend; heading: shellBackend.page===2 ? "Tu colección multimedia" : "Todos tus videojuegos" }
            SettingsPage { id: settings; x: 92; y: 180; width: 1736; height: 825; visible: backend.page===3; backend: shellBackend }
            Text { x: 94; y: 1042; text: "Flechas / Tab Navegar    Enter Elegir    Esc Volver    F11 Pantalla completa"; color: "#7891a5"; font.pixelSize: 17 }
            Text { x: 1240; y: 1042; text: "0.2 DEMO · Perfiles sin PIN ni protección real"; color: "#a8f3de"; font.pixelSize: 17 }
        }
        DetailPage { id: detail; objectName: "detailPage"; anchors.fill: parent; backend: shellBackend; onDismissed: {if(backend.page===1 || backend.page===2)library.restore();else if(nav.itemAt(backend.page)) nav.itemAt(backend.page).forceActiveFocus()} }
    }
    property var shellBackend: backend
    Component.onCompleted: Qt.callLater(function() {if(nav.itemAt(0))nav.itemAt(0).forceActiveFocus()})
}
