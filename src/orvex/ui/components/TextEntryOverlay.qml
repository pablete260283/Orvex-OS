import QtQuick
import QtQuick.Controls
Popup {
    id: editor
    objectName:"textEntryOverlay"
    property var field: null
    property string draft:""
    property bool uppercase:false
    x:260;y:130;width:1400;height:840;padding:32;modal:true;focus:true;closePolicy:Popup.NoAutoClose
    function begin(target){field=target;draft=target.text;open();board.currentIndex=0;Qt.callLater(function(){board.forceActiveFocus()})}
    function finish(save){var target=field;if(save && target)target.text=draft;close();field=null;if(target)target.forceActiveFocus()}
    function choose(value){
        if(value==="Guardar"){finish(true);return}
        if(value==="Cancelar"){finish(false);return}
        if(value==="Borrar")draft=Array.from(draft).slice(0,-1).join("")
        else if(value==="Limpiar")draft=""
        else if(value==="Mayús")uppercase=!uppercase
        else if(draft.length<4096)draft+=(value==="Espacio"?" ":uppercase?value.toUpperCase():value)
    }
    background:Rectangle{color:"#10202d";radius:24;border.color:"#a8f3de"}
    Column {width:parent.width;spacing:20
        Text{text:editor.field?(editor.field.placeholderText || "Editar texto"):"Editar texto";color:"#edf5f8";font.pixelSize:32}
        Text{text:editor.draft || "Introduce texto con el mando";width:parent.width;height:90;wrapMode:Text.WrapAnywhere;maximumLineCount:3;elide:Text.ElideLeft;color:"#a8f3de";font.pixelSize:25}
        GridView {id:board;objectName:"textEntryKeyboard";width:parent.width;height:520;cellWidth:130;cellHeight:76;interactive:false;keyNavigationEnabled:false
            model:["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","ñ","á","é","í","ó","ú","0","1","2","3","4","5","6","7","8","9",":","/","\\","-","_",".","[","]","{","}","\"",",","=","(",")","+","Mayús","Espacio","Borrar","Limpiar","Guardar","Cancelar"]
            delegate:ActionButton{required property string modelData;required property int index;width:122;height:66;selected:board.currentIndex===index;text:editor.uppercase?modelData.toUpperCase():modelData;onClicked:{board.currentIndex=index;editor.choose(modelData);if(editor.opened)board.forceActiveFocus()}}
            Keys.onPressed:function(event){
                var n=currentIndex
                if(event.key===Qt.Key_Right)n=(n+1)%count
                else if(event.key===Qt.Key_Left)n=(n+count-1)%count
                else if(event.key===Qt.Key_Down)n=Math.min(count-1,n+10)
                else if(event.key===Qt.Key_Up)n=Math.max(0,n-10)
                else if(event.key===Qt.Key_Return || event.key===Qt.Key_Enter){editor.choose(model[n]);event.accepted=true;return}
                else if(event.key===Qt.Key_Escape){editor.finish(false);event.accepted=true;return}
                else {event.accepted=false;return}
                currentIndex=n;positionViewAtIndex(n,GridView.Contain);event.accepted=true
            }
        }
        Text{text:"Confirmar: elegir · Guardar: aplicar · Volver: cancelar";color:"#b7cbd6";font.pixelSize:22}
    }
}
