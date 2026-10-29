import QtQuick
import QtQuick.Controls
import QtQuick.Window
import "../components"
import "../components/FocusTools.js" as FocusTools
FocusScope {
    id: settings
    signal importRequested()
    signal artworkRequested(string gameId,string role)
    signal backRequested()
    property string selectedGame: ""
    property var backend
    property int category: 0
    property string message: ""
    readonly property var categories: ["Interfaz","Controles","Audio","Biblioteca","Perfiles","Sistema"]
    readonly property bool modalActive: dolphinSetup.opened || controllerPopup.opened || metadataEditor.opened || removal.opened
    function enter() {choices.itemAt(category).forceActiveFocus()}
    function openManagerFocus(){managerEntry.forceActiveFocus()}
    function openControls(){category=1;controllerPopup.open()}
    function loadEmulator(){var config=backend.emulatorConfiguration(emulatorChoice.currentText);dolphinPath.text=config.executable||"";romRoot.text=config.root||""}
    function loadGame(){
        var e=backend.managedGames[games.currentIndex]
        selectedGame=e?e.id:""
        editName.text=e?e.name:"";editPlatform.text=e?e.platform:""
        editPath.text=e?e.executable:"";editArgs.text=e?e.arguments:"[]"
    }
    function firstContent(){FocusTools.first(content)}
    function resetEdits(){loadGame();message="Cambios sin guardar descartados."}
    onVisibleChanged: {if(visible)Qt.callLater(enter);else {recoveryConsent.close();controlConsent.close();controllerPopup.close();dolphinSetup.close();metadataEditor.close();removal.close()}}
    Text {text:"Configuración";color:"#edf5f8";font.pixelSize:46}
    FocusColumn {y:100;spacing:18
        Repeater {id:choices;model:settings.categories
            ActionButton {
                required property string modelData
                required property int index
                objectName:"settingsCategory-"+index;width:350;text:modelData;selected:settings.category===index
                onClicked:{settings.category=index;settings.message="";settings.firstContent()}
                Keys.onDownPressed:{settings.category=(index+1)%6;choices.itemAt(settings.category).forceActiveFocus()}
                Keys.onUpPressed:{settings.category=(index+5)%6;choices.itemAt(settings.category).forceActiveFocus()}
                Keys.onRightPressed: settings.firstContent()
                Keys.onEscapePressed: settings.backRequested()
            }
        }
        ActionButton {objectName:"settingsBack";width:350;text:"Volver";onClicked:settings.backRequested()}
    }
    Rectangle {id:pane;x:410;y:100;width:1320;height:720;radius:26;color:"#132332"
        Text {x:40;y:25;text:settings.categories[settings.category];color:"#edf5f8";font.pixelSize:36}
        ScrollView {id:scroll;x:40;y:88;width:1240;height:550;clip:true
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            FocusColumn {id:content;width:1220;spacing:16
                Text {visible:settings.category!==3;width:1200;wrapMode:Text.WordWrap;lineHeight:1.25;color:"#b7cbd6";font.pixelSize:24
                    text:settings.category===0?"Preferencias funcionales · Se guardan automáticamente en SQLite.":settings.category===1?"Cruceta o joystick: mover · Confirmar: elegir · Volver: regresar.
Los ajustes externos requieren aprobación y no se cambian durante el juego.":settings.category===2?"Audio del sistema: integración futura. ORVEX no modifica volumen ni dispositivos.
Utiliza los ajustes de audio de Windows o del juego.":settings.category===4?"Perfiles demostrativos sin PIN. El cambio es libre: no es un control parental seguro.":"Diagnóstico técnico · Sesiones y errores se conservan sin mostrarlos durante el juego."
                }
                ActionButton {objectName:"reducedMotion";width:1100;visible:settings.category===0;text:"Reducir movimiento: "+(settings.backend.reducedMotion?"Sí":"No");onClicked:settings.backend.toggleMotion()}
                Row {spacing:12;visible:settings.category===0
                    Repeater {model:["dynamic","fixed","default"]
                        ActionButton {required property string modelData;width:360;text:modelData==="dynamic"?"Fondo dinámico":modelData==="fixed"?"Fondo fijo":"Predeterminado";selected:settings.backend.backgroundMode===modelData;onClicked:settings.backend.setBackgroundMode(modelData)}
                    }
                }
                Flow {width:1200;spacing:12;visible:settings.category===0 && settings.backend.backgroundMode==="fixed"
                    Repeater {model:settings.backend.backgroundOptions
                        ActionButton {required property var modelData;width:280;text:modelData.title;selected:settings.backend.fixedBackground===modelData.id;onClicked:settings.backend.setFixedBackground(modelData.id)}
                    }
                }
                ActionButton {objectName:"controllerLayout";width:1100;visible:settings.category===1;text:"Botones WinMM: "+(settings.backend.controllerLayout==="sony"?"Sony (Cross / Circle)":"Estándar (1 / 2)");onClicked:settings.backend.toggleControllerLayout()}
                ActionButton {id:managerEntry;objectName:"openControllerManager";enabled:settings.backend.profile==="adult";width:1100;visible:settings.category===1;text:"Gestor de mandos y perfiles…";onClicked:controllerPopup.open()}
                ActionButton {objectName:"quickMenuShortcut";width:1100;visible:settings.category===1;text:"Menú de juego · Atajo: "+settings.backend.quickMenuShortcutLabel;onClicked:settings.backend.beginShortcutCapture()}
                Text {width:1200;visible:settings.category===1;text:settings.backend.quickMenuCaptureMessage;wrapMode:Text.WordWrap;color:"#a8f3de";font.pixelSize:22}
                FocusColumn {id:libraryFields;objectName:"libraryFields";width:1200;spacing:14;visible:settings.category===3
                    Row {spacing:18
                        ActionButton {objectName:"emulatorSettings";width:580;text:"Emuladores y carpetas…";enabled:settings.backend.profile==="adult"&&!settings.backend.launchBusy;onClicked:dolphinSetup.open()}
                        ActionButton {objectName:"libraryImport";width:580;text:"Importar juego";enabled:settings.backend.profile==="adult"&&!settings.backend.launchBusy;onClicked:settings.importRequested()}
                    }
                    Text {visible:!settings.backend.managedGames.length;width:1180;wrapMode:Text.WordWrap;color:"#b7cbd6";font.pixelSize:24;text:settings.backend.profile==="adult"?"Tu biblioteca está vacía. Importa un juego o configura una carpeta de ROMs.":"Administración disponible en el perfil Adulto."}
                    DarkCombo {id:games;objectName:"managedGames";width:1180;model:settings.backend.managedGames;textRole:"title";emptyText:"No hay juegos para administrar";enabled:count>0;onActivated:settings.loadGame();onModelChanged:Qt.callLater(settings.loadGame);onCurrentIndexChanged:Qt.callLater(settings.loadGame)}
                    FocusColumn {width:1180;spacing:14;visible:!!settings.selectedGame;enabled:!!settings.selectedGame&&!settings.backend.launchBusy
                        DarkField {id:editName;objectName:"editGameName";width:1180;placeholderText:"Nombre del juego"}
                        DarkField {id:editPlatform;objectName:"editGamePlatform";width:1180;placeholderText:"Plataforma"}
                        DarkField {id:editPath;objectName:"editGamePath";width:1180;placeholderText:"Ruta del ejecutable"}
                        DarkField {id:editArgs;objectName:"editGameArgs";width:1180;placeholderText:"Parámetros avanzados (array JSON)"}
                        Row {spacing:14
                            ActionButton {objectName:"saveGameEdits";width:380;text:"Guardar edición";onClicked:{if(settings.backend.editGame(settings.selectedGame,editName.text,editPlatform.text,editPath.text,editArgs.text))settings.message="Cambios guardados."}}
                            ActionButton {width:380;text:"Cancelar edición";onClicked:settings.resetEdits()}
                            ActionButton {width:380;text:"Ocultar / mostrar";onClicked:{var e=settings.backend.managedGames[games.currentIndex];if(e)settings.backend.hideGame(e.id,!e.hidden)}}
                        }
                        Row {spacing:14
                            ActionButton {width:380;text:"Carátula…";onClicked:settings.artworkRequested(settings.selectedGame,"cover")}
                            ActionButton {width:380;text:"Fondo…";onClicked:settings.artworkRequested(settings.selectedGame,"backdrop")}
                            ActionButton {width:380;objectName:"metadataSettings";text:"Metadatos…";onClicked:metadataEditor.open()}
                        }
                        ActionButton {objectName:"removeGame";width:1180;text:"Quitar de biblioteca…";onClicked:removal.open()}
                    }
                }
                Row {spacing:20;visible:settings.category===4
                    ActionButton {objectName:"settingsAdult";width:560;text:"Adulto · demo";selected:settings.backend.profile==="adult";onClicked:settings.backend.setProfile("adult")}
                    ActionButton {objectName:"settingsChild";width:560;text:"Infantil · demo";selected:settings.backend.profile==="child";onClicked:settings.backend.setProfile("child")}
                }
                TextArea {objectName:"systemDiagnostics";visible:settings.category===5;width:1200;implicitHeight:350;readOnly:true;activeFocusOnTab:true;wrapMode:TextEdit.Wrap;text:settings.backend.diagnosticReport;color:"#edf5f8";font.pixelSize:20;background:Rectangle{color:"#0d1c29";radius:12} Keys.onEscapePressed:settings.enter()}
                ActionButton {visible:settings.category===5;width:1180;text:"Actualizar diagnóstico";onClicked:settings.backend.refreshControllers()}
                ActionButton {objectName:"settingsCategories";width:1180;text:"Categorías · Volver";onClicked:settings.enter()}
            }
        }
        Text {x:40;y:650;width:1240;height:58;maximumLineCount:2;elide:Text.ElideRight;text:settings.message || settings.backend.operationMessage;color:"#a8f3de";font.pixelSize:21;wrapMode:Text.WordWrap}
        Popup { id: dolphinSetup; objectName:"emulatorDialog"; focus:true; onOpened:{settings.loadEmulator();emulatorChoice.forceActiveFocus()} onClosed:settings.firstContent(); x: 50; y: -160; width: 1200; height: 850; padding:25; modal: true
            background: Rectangle {color: "#142333";radius: 18; border.color: "#a8f3de"}
            ScrollView {anchors.fill:parent;clip:true
            FocusColumn { spacing: 12; width: 1090
                Label { color: "#edf5f8"; font.pixelSize:26; text: "Emuladores · Dolphin (Wii/GameCube), PCSX2 (PS2)" }
                DarkCombo { id: emulatorChoice; width: 1050; model: ["dolphin","pcsx2"]; onActivated:settings.loadEmulator() }
                DarkField { id: dolphinPath; width: 1050; placeholderText: "Ruta del ejecutable del emulador" }
                DarkField { id: romRoot; width: 1050; placeholderText: "Carpeta principal de ROMs (contiene Wii y GameCube)" }
                Row {spacing:12
                    ActionButton {width:510;text:"Examinar ejecutable…";onClicked:Window.window.browseFile("Ejecutable del emulador",function(path){dolphinPath.text=path},[],false)}
                    ActionButton {width:510;text:"Examinar carpeta ROMs…";onClicked:Window.window.browseFile("Carpeta principal de ROMs",function(path){romRoot.text=path},[],true)}
                }
                ActionButton { text: "Guardar configuración"; onClicked: settings.backend.configureEmulator(emulatorChoice.currentText,dolphinPath.text,romRoot.text) }
                ActionButton { text: "Escanear ahora"; onClicked: settings.backend.scanEmulator(emulatorChoice.currentText) }
                Text { width: 1050; wrapMode: Text.Wrap; text: settings.backend.operationMessage; color: "#edf5f8"; font.pixelSize:22 }
                Text { color: "#edf5f8"; font.pixelSize:22; width:1050; wrapMode:Text.WordWrap; text: "Selecciona primero un juego en Biblioteca para asociar su perfil." }
                DarkField { id: profileReference; width: 1050; placeholderText: "Perfil INI existente (no se modifica)" }
                ActionButton { enabled:!!settings.selectedGame; text: "Asociar perfil"; onClicked: settings.backend.associateControlProfile(settings.selectedGame,profileReference.text) }
                DarkField {id:pauseConfig;objectName:"pauseConfig";width:1050;placeholderText:"Opcional: INI activo con pausa al perder foco habilitada"}
                ActionButton {width:1050;text:"Aprobar referencia de pausa (solo lectura)";onClicked:settings.backend.approvePauseConfig(emulatorChoice.currentText,pauseConfig.text)}
                ActionButton { text: "Cerrar"; onClicked: dolphinSetup.close() }
            }
            }
        }
        Popup {
            id: controllerPopup; onClosed:openManagerFocus(); objectName: "controllerManager"; x: 80; y: -65; width: 1150; height: 845; padding: 30; modal: true; focus: true
            onOpened: {settings.backend.refreshControllers(); deviceChoice.forceActiveFocus()}
            Timer { interval: 3000; repeat: true; running: controllerPopup.opened; onTriggered: if(!deviceChoice.popup.visible)settings.backend.pollControllers() }
            background: Rectangle { radius: 18; color: "#10202d"; border.color: "#a8f3de" }
            FocusColumn {
                spacing: 12; width: parent.width
                Text { text: "Mandos y perfiles"; color: "#edf5f8"; font.pixelSize: 32 }
                Text { text: settings.backend.launchBusy?"Juego en ejecución: puedes consultar mandos; cambios externos disponibles al cerrar el juego.":"Mueve ↑↓ entre campos y ←→ para elegir. Importa el perfil Joy-Con probado desde Dolphin."; width: parent.width; wrapMode: Text.WordWrap; color: "#b7d2d8"; font.pixelSize: 18 }
                Row { spacing: 12
                    DarkCombo { id: deviceChoice; Keys.onDownPressed: detectController.forceActiveFocus(); Keys.onUpPressed: closeControllers.forceActiveFocus(); objectName: "controllerDevices"; width: 650; model: settings.backend.controllerDevices; textRole: "name"; Accessible.name: "Mando detectado" }
                    ActionButton { id: detectController; Keys.onUpPressed: deviceChoice.forceActiveFocus(); Keys.onDownPressed: controlEngine.forceActiveFocus(); width: 380; text: "Detectar mandos"; onClicked: settings.backend.refreshControllers() }
                }
                Text {width:parent.width;wrapMode:Text.WordWrap;color:"#b7d2d8";font.pixelSize:20;text:{var d=settings.backend.controllerDevices[deviceChoice.currentIndex];return d?(d.display || d.name):"No hay mandos detectados. Conecta uno y elige Detectar mandos."}}
                Row { spacing: 12
                    DarkCombo { id: controlEngine; Keys.onUpPressed: detectController.forceActiveFocus(); Keys.onDownPressed: controlFamily.forceActiveFocus(); width: 220; model: [{label:"Dolphin",value:"dolphin"},{label:"PCSX2",value:"pcsx2"},{label:"PC nativo",value:"native"}]; textRole: "label"; valueRole: "value"; Accessible.name: "Motor del perfil" }
                    DarkCombo { id: controlFamily; Keys.onUpPressed: controlEngine.forceActiveFocus(); Keys.onDownPressed: importProfile.forceActiveFocus(); width: 380; model: [{label:"Joy-Con derecho",value:"joycon-r"},{label:"Joy-Con izquierdo",value:"joycon-l"},{label:"DualSense",value:"dualsense"},{label:"Xbox",value:"xbox"},{label:"Wiimote",value:"wiimote"},{label:"Otro",value:"other"}]; textRole: "label"; valueRole: "value"; Accessible.name: "Tipo de mando del perfil" }
                    ActionButton { id: importProfile; enabled:!settings.backend.launchBusy; Keys.onUpPressed: controlFamily.forceActiveFocus(); Keys.onDownPressed: controlProfile.forceActiveFocus(); width: 420; text: "Importar copia de INI…"; onClicked:Window.window.browseFile("Importar copia de perfil INI",function(path){settings.backend.captureControllerProfile(path,controlEngine.currentValue,controlFamily.currentValue)},["ini"],false) }
                }
                Row { spacing: 12
                    DarkCombo { id: controlProfile; Keys.onUpPressed: importProfile.forceActiveFocus(); Keys.onDownPressed: controlGame.forceActiveFocus(); width: 500; model: settings.backend.controllerProfiles; textRole: "name"; displayText: count===0 ? "No hay perfiles importados" : currentText; Accessible.name: "Perfil aprobado" }
                    DarkCombo { id: controlGame; Keys.onUpPressed: controlProfile.forceActiveFocus(); Keys.onDownPressed: controlScope.forceActiveFocus(); width: 520; model: settings.backend.managedGames; textRole: "title"; displayText: count===0 ? "No hay juegos disponibles" : currentText; Accessible.name: "Juego y versión" }
                }
                Row { spacing: 12
                    DarkCombo { id: controlScope; Keys.onUpPressed: controlGame.forceActiveFocus(); Keys.onDownPressed: controlPlayer.forceActiveFocus(); width: 260; model: [{label:"Este juego",value:"game"},{label:"Esta plataforma",value:"platform"},{label:"Predeterminado",value:"default"}]; textRole: "label"; valueRole: "value"; Accessible.name: "Ámbito: juego, plataforma o predeterminado" }
                    DarkCombo { id: controlPlayer; Keys.onUpPressed: controlScope.forceActiveFocus(); Keys.onDownPressed: {if(bindProfile.enabled)bindProfile.forceActiveFocus();else controlTarget.forceActiveFocus()} width: 180; model: ["1","2","3","4"]; Accessible.name: "Jugador" }
                    ActionButton { id: bindProfile; Keys.onUpPressed: controlPlayer.forceActiveFocus(); Keys.onDownPressed: controlTarget.forceActiveFocus(); width: 580; text: "Asociar perfil al mando"; enabled: !settings.backend.launchBusy && deviceChoice.currentIndex>=0 && controlProfile.currentIndex>=0 && controlGame.currentIndex>=0; onClicked: {var d=settings.backend.controllerDevices[deviceChoice.currentIndex];var p=settings.backend.controllerProfiles[controlProfile.currentIndex];var g=settings.backend.managedGames[controlGame.currentIndex];settings.backend.bindControllerProfile(p.id,g.id,controlScope.currentValue,d.device_id,d.family,parseInt(controlPlayer.currentText))} }
                }
                Row { spacing: 12
                    ActionButton { id: controlTarget; enabled:!settings.backend.launchBusy; Keys.onUpPressed: {if(bindProfile.enabled)bindProfile.forceActiveFocus();else controlPlayer.forceActiveFocus()} Keys.onDownPressed: controlApply.forceActiveFocus(); width: 500; text: "Elegir configuración Dolphin…"; onClicked:Window.window.browseFile("WiimoteNew.ini existente",function(path){settings.backend.configureControllerTarget(path)},["ini"],false) }
                    ActionButton { id: controlApply; enabled:!settings.backend.launchBusy; Keys.onUpPressed: controlTarget.forceActiveFocus(); Keys.onDownPressed: recoverButton.forceActiveFocus(); width: 520; text: "Aplicación temporal: "+(settings.backend.controllerAutoApply?"activada":"desactivada"); onClicked: controlConsent.open() }
                }
                Text { width: parent.width; height: 90; wrapMode: Text.WordWrap; elide: Text.ElideRight; maximumLineCount: 4; text: settings.backend.operationMessage; color: "#a8f3de"; font.pixelSize: 19 }
                Row { spacing: 12
                    ActionButton { id: recoverButton; enabled:!settings.backend.launchBusy; Keys.onUpPressed: controlApply.forceActiveFocus(); Keys.onDownPressed: closeControllers.forceActiveFocus(); width: 500; text: "Recuperar respaldo…"; onClicked: recoveryConsent.open() }
                    ActionButton { id: closeControllers; Keys.onUpPressed: recoverButton.forceActiveFocus(); Keys.onDownPressed: deviceChoice.forceActiveFocus(); width: 300; text: "Cerrar"; onClicked: controllerPopup.close() }
                }
            }
            Popup { id: recoveryConsent; onOpened: cancelRecovery.forceActiveFocus(); x: 100; y: 120; width: 900; height: 300; modal: true; focus: true
                background: Rectangle { color: "#182d37"; radius: 15; border.color: "#a8f3de" }
                FocusColumn { spacing: 20; width: parent.width
                    Text { width: 820; wrapMode: Text.WordWrap; color: "#edf5f8"; font.pixelSize: 22; text: "Cierra Dolphin completamente antes de recuperar el respaldo. Si el archivo cambió, ORVEX conservará ambos y mostrará la ruta de la copia." }
                    ActionButton { id: acceptRecovery; KeyNavigation.down: cancelRecovery; KeyNavigation.up: cancelRecovery; text: "Dolphin cerrado · Recuperar"; onClicked: {settings.backend.retryControllerRecovery();recoveryConsent.close()} }
                    ActionButton { id: cancelRecovery; KeyNavigation.down: acceptRecovery; KeyNavigation.up: acceptRecovery; text: "Cancelar"; onClicked: recoveryConsent.close() }
                }
            }
            Popup { id: controlConsent; onOpened: cancelControlConsent.forceActiveFocus(); x: 100; y: 120; width: 900; height: 370; modal: true; focus: true
                background: Rectangle { color: "#182d37"; radius: 15; border.color: "#a8f3de" }
                FocusColumn { spacing: 20; width: parent.width
                    Text { width: 820; wrapMode: Text.WordWrap; color: "#edf5f8"; font.pixelSize: 22; text: "La aplicación temporal modifica WiimoteNew.ini durante el juego. Se guarda una copia antes y se intenta restaurar al salir. Solo se admiten copias completas sin índices SDL variables; ante conflictos se conserva el archivo actual." }
                    ActionButton { id: acceptControlConsent; KeyNavigation.down: cancelControlConsent; KeyNavigation.up: cancelControlConsent; text: "Confirmar cambio"; onClicked: {settings.backend.toggleControllerAutoApply();controlConsent.close()} }
                    ActionButton { id: cancelControlConsent; KeyNavigation.down: acceptControlConsent; KeyNavigation.up: acceptControlConsent; text: "Cancelar"; onClicked: controlConsent.close() }
                }
            }
        }
        Popup { id: metadataEditor; objectName:"metadataDialog"; focus:true; onOpened:{settings.backend.cancelMetadata();proposal.forceActiveFocus()} onClosed:{settings.backend.cancelMetadata();settings.firstContent()} background:Rectangle{color:"#142333";radius:18;border.color:"#a8f3de"} x: 100; y: 20; width: 1100; height: 700; modal: true
            FocusColumn { spacing: 20; width: parent.width
                Label { color:"#edf5f8"; font.pixelSize:22; text: "Propuesta local JSON. No es una búsqueda en Internet." }
                DarkArea { id: proposal; width: 1000; height: 180; text: '{"description":"","genre":"","year":2026,"edition":"","source":"local"}' }
                ActionButton { text: "Revisar propuesta"; onClicked: review.text=settings.backend.proposeMetadata(settings.selectedGame,proposal.text) }
                DarkArea { id: review; width: 1000; height: 150; readOnly: true }
                ActionButton { text: "Confirmar reemplazo"; enabled:settings.backend.metadataPending; onClicked: {if(settings.backend.confirmMetadata())metadataEditor.close()} }
                ActionButton {text:"Cancelar";onClicked:metadataEditor.close()}
            }
        }
        Popup { id: removal; objectName:"removalDialog"; focus:true; onOpened:{keepHistory.checked=true;cancelRemoval.forceActiveFocus()} onClosed:settings.firstContent(); background:Rectangle{color:"#142333";radius:18;border.color:"#a8f3de"} x: 120; y: 150; width: 1000; height: 350; modal: true
            FocusColumn { spacing: 20
                Label { color:"#edf5f8"; font.pixelSize:22; text: "Quitar referencia. Nunca se borrarán juegos ni partidas." }
                CheckBox { id: keepHistory; width:900;height:60; background:Rectangle{radius:10;color:keepHistory.activeFocus?"#29424a":"transparent";border.width:keepHistory.activeFocus?3:0;border.color:"#a8f3de"} Keys.onReturnPressed:checked=!checked; Keys.onEnterPressed:checked=!checked; checked: true; contentItem:Text{text:keepHistory.text;color:"#edf5f8";font.pixelSize:23;leftPadding:50} text: "Conservar historial de sesiones" }
                ActionButton { text: "Confirmar retirada"; onClicked: {settings.backend.removeGame(settings.selectedGame,keepHistory.checked);removal.close()} }
                ActionButton { id:cancelRemoval;text: "Cancelar"; onClicked: removal.close() }
            }
        }
    }
    Connections {target:Window.window
        function onActiveFocusItemChanged(){
            var item=Window.window.activeFocusItem
            if(!item || !settings.visible || settings.modalActive)return
            var point=item.mapToItem(content,0,0)
            if(point.y>=0 && point.y<content.height){
                var flick=scroll.contentItem
                if(point.y<flick.contentY)flick.contentY=point.y
                else if(point.y+item.height>flick.contentY+scroll.height)flick.contentY=Math.min(flick.contentHeight-scroll.height,point.y+item.height-scroll.height+12)
            }
        }
    }
    Keys.onEscapePressed: enter()
}
