import QtQuick
Rectangle {
    id: item
    property string label
    property bool selected: false
    property bool highlighted: false
    signal activated()
    width: 170; height: 58; radius: 29
    color: selected ? "#233b43" : "transparent"
    border.color: highlighted ? "#a8f3de" : "transparent"
    border.width: 2
    Text { anchors.centerIn: parent; text: item.label; color: selected ? "#b5f4e0" : "#a9b6c5"; font.pixelSize: 22; font.weight: Font.DemiBold }
    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: item.activated() }
}
