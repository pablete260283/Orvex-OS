import QtQuick
import QtQuick.Window
import "FocusTools.js" as FocusTools
Column {
    id: group
    property bool navigationScope: true
    Connections {
        target:Window.window
        function onActiveFocusItemChanged(){
            var item=Window.window.activeFocusItem
            if(!item || !group.visible)return
            var ancestor=item.parent,inside=false
            while(ancestor){if(ancestor===group){inside=true;break}ancestor=ancestor.parent}
            if(!inside)return
            ancestor=group.parent
            while(ancestor && ancestor.contentY===undefined)ancestor=ancestor.parent
            if(!ancestor || !ancestor.contentItem)return
            var point=item.mapToItem(ancestor.contentItem,0,0)
            if(point.y<ancestor.contentY)ancestor.contentY=Math.max(0,point.y-8)
            else if(point.y+item.height>ancestor.contentY+ancestor.height)
                ancestor.contentY=Math.max(0,Math.min(ancestor.contentHeight-ancestor.height,point.y+item.height-ancestor.height+12))
        }
    }
    Keys.onPressed: function(event) {
        if(event.key===Qt.Key_Down || event.key===Qt.Key_Right)FocusTools.move(group,Window.window.activeFocusItem,true)
        else if(event.key===Qt.Key_Up || event.key===Qt.Key_Left)FocusTools.move(group,Window.window.activeFocusItem,false)
        else {event.accepted=false;return}
        event.accepted=true
    }
}
