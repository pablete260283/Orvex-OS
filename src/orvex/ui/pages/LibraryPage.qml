import QtQuick
import QtQuick.Controls
import "../components"
Item {
    id: library
    property var backend
    property string heading
    signal requestReveal()
    opacity: visible ? 1 : 0
    Behavior on opacity { NumberAnimation { duration: library.backend.reducedMotion ? 0 : 120 } }
    function enter() { search.forceActiveFocus() }
    function restore() { grid.forceActiveFocus(); if(grid.currentItem) grid.currentItem.forceActiveFocus() }
    Text { text: heading; color: "#edf5f8"; font.pixelSize: 46; font.weight: Font.DemiBold }
    Text { y: 65; text: library.backend.page===1 && library.backend.librarySource==="real"?"Ejecutables importados · Biblioteca personal en SQLite":"Catálogo ficticio · Explora, guarda y descubre"; color: "#8fa7b9"; font.pixelSize: 23 }
    TextField {
        id: search; onActiveFocusChanged: if(activeFocus)library.requestReveal(); objectName: "librarySearch"; x: 0; y: 120; width: 610; height: 62
        placeholderTextColor: "#91a9bb"; leftPadding: 20; placeholderText: "Buscar por nombre…"; text: library.backend.query; font.pixelSize: 23; color: "#eff5f9"; selectByMouse: true
        background: Rectangle { radius: 16; color: "#142333"; border.width: search.activeFocus ? 3 : 1; border.color: search.activeFocus ? "#a8f3de" : "#304453" }
        onTextEdited: library.backend.setQuery(text)
        Keys.onDownPressed: library.restore()
        onAccepted: library.restore()
    }
    ComboBox {
        id: filter; onActiveFocusChanged: if(activeFocus)library.requestReveal(); objectName: "libraryFilter"; x: 640; y: 120; width: 410; height: 62
        model: library.backend.options; currentIndex: Math.max(0,model.indexOf(library.backend.category)); font.pixelSize: 21
        onActivated: library.backend.setCategory(currentText)
        background: Rectangle { radius: 16; color: "#203544"; border.width: filter.activeFocus ? 3 : 1; border.color: filter.activeFocus ? "#a8f3de" : "#304453" }
        contentItem: Text { leftPadding: 20; text: filter.displayText; color: "#edf5f8"; font.pixelSize: 21; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
    }
    ActionButton { objectName: "favoritesFilter"; x: 1080; y: 120; width: 290; text: library.backend.favoritesOnly ? "♥ Solo favoritos" : "♡ Todos los títulos"; selected: library.backend.favoritesOnly; onClicked: library.backend.toggleFavorites() }
    ActionButton { x: 1400; y: 120; width: 330; text: "Limpiar filtros"; onClicked: library.backend.clearFilters() }
    Text { y: 215; text: library.backend.entries.length+" títulos · "+library.backend.profileLabel+" (demo)"; color: "#8fa7b9"; font.pixelSize: 21 }
    GridView {
        id: grid; objectName: "libraryGrid"; x: 0; y: 270; width: parent.width; height: parent.height-270
        cellWidth: 434; cellHeight: 325; clip: true; model: library.backend.entries
        currentIndex: library.backend.selectedIndex; keyNavigationEnabled: false; activeFocusOnTab: true
        delegate: MediaCard {
            required property var modelData; required property int index
            entry: modelData; onActiveFocusChanged: if(activeFocus) {library.requestReveal();library.backend.focusItem(modelData.id)} onHoveredChanged: if(hovered)library.backend.focusItem(modelData.id); highlighted: GridView.isCurrentItem && grid.activeFocus
            onActivated: library.backend.openDetail(index)
            Keys.onPressed: function(event) {
                if(event.key===Qt.Key_Right) library.backend.selectIndex(Math.min(grid.count-1,index+1))
                else if(event.key===Qt.Key_Left) library.backend.selectIndex(Math.max(0,index-1))
                else if(event.key===Qt.Key_Down) library.backend.selectIndex(Math.min(grid.count-1,index+4))
                else if(event.key===Qt.Key_Up) { if(index<4) { search.forceActiveFocus(); return } else library.backend.selectIndex(index-4) }
                else {event.accepted=false;return}
                event.accepted=true; if(grid.currentItem)grid.currentItem.forceActiveFocus()
            }
        }
        Keys.onReturnPressed: if(grid.count>0) library.backend.openDetail(currentIndex)
        Keys.onPressed: function(event) {
            var index=library.backend.selectedIndex
            if(event.key===Qt.Key_Right) library.backend.selectIndex(Math.min(grid.count-1,index+1))
            else if(event.key===Qt.Key_Left) library.backend.selectIndex(Math.max(0,index-1))
            else if(event.key===Qt.Key_Down) library.backend.selectIndex(Math.min(grid.count-1,index+4))
            else if(event.key===Qt.Key_Up) { if(index<4) search.forceActiveFocus(); else library.backend.selectIndex(index-4) }
            else {event.accepted=false;return}
            event.accepted=true
        }
        Text { visible: grid.count===0; anchors.centerIn: parent; text: "No hay títulos con estos filtros.
Prueba otra búsqueda o limpia los filtros."; horizontalAlignment: Text.AlignHCenter; color: "#a5bac9"; font.pixelSize: 28 }
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
    }
}
