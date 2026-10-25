import QtQuick
Item {
    id: backdrop
    property string art: ""
    property bool reduced: false
    property string profile: "adult"
    onProfileChanged: {fade.stop();base.source="";incoming.source="";incoming.opacity=0;debounce.restart()}
    function update() {
        fade.stop()
        // Finish an interrupted blend before preparing the next local image.
        if(incoming.opacity>0.5) base.source=incoming.source
        incoming.opacity=0
        incoming.source=art ? "../assets/"+art+".svg" : ""
        if(!art)base.source=""
        else if(incoming.status===Image.Ready)fade.restart()
    }
    onArtChanged: debounce.restart()
    Timer { id: debounce; interval: backdrop.reduced ? 0 : 100; onTriggered: backdrop.update() }
    Image { id: base; anchors.fill: parent; fillMode: Image.PreserveAspectCrop; asynchronous: false }
    Image { id: incoming; anchors.fill: parent; fillMode: Image.PreserveAspectCrop; opacity: 0; onStatusChanged: if(status===Image.Ready)fade.restart() }
    SequentialAnimation { id: fade
        NumberAnimation { target: incoming; property: "opacity"; to: 1; duration: backdrop.reduced ? 0 : 280 }
        ScriptAction { script: {base.source=incoming.source;incoming.opacity=0} }
    }
    Rectangle { anchors.fill: parent; color: "#b809131e" }
    Rectangle { anchors.fill: parent; gradient: Gradient { GradientStop {position:0;color:"#c90b1320"} GradientStop {position:0.5;color:"#600b1320"} GradientStop {position:1;color:"#f50b1320"} } }
}
