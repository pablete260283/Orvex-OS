import QtQuick
import QtQuick.Controls
import QtQuick.Window
TextArea {
    id:field
    clip:true
    color:"#edf5f8";selectionColor:"#3d887f";selectedTextColor:"#ffffff"
    placeholderTextColor:"#a0b5c1";font.pixelSize:22;wrapMode:TextEdit.Wrap
    focusPolicy:Qt.StrongFocus
    background:Rectangle{color:"#192d3a";radius:10;border.width:field.activeFocus?3:1;border.color:field.activeFocus?"#a8f3de":"#506975"}
    Keys.onUpPressed:Window.window.moveControlFocus(field,false)
    Keys.onDownPressed:Window.window.moveControlFocus(field,true)
    Keys.onReturnPressed: if(!readOnly)Window.window.editField(field)
}
