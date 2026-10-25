import QtQuick
import QtQuick.Controls
AbstractButton {
    id: card
    required property var entry
    property bool highlighted: activeFocus || hovered
    signal activated()
    hoverEnabled: true
    width: 400; height: 284; focusPolicy: Qt.StrongFocus
    background: Rectangle { radius: 19; color: "#14202e"; border.color: card.highlighted ? "#a8f3de" : "#263445"; border.width: card.highlighted ? 3 : 1 }
    contentItem: Item {
        Image { x: 7; y: 7; width: card.width-14; height: 168; source: entry.cover_url || ""; fillMode: Image.PreserveAspectCrop }
        Rectangle { x: 20; y: 20; width: 65; height: 25; radius: 6; color: "#bd0b1621"; Text { anchors.centerIn: parent; text: "DEMO"; color: "#d3e2ed"; font.pixelSize: 12; font.letterSpacing: 1.5 } }
        Text { x: 20; y: 190; width: card.width-40; text: (entry.favorite ? "♥  " : "")+entry.title; color: "#eff5f9"; font.pixelSize: 23; font.weight: Font.DemiBold; elide: Text.ElideRight }
        Text { x: 20; y: 228; width: card.width-40; text: entry.platform+"  ·  "+(entry.age===0 ? "General" : entry.age+"+"); color: "#91a3b4"; font.pixelSize: 17; elide: Text.ElideRight }
        Text { x: 20; y: 255; width: card.width-40; elide: Text.ElideRight; text: entry.progress ? "DEMO · "+entry.progress.percentLabel : "Abrir ficha  →"; color: "#a8f3de"; font.pixelSize: 15 }
    }
    onClicked: activated()
}
