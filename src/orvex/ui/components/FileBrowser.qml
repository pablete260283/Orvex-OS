import QtQuick
import QtQuick.Controls
Popup {
    id:browser
    objectName:"fileBrowser"
    required property var backend
    property var callback:null
    property var listing:({directory:"",parent:"computer",items:[],error:""})
    property var extensions:[]
    property bool foldersOnly:false
    property string heading:"Seleccionar archivo"
    readonly property var entries:listing.items.filter(function(e){return e.directory || (!foldersOnly && (!extensions.length || extensions.indexOf(e.name.split('.').pop().toLowerCase())>=0))})
    x:260;y:100;width:1400;height:880;padding:30;modal:true;focus:true;closePolicy:Popup.NoAutoClose
    function visit(path){listing=backend.browseDirectory(path);pathField.text=listing.directory;files.currentIndex=0;Qt.callLater(function(){files.forceActiveFocus()})}
    function begin(title,handler,types,directories){heading=title;callback=handler;extensions=types||[];foldersOnly=directories||false;visit("");open();Qt.callLater(function(){files.forceActiveFocus()})}
    function finish(path){var handler=callback;callback=null;close();if(handler && path)handler(path)}
    function choose(){var item=entries[files.currentIndex];if(!item)return;if(item.directory)visit(item.path);else finish(item.path)}
    background:Rectangle{color:"#10202d";radius:22;border.color:"#a8f3de"}
    FocusColumn{width:parent.width;spacing:14
        Text{text:browser.heading;color:"#edf5f8";font.pixelSize:32}
        DarkField{id:pathField;objectName:"browserPath";width:parent.width;placeholderText:"Ruta de carpeta"}
        Row{spacing:12
            ActionButton{objectName:"browserGo";width:320;text:"Abrir ruta";onClicked:browser.visit(pathField.text)}
            ActionButton{objectName:"browserParent";width:320;text:"Subir";onClicked:browser.visit(browser.listing.parent)}
            ActionButton{width:320;text:"Unidades";onClicked:browser.visit("computer")}
        }
        ListView{id:files;objectName:"browserFiles";width:parent.width;height:450;clip:true;model:browser.entries;activeFocusOnTab:true;keyNavigationEnabled:false
            delegate:ActionButton{required property var modelData;required property int index;objectName:"browserFile-"+index;width:files.width-16;height:62;text:(modelData.directory?"Carpeta · ":"")+modelData.name;selected:files.currentIndex===index;onClicked:{files.currentIndex=index;browser.choose()}}
            Keys.onPressed:function(event){
                if(event.key===Qt.Key_Down){currentIndex=Math.min(count-1,currentIndex+1);positionViewAtIndex(currentIndex,ListView.Contain)}
                else if(event.key===Qt.Key_Up){if(currentIndex>0)currentIndex--;else pathField.forceActiveFocus();positionViewAtIndex(currentIndex,ListView.Contain)}
                else if(event.key===Qt.Key_Return || event.key===Qt.Key_Enter)browser.choose()
                else if(event.key===Qt.Key_Left)browser.visit(browser.listing.parent)
                else if(event.key===Qt.Key_Right)closeBrowser.forceActiveFocus()
                else if(event.key===Qt.Key_Escape)browser.finish("")
                else{event.accepted=false;return}
                event.accepted=true
            }
            ScrollIndicator.vertical:ScrollIndicator{}
        }
        Text{width:parent.width;wrapMode:Text.WordWrap;color:"#b7cbd6";font.pixelSize:22;text:browser.listing.error || (files.count?"Confirmar: abrir carpeta o seleccionar · Derecha: opciones":"Carpeta vacía o sin archivos compatibles. Derecha: opciones.")}
        Row{spacing:16
            ActionButton{visible:browser.foldersOnly;width:620;text:"Seleccionar esta carpeta";enabled:browser.listing.directory!=="computer";onClicked:browser.finish(browser.listing.directory)}
            ActionButton{id:closeBrowser;objectName:"browserCancel";width:620;text:"Cancelar";onClicked:browser.finish("")}
        }
        Keys.onEscapePressed:browser.finish("")
    }
}
