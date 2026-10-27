import QtQuick
import "../components"
FocusScope {
    id: detailPage
    property var backend
    property var entry: backend.detail
    property string notice: ""
    signal artworkRequested(string gameId,string role)
    signal dismissed()
    visible: backend.detailOpen
    opacity: visible ? 1 : 0
    Behavior on opacity { NumberAnimation { duration: detailPage.backend.reducedMotion ? 0 : 120 } }
    onVisibleChanged: { notice=""; if(visible) play.forceActiveFocus(); else dismissed() }
    function close() { if(notice!=="") notice=""; else backend.closeDetail() }
    Rectangle { anchors.fill: parent; color: "#d90b1320" }
    ActionButton { id: back; objectName: "detailBack"; x: 92; y: 65; text: "← Volver"; onClicked: detailPage.backend.closeDetail(); KeyNavigation.tab: favorite; KeyNavigation.right: favorite; KeyNavigation.left: play; KeyNavigation.down: play; KeyNavigation.up: play; KeyNavigation.backtab: play }
    Text { x: 390; y: 82; text: entry.installed?"JUEGO LOCAL / EJECUTABLE IMPORTADO":"FICHA / CONTENIDO DE DEMOSTRACIÓN"; color: "#a8f3de"; font.pixelSize: 20; font.letterSpacing: 2 }
    Image { x: 92; y: 210; width: 700; height: 550; source: entry.cover_url || ""; fillMode: Image.PreserveAspectFit }
    Text { x: 850; y: 215; width: 970; text: entry.title || ""; color: "#f0f5f9"; height: 130; maximumLineCount: 2; elide: Text.ElideRight; font.pixelSize: 52; font.weight: Font.DemiBold; wrapMode: Text.WordWrap }
    Text { x: 855; y: 365; width: 965; text: (entry.platform || "")+"  ·  "+((entry.age===undefined || entry.age===null)?"Edad no verificada":entry.age===0 ? "General" : (entry.age || "")+"+"); color: "#a8f3de"; font.pixelSize: 27 }
    Text { x: 855; y: 420; width: 920; text: entry.description || ""; height: 145; maximumLineCount: 3; elide: Text.ElideRight; wrapMode: Text.WordWrap; color: "#bbcdd9"; font.pixelSize: 28; lineHeight: 1.4 }
    Text { x: 855; y: 580; width: 930; height: 55; maximumLineCount: 2; elide: Text.ElideRight; text: entry.installed?"":entry.availability || ""; wrapMode: Text.WrapAnywhere; color: "#91a9bb"; font.pixelSize: 22 }
    ProgressInfo { x: 855; y: 800; width: 930; visible: false; record: entry.progress || ({}) }
    ActionButton { id: play; objectName: "demoPlay"; x: 855; y: 700; width: 350; accent: true; text: entry.installed?(backend.launchBusy?"En ejecución":"Jugar"):entry.kind==="game" ? "Jugar · DEMO" : "Ver · DEMO"; enabled: !entry.installed || !backend.launchBusy; onClicked: {if(entry.installed)backend.requestLaunch(entry.id);else detailPage.notice="Demostración: no hay un lanzador ni un reproductor conectado."} KeyNavigation.tab: back; KeyNavigation.right: back; KeyNavigation.left: favorite; KeyNavigation.down: back; KeyNavigation.up: back; KeyNavigation.backtab: favorite }
    ActionButton { id: favorite; objectName: "detailFavorite"; x: 1235; y: 700; width: 550; text: entry.favorite ? "♥ Quitar de favoritos" : "♡ Agregar a favoritos"; onClicked: detailPage.backend.toggleFavorite(entry.id); KeyNavigation.tab: play; KeyNavigation.right: play; KeyNavigation.left: back; KeyNavigation.down: play; KeyNavigation.up: play; KeyNavigation.backtab: back }
    Text { x: 855; y: 650; width: 940; text: entry.installed?(backend.launchState==="Error"?"No se pudo completar el lanzamiento. Consulta Configuración → Sistema.":backend.controllerNotice):detailPage.notice; wrapMode: Text.WordWrap; color: "#a8f3de"; font.pixelSize: 20 }
    ActionButton { visible: false; x: 92; y: 800; width: 330; text: "Asociar carátula…"; onClicked: detailPage.artworkRequested(entry.id,"cover") }
    ActionButton { visible: false; x: 450; y: 800; width: 330; text: "Asociar fondo…"; onClicked: detailPage.artworkRequested(entry.id,"backdrop") }
    Text { x: 92; y: 970; text: "ORVEX OS 0.4 · "+backend.profileLabel+" · Perfiles demostrativos sin PIN"; color: "#8fa7b9"; font.pixelSize: 22 }
}
