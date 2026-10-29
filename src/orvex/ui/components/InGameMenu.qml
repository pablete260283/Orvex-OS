import QtQuick
import QtQuick.Controls
import QtQuick.Window
Window {
    id:overlay
    objectName:"inGameOverlay"
    required property var controller
    signal controlsRequested()
    width:1000;height:670;minimumWidth:800;minimumHeight:580
    title:"ORVEX · Menú de juego";color:"#10202d"
    flags:Qt.Dialog | Qt.WindowStaysOnTopHint
    visible:controller.opened && controller.state!=="controls"
    onVisibleChanged: if(visible){requestActivate();Qt.callLater(function(){if(controller.state==="confirm-close")cancelClose.forceActiveFocus();else continueGame.forceActiveFocus()})}
    onClosing:function(close){close.accepted=false;controller.back()}
    Connections{target:controller
        function onChanged(){if(overlay.visible)Qt.callLater(function(){if(controller.state==="confirm-close")cancelClose.forceActiveFocus();else continueGame.forceActiveFocus()})}
    }
    Rectangle{anchors.fill:parent;anchors.margins:16;color:"#132b37";radius:24;border.color:"#69c8b5"}
    FocusColumn{anchors.fill:parent;anchors.margins:46;spacing:18
        Text{text:"ORVEX · Menú de juego";font.pixelSize:34;color:"#edf5f8"}
        Text{width:parent.width;height:100;text:controller.message;wrapMode:Text.WordWrap;font.pixelSize:22;color:"#b7cbd6"}
        ActionButton{id:continueGame;objectName:"quickContinue";width:parent.width;visible:controller.state==="menu" || controller.state==="waiting-close";text:"Continuar jugando";accent:activeFocus;onClicked:controller.resume()}
        ActionButton{objectName:"quickClose";width:parent.width;visible:controller.state==="menu";text:"Cerrar juego y volver a ORVEX";onClicked:controller.ask_close()}
        ActionButton{objectName:"quickControls";width:parent.width;visible:controller.state==="menu";text:"Configuración de controles";onClicked:{controller.controls();overlay.controlsRequested()}}
        Text{width:parent.width;visible:controller.state==="confirm-close";text:"Guarda tu partida antes de continuar. Se solicitará el cierre a la aplicación; no se garantiza que guarde ni se forzará su salida.";wrapMode:Text.WordWrap;color:"#edf5f8";font.pixelSize:23}
        ActionButton{id:cancelClose;objectName:"quickCancelClose";width:parent.width;visible:controller.state==="confirm-close";text:"Cancelar";onClicked:controller.back()}
        ActionButton{objectName:"quickConfirmClose";width:parent.width;visible:controller.state==="confirm-close";text:"Solicitar cierre seguro";onClicked:controller.close_game()}
        Keys.onEscapePressed:controller.back()
    }
    function moveControlFocus(item,forward){/* Buttons use FocusColumn; no text fields here. */}
}
