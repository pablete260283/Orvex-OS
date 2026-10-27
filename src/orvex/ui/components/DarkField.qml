import QtQuick
import QtQuick.Controls
TextField {
    id: field
    color: "#edf5f8"
    placeholderTextColor: "#a0b5c1"
    selectionColor: "#3d887f"
    background: Rectangle { color: "#192d3a"; radius: 10; border.width: field.activeFocus ? 3 : 1; border.color: field.activeFocus ? "#a8f3de" : "#506975" }
}
