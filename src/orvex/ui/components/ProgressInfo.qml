import QtQuick
Item {
    id: info
    property var record: ({})
    width: 900; height: 125
    Text { text: "PROGRESO DEMO  ·  "+(record.statusLabel || "Sin información")+"  ·  "+(record.percentLabel || "Sin porcentaje disponible"); color: "#a8f3de"; font.pixelSize: 23 }
    Rectangle { y: 40; width: parent.width; height: 9; radius: 4; color: "#334552"
        Rectangle { height: parent.height; width: parent.width*Math.max(0,Math.min(100,info.record.percent || 0))/100; radius: 4; color: "#a8f3de" }
    }
    Text { y: 70; text: (record.timeLabel || "Tiempo no disponible")+" jugados  ·  Última sesión: "+(record.lastLabel || "Sin sesiones"); color: "#bdcdd8"; font.pixelSize: 21 }
}
