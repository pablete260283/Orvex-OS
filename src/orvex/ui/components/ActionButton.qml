import QtQuick
import QtQuick.Controls
Button {
    id: control
    property bool accent: false
    property bool selected: false
    Keys.onReturnPressed: if(enabled)control.clicked()
    Keys.onEnterPressed: if(enabled)control.clicked()
    opacity: enabled ? 1 : 0.5
    Accessible.name: text
    ToolTip.visible: hovered && contentItem.truncated === true
    ToolTip.text: text
    focusPolicy: Qt.StrongFocus
    implicitWidth: Math.max(250,contentItem.implicitWidth+48); implicitHeight: 60
    background: Rectangle { radius: 16; color: control.accent ? "#a8f3de" : control.selected ? "#29424a" : "#1a2a39"; border.color: control.activeFocus ? "#e1fff7" : "#314957"; border.width: control.activeFocus ? 3 : 1 }
    contentItem: Text { text: control.text; color: control.accent ? "#10262b" : "#e3eef4"; font.pixelSize: 22; font.weight: Font.DemiBold; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
}
