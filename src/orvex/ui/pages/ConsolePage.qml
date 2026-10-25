import QtQuick
import QtQuick.Controls
import "../components"
Item {
    id: consolePage
    property var backend
    property bool fromLibrary: false
    property int recentIndex: 0
    function enter() { viewport.contentY=0; if(recent.itemAt(0)) recent.itemAt(0).forceActiveFocus() }
    function restore() { if(fromLibrary) { viewport.contentY=900; library.restore() } else if(recent.itemAt(recentIndex)) recent.itemAt(recentIndex).forceActiveFocus() }
    Flickable {
        id: viewport; anchors.fill: parent; contentWidth: width; contentHeight: 1790; clip: true; boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
        Text { text: consolePage.backend.page===2?"PARA VER · CATÁLOGO DEMO":"RECIENTES · SESIONES DEMOSTRATIVAS"; color: "#a8f3de"; font.pixelSize: 18; font.letterSpacing: 3 }
        Flickable { id: strip; y: 48; width: parent.width; height: 305; contentWidth: carousel.width; clip: true; flickableDirection: Flickable.HorizontalFlick
            Row { id: carousel; spacing: 24
                Repeater { id: recent; model: consolePage.backend.showcase
                    MediaCard { required property var modelData; required property int index; width: 260; entry: modelData
                        onActiveFocusChanged: if(activeFocus) { consolePage.recentIndex=index;consolePage.backend.focusItem(modelData.id); strip.contentX=Math.max(0,Math.min(x,carousel.width-consolePage.width));viewport.contentY=0 }
                        onHoveredChanged: if(hovered)consolePage.backend.focusItem(modelData.id)
                        onActivated: {consolePage.recentIndex=index;consolePage.fromLibrary=false;consolePage.backend.openTitle(modelData.id)}
                        Keys.onDownPressed: {viewport.contentY=900;consolePage.fromLibrary=true;library.enter()}
                        Keys.onRightPressed: if(recent.itemAt(index+1))recent.itemAt(index+1).forceActiveFocus()
                        Keys.onLeftPressed: if(recent.itemAt(index-1))recent.itemAt(index-1).forceActiveFocus()
                    }
                }
            }
        }
        Text { objectName: "heroTitle"; y: 390; width: 1350; text: consolePage.backend.featured.title || "Explora tu colección"; color: "#f1f7f8"; font.pixelSize: 68; font.weight: Font.DemiBold; elide: Text.ElideRight }
        Text { y: 485; width: 1100; text: consolePage.backend.featured.description || ""; color: "#bdcdd8"; font.pixelSize: 25; wrapMode: Text.WordWrap }
        ProgressInfo { y: 590; width: 950; visible: !!consolePage.backend.featured.progress; record: consolePage.backend.featured.progress || ({}) }
        Text { y: 595; visible: consolePage.backend.page===2; text: (consolePage.backend.featured.platform || "")+" · "+(consolePage.backend.featured.age || 0)+"+ · Disponibilidad demostrativa"; color: "#a8f3de"; font.pixelSize: 25 }
        ActionButton { y: 745; width: 400; text: consolePage.backend.page===2?"Ver ficha · DEMO":"Continuar jugando · DEMO"; accent: true; enabled: !!consolePage.backend.featured.id; onClicked: {consolePage.fromLibrary=false;consolePage.backend.openTitle(consolePage.backend.featured.id)} }
        ActionButton { x: 435; y: 745; width: 400; text: "Biblioteca completa ↓"; onClicked: {viewport.contentY=900;consolePage.fromLibrary=true;library.enter()} }
        LibraryPage { id: library; y: 920; width: consolePage.width; height: 825; backend: consolePage.backend; onRequestReveal: {viewport.contentY=900;consolePage.fromLibrary=true} heading: consolePage.backend.page===2?"Biblioteca multimedia":"Biblioteca de videojuegos"; onActiveFocusChanged: if(activeFocus)consolePage.fromLibrary=true }
    }
    Connections { target: consolePage.backend; function onPageChanged(){viewport.contentY=0;consolePage.fromLibrary=false;consolePage.recentIndex=0} function onDetailChanged(){if(consolePage.backend.detailOpen && viewport.contentY>850)consolePage.fromLibrary=true} }
}
