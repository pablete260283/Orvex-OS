import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import "../components"
Item {
    id: settings
    signal importRequested()
    signal artworkRequested(string gameId,string role)
    property string selectedGame: ""
    property var backend
    property int category: 0
    property string message: ""
    readonly property var categories: ["Interfaz","Controles","Audio","Biblioteca","Perfiles","Sistema"]
    function enter() { choices.itemAt(category).forceActiveFocus() }
    opacity: visible ? 1 : 0
    Behavior on opacity { NumberAnimation { duration: settings.backend.reducedMotion ? 0 : 120 } }
    Text { text: "Configuración"; color: "#edf5f8"; font.pixelSize: 46; font.weight: Font.DemiBold }
    Column { y: 110; spacing: 18
        Repeater { id: choices; model: settings.categories
            ActionButton { required property string modelData; required property int index; objectName: "settingsCategory-"+index; width: 350; text: modelData; selected: settings.category===index; onClicked: {settings.category=index;settings.message=""} }
        }
    }
    Rectangle { x: 410; y: 110; width: 1320; height: 660; radius: 26; color: "#132332"
        Text { x: 45; y: 38; text: settings.categories[settings.category]; color: "#edf5f8"; font.pixelSize: 38 }
        Text { visible: settings.category!==3; x: 45; y: 115; width: 1220; text: settings.category===0 ? "FUNCIONAL · Preferencias guardadas en SQLite" : settings.category===3 ? "FUNCIONAL · Filtros y favoritos por perfil" : settings.category===4 ? "DEMO · Filtro infantil hasta 7+. Sin autenticación ni PIN.
El cambio de perfil es libre: no es un control parental seguro." : settings.category===1 ? "Navegación: cruceta o joystick · Confirmar · Volver.\nWindows: XInput y alternativa WinMM. Linux: joydev.\nCompatibilidad física pendiente; no configura Bluetooth ni emuladores." : settings.category===5 ? "FUNCIONAL · ORVEX OS 0.4
Qt 6 / QML · PySide6 · SQLite
Biblioteca local y catálogo demo separados. Sin servicios externos." : "FUTURO · Esta categoría no controla dispositivos.
La integración se desarrollará en una próxima fase."; color: settings.category===1 || settings.category===2 ? "#bdac8c" : "#9cb5c7"; font.pixelSize: 26; wrapMode: Text.WordWrap; lineHeight: 1.5 }
        ActionButton { objectName: "openControllerManager"; enabled: settings.backend.profile==="adult"; x: 45; y: 450; width: 1000; visible: settings.category===1; text: "Gestor de mandos y perfiles…"; onClicked: controllerPopup.open() }
        ActionButton { x: 45; y: 360; width: 1000; visible: settings.category===1; text: "Botones WinMM: "+(settings.backend.controllerLayout==="sony"?"Sony (Cross / Circle)":"Estándar (1 / 2)"); onClicked: settings.backend.toggleControllerLayout() }
        Row { x: 45; y: 395; spacing: 18; visible: settings.category===0
            Repeater { model: ["dynamic","fixed","default"]
                ActionButton { required property string modelData; width: 360; text: modelData==="dynamic" ? "Fondo dinámico" : modelData==="fixed" ? "Fondo fijo" : "Predeterminado"; selected: settings.backend.backgroundMode===modelData; onClicked: settings.backend.setBackgroundMode(modelData) }
            }
        }
        Row { x: 45; y: 485; spacing: 12; visible: settings.category===0 && settings.backend.backgroundMode==="fixed"
            Repeater { model: settings.backend.backgroundOptions
                ActionButton { required property var modelData; width: 135; text: modelData.title; selected: settings.backend.fixedBackground===modelData.id; onClicked: settings.backend.setFixedBackground(modelData.id) }
            }
        }
        ActionButton { objectName: "reducedMotion"; x: 45; y: 300; width: 650; visible: settings.category===0; text: "Reducir movimiento: "+(settings.backend.reducedMotion ? "Sí" : "No"); onClicked: settings.backend.toggleMotion() }
        ActionButton { x: 45; y: 300; width: 650; visible: false; text: "Limpiar filtros de las bibliotecas"; onClicked: {settings.backend.clearFilters();settings.message="Filtros restablecidos. Tus favoritos se conservan."} }
        Row { x: 45; y: 330; spacing: 30; visible: settings.category===4
            ActionButton { width: 350; text: "Adulto · demo"; selected: settings.backend.profile==="adult"; onClicked: settings.backend.setProfile("adult") }
            ActionButton { width: 350; text: "Infantil · demo"; selected: settings.backend.profile==="child"; onClicked: settings.backend.setProfile("child") }
        }
        Column { x: 40; y: 110; spacing: 14; visible: settings.category===3; width: 1220
            ActionButton { text: "Emuladores / carpetas…"; onClicked: dolphinSetup.open() }
            ActionButton { text: "Importar juego"; onClicked: settings.importRequested() }
            DarkCombo { id: games; width: 1100; model: settings.backend.managedGames; textRole: "title"; onActivated: {var e=model[currentIndex];settings.selectedGame=e.id;editName.text=e.name;editPlatform.text=e.platform;editPath.text=e.executable;editArgs.text=e.arguments} }
            Row { spacing: 15
                DarkField { id: editName; width: 550; placeholderText: "Nombre" }
                DarkField { id: editPlatform; width: 550; placeholderText: "Plataforma" }
            }
            DarkField { id: editPath; width: 1120; placeholderText: "Ruta del ejecutable" }
            DarkField { id: editArgs; width: 1120; placeholderText: "Configuración avanzada · Argumentos JSON" }
            Row { spacing: 15
                ActionButton { width: 260; text: "Guardar edición"; onClicked: settings.backend.editGame(settings.selectedGame,editName.text,editPlatform.text,editPath.text,editArgs.text) }
                ActionButton { width: 260; text: "Ocultar"; onClicked: settings.backend.hideGame(settings.selectedGame,true) }
                ActionButton { width: 260; text: "Mostrar"; onClicked: settings.backend.hideGame(settings.selectedGame,false) }
            }
            Row { spacing: 15
                ActionButton { width: 260; text: "Carátula…"; onClicked: settings.artworkRequested(settings.selectedGame,"cover") }
                ActionButton { width: 260; text: "Fondo…"; onClicked: settings.artworkRequested(settings.selectedGame,"backdrop") }
                ActionButton { width: 260; text: "Metadatos…"; onClicked: metadataEditor.open() }
            }
        }
        ActionButton { x: 900; y: 580; visible: settings.category===3; text: "Quitar de biblioteca…"; onClicked: removal.open() }
        Popup { id: dolphinSetup; x: 50; y: 20; width: 1150; height: 800; modal: true
            background: Rectangle {color: "#142333";radius: 18; border.color: "#a8f3de"}
            Column { spacing: 20; width: parent.width
                Label { color: "#edf5f8"; text: "Emuladores · Dolphin (Wii/GameCube), PCSX2 (PS2)" }
                DarkCombo { id: emulatorChoice; width: 1050; model: ["dolphin","pcsx2"] }
                DarkField { id: dolphinPath; width: 1050; placeholderText: "Ruta del ejecutable del emulador" }
                DarkField { id: romRoot; width: 1050; placeholderText: "Carpeta principal de ROMs (contiene Wii y GameCube)" }
                ActionButton { text: "Guardar configuración"; onClicked: settings.backend.configureEmulator(emulatorChoice.currentText,dolphinPath.text,romRoot.text) }
                ActionButton { text: "Escanear ahora"; onClicked: settings.backend.scanEmulator(emulatorChoice.currentText) }
                Text { width: 1050; wrapMode: Text.Wrap; text: settings.backend.operationMessage; color: "#edf5f8" }
                Text { color: "#edf5f8"; text: "Selecciona primero un juego en Biblioteca para asociar su perfil." }
                DarkField { id: profileReference; width: 1050; placeholderText: "Perfil INI existente (no se modifica)" }
                ActionButton { text: "Asociar perfil"; onClicked: settings.backend.associateControlProfile(settings.selectedGame,profileReference.text) }
                ActionButton { text: "Cerrar"; onClicked: dolphinSetup.close() }
            }
        }
        FileDialog { id: controlProfilePicker; title: "Importar perfil INI existente"; nameFilters: ["Perfiles INI (*.ini)"]; onAccepted: settings.backend.captureControllerProfile(selectedFile.toString(),controlEngine.currentValue,controlFamily.currentValue) }
        FileDialog { id: controlTargetPicker; title: "Selecciona WiimoteNew.ini existente"; nameFilters: ["Configuración Dolphin (*.ini)"]; onAccepted: settings.backend.configureControllerTarget(selectedFile.toString()) }
        Popup {
            id: controllerPopup; objectName: "controllerManager"; x: 80; y: -65; width: 1150; height: 845; padding: 30; modal: true; focus: true
            onOpened: {settings.backend.refreshControllers(); deviceChoice.forceActiveFocus()}
            Timer { interval: 3000; repeat: true; running: controllerPopup.opened; onTriggered: if(!deviceChoice.popup.visible)settings.backend.pollControllers() }
            background: Rectangle { radius: 18; color: "#10202d"; border.color: "#a8f3de" }
            Column {
                spacing: 12; width: parent.width
                Text { text: "Mandos y perfiles"; color: "#edf5f8"; font.pixelSize: 32 }
                Text { text: "Mueve ↑↓ entre campos y ←→ para elegir. Importa el perfil Joy-Con probado desde Dolphin."; width: parent.width; wrapMode: Text.WordWrap; color: "#b7d2d8"; font.pixelSize: 18 }
                Row { spacing: 12
                    DarkCombo { id: deviceChoice; Keys.onDownPressed: detectController.forceActiveFocus(); Keys.onUpPressed: closeControllers.forceActiveFocus(); objectName: "controllerDevices"; width: 650; model: settings.backend.controllerDevices; textRole: "display"; Accessible.name: "Mando detectado" }
                    ActionButton { id: detectController; Keys.onUpPressed: deviceChoice.forceActiveFocus(); Keys.onDownPressed: controlEngine.forceActiveFocus(); width: 380; text: "Detectar mandos"; onClicked: settings.backend.refreshControllers() }
                }
                Row { spacing: 12
                    DarkCombo { id: controlEngine; Keys.onUpPressed: detectController.forceActiveFocus(); Keys.onDownPressed: controlFamily.forceActiveFocus(); width: 280; model: [{label:"Dolphin",value:"dolphin"},{label:"PCSX2",value:"pcsx2"},{label:"PC nativo",value:"native"}]; textRole: "label"; valueRole: "value"; Accessible.name: "Motor del perfil" }
                    DarkCombo { id: controlFamily; Keys.onUpPressed: controlEngine.forceActiveFocus(); Keys.onDownPressed: importProfile.forceActiveFocus(); width: 280; model: [{label:"Joy-Con derecho",value:"joycon-r"},{label:"Joy-Con izquierdo",value:"joycon-l"},{label:"DualSense",value:"dualsense"},{label:"Xbox",value:"xbox"},{label:"Wiimote",value:"wiimote"},{label:"Otro",value:"other"}]; textRole: "label"; valueRole: "value"; Accessible.name: "Tipo de mando del perfil" }
                    ActionButton { id: importProfile; Keys.onUpPressed: controlFamily.forceActiveFocus(); Keys.onDownPressed: controlProfile.forceActiveFocus(); width: 460; text: "Importar copia de INI…"; onClicked: controlProfilePicker.open() }
                }
                Row { spacing: 12
                    DarkCombo { id: controlProfile; Keys.onUpPressed: importProfile.forceActiveFocus(); Keys.onDownPressed: controlGame.forceActiveFocus(); width: 500; model: settings.backend.controllerProfiles; textRole: "name"; displayText: currentIndex<0 ? "Selecciona un perfil" : currentText; Accessible.name: "Perfil aprobado" }
                    DarkCombo { id: controlGame; Keys.onUpPressed: controlProfile.forceActiveFocus(); Keys.onDownPressed: controlScope.forceActiveFocus(); width: 520; model: settings.backend.managedGames; textRole: "title"; displayText: currentIndex<0 ? "Selecciona un juego" : currentText; Accessible.name: "Juego y versión" }
                }
                Row { spacing: 12
                    DarkCombo { id: controlScope; Keys.onUpPressed: controlGame.forceActiveFocus(); Keys.onDownPressed: controlPlayer.forceActiveFocus(); width: 260; model: [{label:"Este juego",value:"game"},{label:"Esta plataforma",value:"platform"},{label:"Predeterminado",value:"default"}]; textRole: "label"; valueRole: "value"; Accessible.name: "Ámbito: juego, plataforma o predeterminado" }
                    DarkCombo { id: controlPlayer; Keys.onUpPressed: controlScope.forceActiveFocus(); Keys.onDownPressed: {if(bindProfile.enabled)bindProfile.forceActiveFocus();else controlTarget.forceActiveFocus()} width: 180; model: ["1","2","3","4"]; Accessible.name: "Jugador" }
                    ActionButton { id: bindProfile; Keys.onUpPressed: controlPlayer.forceActiveFocus(); Keys.onDownPressed: controlTarget.forceActiveFocus(); width: 580; text: "Asociar perfil al mando"; enabled: deviceChoice.currentIndex>=0 && controlProfile.currentIndex>=0 && controlGame.currentIndex>=0; onClicked: {var d=settings.backend.controllerDevices[deviceChoice.currentIndex];var p=settings.backend.controllerProfiles[controlProfile.currentIndex];var g=settings.backend.managedGames[controlGame.currentIndex];settings.backend.bindControllerProfile(p.id,g.id,controlScope.currentValue,d.device_id,d.family,parseInt(controlPlayer.currentText))} }
                }
                Row { spacing: 12
                    ActionButton { id: controlTarget; Keys.onUpPressed: {if(bindProfile.enabled)bindProfile.forceActiveFocus();else controlPlayer.forceActiveFocus()} Keys.onDownPressed: controlApply.forceActiveFocus(); width: 500; text: "Elegir configuración Dolphin…"; onClicked: controlTargetPicker.open() }
                    ActionButton { id: controlApply; Keys.onUpPressed: controlTarget.forceActiveFocus(); Keys.onDownPressed: recoverButton.forceActiveFocus(); width: 520; text: "Aplicación temporal: "+(settings.backend.controllerAutoApply?"activada":"desactivada"); onClicked: controlConsent.open() }
                }
                Text { width: parent.width; height: 90; wrapMode: Text.WordWrap; elide: Text.ElideRight; maximumLineCount: 4; text: settings.backend.operationMessage; color: "#a8f3de"; font.pixelSize: 19 }
                Row { spacing: 12
                    ActionButton { id: recoverButton; Keys.onUpPressed: controlApply.forceActiveFocus(); Keys.onDownPressed: closeControllers.forceActiveFocus(); width: 500; text: "Recuperar respaldo…"; onClicked: recoveryConsent.open() }
                    ActionButton { id: closeControllers; Keys.onUpPressed: recoverButton.forceActiveFocus(); Keys.onDownPressed: deviceChoice.forceActiveFocus(); width: 300; text: "Cerrar"; onClicked: controllerPopup.close() }
                }
            }
            Popup { id: recoveryConsent; onOpened: cancelRecovery.forceActiveFocus(); x: 100; y: 120; width: 900; height: 300; modal: true; focus: true
                background: Rectangle { color: "#182d37"; radius: 15; border.color: "#a8f3de" }
                Column { spacing: 20; width: parent.width
                    Text { width: 820; wrapMode: Text.WordWrap; color: "#edf5f8"; font.pixelSize: 22; text: "Cierra Dolphin completamente antes de recuperar el respaldo. Si el archivo cambió, ORVEX conservará ambos y mostrará la ruta de la copia." }
                    ActionButton { id: acceptRecovery; KeyNavigation.down: cancelRecovery; KeyNavigation.up: cancelRecovery; text: "Dolphin cerrado · Recuperar"; onClicked: {settings.backend.retryControllerRecovery();recoveryConsent.close()} }
                    ActionButton { id: cancelRecovery; KeyNavigation.down: acceptRecovery; KeyNavigation.up: acceptRecovery; text: "Cancelar"; onClicked: recoveryConsent.close() }
                }
            }
            Popup { id: controlConsent; onOpened: cancelControlConsent.forceActiveFocus(); x: 100; y: 120; width: 900; height: 370; modal: true; focus: true
                background: Rectangle { color: "#182d37"; radius: 15; border.color: "#a8f3de" }
                Column { spacing: 20; width: parent.width
                    Text { width: 820; wrapMode: Text.WordWrap; color: "#edf5f8"; font.pixelSize: 22; text: "La aplicación temporal modifica WiimoteNew.ini durante el juego. Se guarda una copia antes y se intenta restaurar al salir. Solo se admiten copias completas sin índices SDL variables; ante conflictos se conserva el archivo actual." }
                    ActionButton { id: acceptControlConsent; KeyNavigation.down: cancelControlConsent; KeyNavigation.up: cancelControlConsent; text: "Confirmar cambio"; onClicked: {settings.backend.toggleControllerAutoApply();controlConsent.close()} }
                    ActionButton { id: cancelControlConsent; KeyNavigation.down: acceptControlConsent; KeyNavigation.up: acceptControlConsent; text: "Cancelar"; onClicked: controlConsent.close() }
                }
            }
        }
        Popup { id: metadataEditor; x: 100; y: 20; width: 1100; height: 600; modal: true
            Column { spacing: 20; width: parent.width
                Label { text: "Propuesta local JSON. No es una búsqueda en Internet." }
                TextArea { id: proposal; width: 1000; height: 180; text: '{"description":"","genre":"","year":2026,"edition":"","source":"local"}' }
                ActionButton { text: "Revisar propuesta"; onClicked: review.text=settings.backend.proposeMetadata(settings.selectedGame,proposal.text) }
                TextArea { id: review; width: 1000; height: 150; readOnly: true }
                ActionButton { text: "Confirmar reemplazo"; onClicked: {settings.backend.confirmMetadata();metadataEditor.close()} }
            }
        }
        Popup { id: removal; x: 120; y: 150; width: 1000; height: 350; modal: true
            Column { spacing: 20
                Label { text: "Quitar referencia. Nunca se borrarán juegos ni partidas." }
                CheckBox { id: keepHistory; checked: true; text: "Conservar historial de sesiones" }
                ActionButton { text: "Confirmar retirada"; onClicked: {settings.backend.removeGame(settings.selectedGame,keepHistory.checked);removal.close()} }
                ActionButton { text: "Cancelar"; onClicked: removal.close() }
            }
        }
        ScrollView { x: 40; y: 220; width: 1200; height: 380; visible: settings.category===5
            TextArea { text: settings.backend.operationMessage+"\n\n"+settings.backend.diagnosticReport; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; font.pixelSize: 18 }
        }
        Text { x: 45; y: 500; width: 1200; text: settings.message; color: "#a8f3de"; font.pixelSize: 24; wrapMode: Text.WordWrap }
    }
}
