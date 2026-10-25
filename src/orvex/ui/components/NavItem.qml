import QtQuick
import QtQuick.Controls
AbstractButton {
    id: item
    property string label
    property bool selected: false
    property bool highlighted: activeFocus
    signal activated()
    width: 170; height: 58; focusPolicy: Qt.StrongFocus
    background: Rectangle { radius: 29; color: item.selected ? "#233b43" : "transparent"; border.color: item.highlighted ? "#a8f3de" : "transparent"; border.width: 2 }
    contentItem: Text { text: item.label; color: item.selected ? "#b5f4e0" : "#a9b6c5"; font.pixelSize: 22; font.weight: Font.DemiBold; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
    onClicked: activated()
}
