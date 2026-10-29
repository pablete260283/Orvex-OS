import QtQuick
import QtQuick.Controls
import QtQuick.Window
ComboBox {
    id: control
    Keys.onUpPressed: Window.window.moveControlFocus(control,false)
    Keys.onDownPressed: Window.window.moveControlFocus(control,true)
    Keys.onLeftPressed: { if (count>0) currentIndex=(currentIndex+count-1)%count; activated(currentIndex) }
    Keys.onRightPressed: { if (count>0) currentIndex=(currentIndex+1)%count; activated(currentIndex) }
    property string emptyText: "Sin opciones disponibles"
    displayText: count ? currentText : emptyText
    focusPolicy: Qt.StrongFocus
    Accessible.name: displayText
    Keys.onReturnPressed: if(count)popup.open()
    Keys.onEnterPressed: if(count)popup.open()
    implicitHeight: 60
    font.pixelSize: 21
    leftPadding: 15
    rightPadding: 42
    contentItem: Text {
        text: control.displayText
        color: control.enabled ? "#edf5f8" : "#8a9ca8"
        font: control.font
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
        leftPadding: control.leftPadding
        rightPadding: control.rightPadding
    }
    indicator: Text {
        x: control.width-width-16; y: (control.height-height)/2
        text: "▾"; color: "#a8f3de"; font.pixelSize: 24
    }
    background: Rectangle {
        color: "#192d3a"; radius: 10
        border.width: control.activeFocus ? 3 : 1
        border.color: control.activeFocus ? "#a8f3de" : "#506975"
    }
    delegate: ItemDelegate {
        id: option
        objectName: "comboOption-"+index
        width: control.width; height: 64
        text: control.textAt(index)
        font.pixelSize: 20
        highlighted: options.currentIndex === index
        onClicked:{control.currentIndex=index;control.activated(index);control.popup.close()}
        contentItem: Text { text: option.text; font: option.font; color: "#edf5f8"; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter }
        background: Rectangle { color: option.highlighted ? "#325b58" : "#192d3a" }
    }
    popup: Popup {
        objectName: control.objectName+"-popup"
        y: control.height; width: control.width; padding: 4
        modal: true; focus: true
        onClosed: control.forceActiveFocus()
        onOpened: {options.currentIndex=control.currentIndex;options.forceActiveFocus()}
        implicitHeight: Math.max(72,Math.min(control.count*64+8, 328))
        contentItem: ListView {
            id: options
            clip: true; implicitHeight: contentHeight
            boundsBehavior: Flickable.StopAtBounds
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex
            Keys.onPressed: function(event) {
                if(event.key===Qt.Key_Down || event.key===Qt.Key_Up){
                    currentIndex=(currentIndex+control.count+(event.key===Qt.Key_Down?1:-1))%control.count
                    positionViewAtIndex(currentIndex,ListView.Contain);event.accepted=true;return
                }
                if(event.key===Qt.Key_Escape){control.popup.close();event.accepted=true;return}
                if(event.key===Qt.Key_Return || event.key===Qt.Key_Enter){
                    if(currentIndex>=0){control.currentIndex=currentIndex;control.activated(currentIndex)}
                    control.popup.close();event.accepted=true;return
                }
                event.accepted=false
            }
            ScrollIndicator.vertical: ScrollIndicator {}
        }
        background: Rectangle { color: "#192d3a"; border.color: "#a8f3de"; radius: 10 }
    }
}
