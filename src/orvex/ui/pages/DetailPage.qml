import QtQuick
import "../components"
FocusScope {
    id: detailPage
    property var backend
    property var entry: backend.detail
    property string notice: ""
    signal dismissed()
    visible: backend.detailOpen
    opacity: visible ? 1 : 0
    Behavior on opacity { NumberAnimation { duration: detailPage.backend.reducedMotion ? 0 : 120 } }
    onVisibleChanged: { notice=""; if(visible) back.forceActiveFocus(); else dismissed() }
    function close() { if(notice!=="") notice=""; else backend.closeDetail() }
    Rectangle { anchors.fill: parent; color: "#0b1320" }
    ActionButton { id: back; objectName: "detailBack"; x: 92; y: 65; text: "← Volver"; onClicked: detailPage.backend.closeDetail(); KeyNavigation.tab: favorite; KeyNavigation.right: favorite; KeyNavigation.backtab: play }
    Text { x: 390; y: 82; text: "FICHA / CONTENIDO DE DEMOSTRACIÓN"; color: "#a8f3de"; font.pixelSize: 20; font.letterSpacing: 2 }
    Image { x: 92; y: 210; width: 700; height: 550; source: entry.art ? "../assets/"+entry.art+".svg" : ""; fillMode: Image.PreserveAspectCrop }
    Text { x: 850; y: 215; width: 970; text: entry.title || ""; color: "#f0f5f9"; font.pixelSize: 64; font.weight: Font.DemiBold; wrapMode: Text.WordWrap }
    Text { x: 855; y: 330; width: 965; text: (entry.platform || "")+"  ·  "+(entry.age===0 ? "General" : (entry.age || "")+"+"); color: "#a8f3de"; font.pixelSize: 27 }
    Text { x: 855; y: 400; width: 920; text: entry.description || ""; wrapMode: Text.WordWrap; color: "#bbcdd9"; font.pixelSize: 28; lineHeight: 1.4 }
    Text { x: 855; y: 595; width: 930; text: entry.availability || ""; wrapMode: Text.WordWrap; color: "#91a9bb"; font.pixelSize: 22 }
    ActionButton { id: play; objectName: "demoPlay"; x: 855; y: 700; width: 350; accent: true; text: entry.kind==="game" ? "Jugar · DEMO" : "Ver · DEMO"; onClicked: detailPage.notice="Demostración: no hay un lanzador ni un reproductor conectado."; KeyNavigation.tab: back; KeyNavigation.right: back; KeyNavigation.backtab: favorite }
    ActionButton { id: favorite; objectName: "detailFavorite"; x: 1235; y: 700; width: 550; text: entry.favorite ? "♥ Quitar de favoritos" : "♡ Agregar a favoritos"; onClicked: detailPage.backend.toggleFavorite(entry.id); KeyNavigation.tab: play; KeyNavigation.right: play; KeyNavigation.backtab: back }
    Text { x: 855; y: 805; width: 940; text: detailPage.notice; wrapMode: Text.WordWrap; color: "#a8f3de"; font.pixelSize: 24 }
    Text { x: 92; y: 970; text: "ORVEX OS 0.2 · "+backend.profileLabel+" · Perfiles demostrativos sin PIN"; color: "#8fa7b9"; font.pixelSize: 22 }
}
