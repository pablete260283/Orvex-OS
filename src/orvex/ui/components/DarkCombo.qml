import QtQuick
import QtQuick.Controls
ComboBox {
    id: control
    Keys.onLeftPressed: { if (count>0) currentIndex=(currentIndex+count-1)%count; activated(currentIndex) }
    Keys.onRightPressed: { if (count>0) currentIndex=(currentIndex+1)%count; activated(currentIndex) }
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
        width: control.width; height: 55
        text: control.textRole ? (Array.isArray(control.model) ? modelData[control.textRole] : model[control.textRole]) : modelData
        font.pixelSize: 20
        highlighted: control.highlightedIndex === index
        contentItem: Text { text: parent.text; font: parent.font; color: "#edf5f8"; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter }
        background: Rectangle { color: parent.highlighted ? "#325b58" : "#192d3a" }
    }
    popup: Popup {
        y: control.height; width: control.width; padding: 2
        implicitHeight: Math.min(contentItem.implicitHeight+4, 360)
        contentItem: ListView {
            clip: true; implicitHeight: contentHeight
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex
            ScrollIndicator.vertical: ScrollIndicator {}
        }
        background: Rectangle { color: "#192d3a"; border.color: "#a8f3de"; radius: 10 }
    }
}
