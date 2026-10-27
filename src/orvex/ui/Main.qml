import QtQuick
import QtQuick.Window
import QtQuick.Controls
import "components"
import "pages"
Window {
    id: window
    width: 1440; height: 810; minimumWidth: 960; minimumHeight: 540; visible: true
    title: "ORVEX OS 0.4 · Biblioteca local"; color: "#0b1320"
    onActiveChanged: if(active && !backend.launchBusy)backend.refresh()
    onClosing: function(close) { if(backend.launchBusy){close.accepted=false;backend.explainClose()} }
    property bool wasGameRunning: false
    Connections { target: backend
        function onOperationChanged() {
            if(window.wasGameRunning && !backend.launchBusy){
                window.requestActivate()
                if(!backend.detailOpen && (backend.page===1 || backend.page===2))Qt.callLater(library.restore)
            }
            window.wasGameRunning=backend.launchBusy
        }
    }
    readonly property int page: backend.page
    readonly property bool brandReady: brandLogo.status===Image.Ready
    function openImport(){localDialogs.openImport()}
    function navigate(p) { backend.navigate(p); if(nav.itemAt(p-1)) nav.itemAt(p-1).forceActiveFocus() }
    function enter() { if(page===1 || page===2) library.enter(); else if(page===3) settings.enter();  }
    function focusNext(forward) { var item=window.activeFocusItem; if(item) item.nextItemInFocusChain(forward).forceActiveFocus(Qt.TabFocusReason) }
    Shortcut { sequence: "Escape"; onActivated: { if(searchOverlay.opened)searchOverlay.cancel();else if(backend.pendingLaunch.id)backend.cancelLaunch();else if(backend.pendingArtwork.id)backend.cancelArtwork();else if(backend.detailOpen) detail.close(); else window.navigate(1) } }
    Shortcut { sequence: "F11"; onActivated: window.visibility=window.visibility===Window.FullScreen ? Window.Windowed : Window.FullScreen }
    Item {
        id: stage; width: 1920; height: 1080; anchors.centerIn: parent; scale: Math.min(window.width/1920,window.height/1080)
        Keys.onPressed: function(event) {
            if(searchOverlay.opened){event.accepted=false;return}
            if(event.key===Qt.Key_Down && (window.activeFocusItem===searchButton || window.activeFocusItem===profileButton || window.activeFocusItem===settingsButton)){library.enter();event.accepted=true;return}

            if(event.key===Qt.Key_Right || event.key===Qt.Key_Down) window.focusNext(true)
            else if(event.key===Qt.Key_Left || event.key===Qt.Key_Up) window.focusNext(false)
            else { event.accepted=false; return }
            event.accepted=true
        }
        Rectangle { anchors.fill: parent; color: "#0b1320" }
        DynamicBackground { anchors.fill: parent; art: backend.backgroundUrl; reduced: backend.reducedMotion; profile: backend.profile }
        Item { id: shell; anchors.fill: parent; enabled: !backend.detailOpen; visible: !backend.detailOpen
            Image { id: brandLogo; objectName: "brandLogo"; x: 92; y: 42; width: 350; height: 350*165/610; source: "assets/brand/svg/orvex-horizontal-dark.svg"; sourceSize: Qt.size(1220,330); fillMode: Image.PreserveAspectFit; onStatusChanged: if(status===Image.Error && source.toString().endsWith(".svg")) source="assets/brand/png/orvex-horizontal-dark-4x.png" }
            Row { x: 600; y: 57; spacing: 24
                Repeater { id: nav; model: ["Videojuegos","Multimedia"]
                    NavItem { required property int index; required property string modelData; objectName: "nav"+(index+1); width: 220; label: modelData; selected: backend.page===index+1; onActivated: window.navigate(index+1)
                        Keys.onRightPressed: {if(index===0)window.navigate(2);else searchButton.forceActiveFocus()}
                        Keys.onLeftPressed: {if(index===1)window.navigate(1);else settingsButton.forceActiveFocus()}
                        Keys.onDownPressed: library.enter()
                    }
                }
            }
            ActionButton { id: profileButton; Keys.onRightPressed: settingsButton.forceActiveFocus(); Keys.onLeftPressed: searchButton.forceActiveFocus(); background: Item {} objectName: "profileButton"; x: 1620; y: 57; width: 90; text: ""; contentItem: Item { Image { anchors.centerIn: parent; width: 32; height: 32; source: "assets/profile.svg"; fillMode: Image.PreserveAspectFit; sourceSize: Qt.size(128,128) } } Accessible.name: "Perfil "+backend.profileLabel; onClicked: profileMenu.open() }
            ActionButton { id: settingsButton; Keys.onRightPressed: nav.itemAt(0).forceActiveFocus(); Keys.onLeftPressed: profileButton.forceActiveFocus(); objectName: "settingsButton"; background: Item {} x: 1730; y: 57; width: 90; text: ""; contentItem: Item { Image { anchors.centerIn: parent; width: 32; height: 32; source: "assets/gear.svg"; fillMode: Image.PreserveAspectFit; sourceSize: Qt.size(128,128) } } Accessible.name: "Configuración"; onClicked: window.navigate(3) }
            ActionButton { id: searchButton; Keys.onRightPressed: profileButton.forceActiveFocus(); Keys.onLeftPressed: nav.itemAt(1).forceActiveFocus(); objectName: "searchButton"; x: 1510; y: 57; width: 90; text: ""; contentItem: Item { Image { anchors.centerIn: parent; width: 32; height: 32; source: "assets/search.svg"; fillMode: Image.PreserveAspectFit; sourceSize: Qt.size(128,128) } } background: Item {} Accessible.name: "Buscar"; onClicked: searchOverlay.begin() }
            Rectangle { x: searchButton.activeFocus?1510:profileButton.activeFocus?1620:1730; y: 122; width: 90; height: 4; radius: 2; color: "#a8f3de"; visible: searchButton.activeFocus || profileButton.activeFocus || settingsButton.activeFocus }
            SearchOverlay { id: searchOverlay; backend: shellBackend; onFinished: Qt.callLater(library.restore) }
            Popup { id: profileMenu; onOpened: adultChoice.forceActiveFocus(); onClosed: {if(backend.page===1 || backend.page===2)library.restore();else profileButton.forceActiveFocus()} x: 1450; y: 135; width: 370; height: 240; padding: 18; modal: true; focus: true
                background: Rectangle { color: "#142333"; radius: 18; border.color: "#a8f3de" }
                Column { spacing: 14
                    Text { text: "PERFIL · DEMO SIN PIN"; color: "#a8f3de"; font.pixelSize: 19 }
                    ActionButton { id: adultChoice; KeyNavigation.down: childChoice; KeyNavigation.up: childChoice; width: 330; text: "Adulto"; selected: backend.profile==="adult"; onClicked: {backend.setProfile("adult");profileMenu.close()} }
                    ActionButton { id: childChoice; KeyNavigation.down: adultChoice; KeyNavigation.up: adultChoice; objectName: "childProfileChoice"; width: 330; text: "Infantil"; selected: backend.profile==="child"; onClicked: {backend.setProfile("child");profileMenu.close()} }
                }
            }
            ConsolePage { onHeaderRequested: searchButton.forceActiveFocus(); onImportRequested: localDialogs.openImport(); id: library; objectName: "consolePage"; enabled: !searchOverlay.opened; x: 92; y: 180; width: 1736; height: 825; visible: backend.page===1 || backend.page===2; backend: shellBackend }
            Text { x: 92; y: 145; width: 1736; text: backend.launchState==="Error"?"No se pudo completar la operación. Consulta Configuración → Sistema.":""; color: "#a8f3de"; font.pixelSize: 18; elide: Text.ElideRight }
            SettingsPage { onImportRequested: localDialogs.openImport(); onArtworkRequested: function(gameId,role){localDialogs.selectArtwork(gameId,role)} id: settings; x: 92; y: 180; width: 1736; height: 825; visible: backend.page===3; backend: shellBackend }
            Text { x: 94; y: 1042; text: "Navegar · Confirmar: abrir · Volver: regresar"; color: "#7891a5"; font.pixelSize: 17 }
            Text { x: 1120; y: 1042; text: "0.4 · Biblioteca local · Perfiles sin PIN"; color: "#a8f3de"; font.pixelSize: 17 }
        }
        LocalLibraryDialogs { id: localDialogs; anchors.fill: parent; backend: shellBackend }
        DetailPage { onArtworkRequested: function(gameId,role){localDialogs.selectArtwork(gameId,role)} id: detail; objectName: "detailPage"; anchors.fill: parent; backend: shellBackend; onDismissed: {if(backend.page===1 || backend.page===2)library.restore();else if(nav.itemAt(backend.page-1)) nav.itemAt(backend.page-1).forceActiveFocus()} }
    }
    property var shellBackend: backend
    Component.onCompleted: Qt.callLater(function() {library.enter()})
}
