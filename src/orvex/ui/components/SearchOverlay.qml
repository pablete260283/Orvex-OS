import QtQuick
import QtQuick.Controls
Popup {
    id: search
    property var backend
    property string previousQuery: ""
    signal finished()
    objectName: "searchOverlay"
    x: 310; y: 180; width: 1300; height: 800; padding: 40
    modal: true; focus: true; closePolicy: Popup.NoAutoClose
    function begin() { previousQuery=backend.query; open(); keys.currentIndex=0; Qt.callLater(function(){keys.forceActiveFocus()}) }
    function cancel() { backend.setQuery(previousQuery); close(); finished() }
    function accept() { close(); finished() }
    function choose(value) {
        if(value==="Resultados"){accept();return}
        if(value==="Cancelar"){cancel();return}
        var q=backend.query
        if(value==="Borrar")q=Array.from(q).slice(0,-1).join("")
        else if(value==="Limpiar")q=""
        else q+=(value==="Espacio"?" ":value)
        backend.setQuery(q.slice(0,120))
    }
    background: Rectangle { color: "#f5101e2b"; radius: 24; border.color: "#8ce9d5" }
    contentItem: Column {
        spacing: 24
        Text { text: "Buscar en "+(search.backend.page===2?"Multimedia":"Videojuegos"); font.pixelSize: 34; color: "#f1f7f8" }
        Text { objectName: "searchQuery"; text: search.backend.query || "Elige letras con el mando"; width: parent.width; elide: Text.ElideLeft; font.pixelSize: 30; color: "#a8f3de" }
        Text { objectName: "searchResultCount"; text: search.backend.showcase.length ? search.backend.showcase.length+" resultados · Resultados para elegir un título" : "Sin coincidencias"; color: "#bdcdd8"; font.pixelSize: 22 }
        GridView {
            id: keys; objectName: "virtualKeyboard"; width: parent.width; height: 470; cellWidth: 122; cellHeight: 76
            interactive: false; keyNavigationEnabled: false
            model: ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","ñ","á","é","í","ó","ú","ü","0","1","2","3","4","5","6","7","8","9","-","'",".","Espacio","Borrar","Limpiar","Resultados","Cancelar"]
            delegate: ActionButton {
                required property string modelData
                required property int index
                objectName: "virtualKey-"+modelData
                width: 116; height: 64; text: modelData
                selected: keys.currentIndex===index
                Accessible.name: modelData
                contentItem: Text { text: modelData; color: "#e3eef4"; font.pixelSize: modelData.length>6?17:22; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                background: Rectangle { radius: 14; color: keys.currentIndex===index?"#29424a":"#1a2a39"; border.width: keys.currentIndex===index?3:1; border.color: keys.currentIndex===index?"#a8f3de":"#314957" }
                onClicked: {keys.currentIndex=index;search.choose(modelData);if(search.opened)keys.forceActiveFocus()}
            }
            Keys.onPressed: function(event) {
                var n=currentIndex
                if(event.key===Qt.Key_Right)n=(n+1)%count
                else if(event.key===Qt.Key_Left)n=(n+count-1)%count
                else if(event.key===Qt.Key_Down)n=Math.min(count-1,n+10)
                else if(event.key===Qt.Key_Up)n=Math.max(0,n-10)
                else if(event.key===Qt.Key_Return || event.key===Qt.Key_Enter){search.choose(model[n]);event.accepted=true;return}
                else if(event.key===Qt.Key_Escape){search.cancel();event.accepted=true;return}
                else {event.accepted=false;return}
                currentIndex=n;event.accepted=true
            }
        }
        Text { text: "Flechas: mover · Confirmar: elegir · Volver: cancelar"; color: "#bdcdd8"; font.pixelSize: 20 }
    }
}
