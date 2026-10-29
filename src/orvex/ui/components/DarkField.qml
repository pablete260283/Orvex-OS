import QtQuick
import QtQuick.Controls
import QtQuick.Window
TextField {
    id: field
    implicitHeight: 60
    font.pixelSize: 23
    selectByMouse: true
    focusPolicy: Qt.StrongFocus
    Accessible.name: placeholderText
    Keys.onUpPressed: Window.window.moveControlFocus(field,false)
    Keys.onDownPressed: Window.window.moveControlFocus(field,true)
    Keys.onReturnPressed: Window.window.editField(field)
    Keys.onEnterPressed: Window.window.editField(field)
    color: "#edf5f8"
    placeholderTextColor: "#a0b5c1"
    selectionColor: "#3d887f"
    background: Rectangle { color: "#192d3a"; radius: 10; border.width: field.activeFocus ? 3 : 1; border.color: field.activeFocus ? "#a8f3de" : "#506975" }
}
