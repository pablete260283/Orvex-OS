import QtQuick
import QtQuick.Controls
import "../components"
Item {
    id: consolePage
    property var backend
    signal importRequested()
    signal headerRequested()
    property bool fromLibrary: false
    property int recentIndex: 0
    function enter() { restore() }
    function restore() {
        var items=backend.showcase
        var index=0
        for(var n=0;n<items.length;n++)if(items[n].id===backend.featured.id){index=n;break}
        recent.currentIndex=items.length?index:-1
        recent.positionViewAtIndex(index,ListView.Contain)
        if(recent.currentItem)recent.currentItem.forceActiveFocus()
        else headerRequested()
    }
    Text { objectName: "heroTitle"; y: 175; width: 1100; text: consolePage.backend.featured.title || (consolePage.backend.query?"Sin coincidencias":"Tu próxima partida empieza aquí"); color: "#f1f7f8"; font.pixelSize: 60; font.weight: Font.DemiBold; elide: Text.ElideRight }
    Text { y: 260; width: 850; maximumLineCount: 2; elide: Text.ElideRight; text: consolePage.backend.featured.description || (consolePage.backend.query?"Prueba otra búsqueda desde la lupa.":"Añade juegos desde Configuración → Biblioteca."); color: "#bdcdd8"; font.pixelSize: 22; wrapMode: Text.WordWrap }
    Text { y: 340; width: 1100; text: consolePage.backend.featured.platform || ""; color: "#c9d6dc"; font.pixelSize: 20 }
    Text { y: 400; visible: !!consolePage.backend.query; text: "Búsqueda: "+consolePage.backend.query+" · "+consolePage.backend.showcase.length+" resultados"; color: "#a8f3de"; font.pixelSize: 20; width: 1100; elide: Text.ElideRight }
    ListView {
        id: recent; objectName: "posterCarousel"; x: -16; y: 465; width: parent.width+32; height: 340
        orientation: ListView.Horizontal; spacing: 32; clip: true
        leftMargin: 32; rightMargin: 32; topMargin: 24
        model: consolePage.backend.showcase
        boundsBehavior: Flickable.StopAtBounds
        cacheBuffer: 520; reuseItems: true
        ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AlwaysOff }
        delegate: FocusScope {
            required property var modelData
            required property int index
            width: 174; height: 320
            PosterCard {
            focus: true
            objectName: "recent-"+modelData.id
            y: 24; entry: modelData; reduced: consolePage.backend.reducedMotion
            highlighted: activeFocus
            onActiveFocusChanged: if(activeFocus){consolePage.recentIndex=index;recent.currentIndex=index;consolePage.backend.focusItem(modelData.id)}
            onHoveredChanged: if(hovered)forceActiveFocus()
            onActivated: {consolePage.recentIndex=index;consolePage.backend.openTitle(modelData.id)}
            Keys.onRightPressed: {recent.incrementCurrentIndex();recent.positionViewAtIndex(recent.currentIndex,ListView.Contain);if(recent.currentItem)recent.currentItem.forceActiveFocus()}
            Keys.onLeftPressed: {recent.decrementCurrentIndex();recent.positionViewAtIndex(recent.currentIndex,ListView.Contain);if(recent.currentItem)recent.currentItem.forceActiveFocus()}
            Keys.onUpPressed: consolePage.headerRequested()
            Keys.onDownPressed: consolePage.headerRequested()
            }
        }
    }
    Connections {
        target: consolePage.backend
        function onLibraryChanged(){if(consolePage.visible && consolePage.enabled && !consolePage.backend.detailOpen && (recent.activeFocus || (recent.currentItem && recent.currentItem.activeFocus)))Qt.callLater(consolePage.restore)}
    }
}
