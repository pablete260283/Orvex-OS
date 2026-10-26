import QtQuick
import QtQuick.Controls
AbstractButton {
    id: card
    required property var entry
    property bool reduced: false
    property bool highlighted: activeFocus || hovered
    signal activated()
    objectName: "poster-" + entry.id
    width: 174; height: 261
    hoverEnabled: true
    focusPolicy: Qt.StrongFocus
    scale: highlighted ? 1.10 : 1
    z: highlighted ? 2 : 1
    Behavior on scale { NumberAnimation { duration: card.reduced ? 0 : 140 } }
    Accessible.name: entry.title || "Juego"
    Accessible.description: "Abrir ficha. Flechas para elegir; abajo para biblioteca."
    background: Rectangle {
        anchors.fill: parent; anchors.margins: -5
        color: "#dd111923"; radius: 14
        border.width: card.highlighted ? 3 : 0
        border.color: "#8ce9d5"
    }
    contentItem: Item {
        Image {
            id: cover; anchors.fill: parent
            source: card.entry.cover_url || ""
            fillMode: Image.PreserveAspectFit
            asynchronous: true
            sourceSize: Qt.size(696,1044)
        }
        Text {
            anchors.centerIn: parent; width: parent.width-24
            visible: cover.status!==Image.Ready
            text: card.entry.title || "Sin carátula"
            color: "#eaf4f4"; font.pixelSize: 22
            horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
        }
    }
    onClicked: activated()
    Keys.onReturnPressed: activated()
    Keys.onEnterPressed: activated()
}
