import QtQuick
Rectangle {
    id: card
    required property var entry
    property bool highlighted: false
    signal activated()
    width: 400; height: 258; radius: 19
    color: "#14202e"
    border.color: highlighted ? "#a8f3de" : "#263445"
    border.width: highlighted ? 3 : 1
    Image { x: 7; y: 7; width: parent.width-14; height: 168; source: "../assets/"+entry.id+".svg"; fillMode: Image.PreserveAspectCrop }
    Rectangle { x: 20; y: 20; width: 65; height: 25; radius: 6; color: "#bd0b1621"
        Text { anchors.centerIn: parent; text: "DEMO"; color: "#d3e2ed"; font.pixelSize: 12; font.letterSpacing: 1.5 }
    }
    Text { x: 20; y: 190; text: entry.title; color: "#eff5f9"; font.pixelSize: 23; font.weight: Font.DemiBold }
    Text { x: 20; y: 225; text: entry.platform; color: "#91a3b4"; font.pixelSize: 17 }
    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: card.activated() }
}
