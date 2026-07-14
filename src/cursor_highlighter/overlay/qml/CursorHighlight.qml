import QtQuick
import QtQuick.Window
import org.kde.layershell 1.0 as LayerShellQt

Item {
    id: root

    Repeater {
        model: screenList

        delegate: Window {
            id: screenWindow
            required property var modelData

            visible: cursorState.highlightVisible
            color: "transparent"
            flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput

            screen: modelData
            LayerShellQt.Window.screenConfiguration: LayerShellQt.Window.ScreenFromQWindow
            LayerShellQt.Window.layer: LayerShellQt.Window.LayerOverlay
            LayerShellQt.Window.anchors: LayerShellQt.Window.AnchorTop
                | LayerShellQt.Window.AnchorBottom
                | LayerShellQt.Window.AnchorLeft
                | LayerShellQt.Window.AnchorRight
            LayerShellQt.Window.exclusionZone: -1
            LayerShellQt.Window.keyboardInteractivity: LayerShellQt.Window.KeyboardInteractivityNone

            Rectangle {
                x: cursorState.x - Screen.virtualX - width / 2
                y: cursorState.y - Screen.virtualY - height / 2
                width: cursorState.size
                height: cursorState.size
                radius: width / 2
                color: cursorState.shape === "ring" ? "transparent" : cursorState.color
                border.width: cursorState.shape === "ring" ? cursorState.ringThickness : 0
                border.color: cursorState.color
                opacity: cursorState.opacity
            }

            Rectangle {
                id: ripple
                x: cursorState.x - Screen.virtualX - width / 2
                y: cursorState.y - Screen.virtualY - height / 2
                width: 10
                height: 10
                radius: width / 2
                color: "transparent"
                border.width: 4
                border.color: "#ffffff"
                opacity: 0

                ParallelAnimation {
                    id: rippleAnim
                    NumberAnimation { target: ripple; property: "width"; from: 10; to: cursorState.size * 2.3; duration: 400; easing.type: Easing.OutQuad }
                    NumberAnimation { target: ripple; property: "height"; from: 10; to: cursorState.size * 2.3; duration: 400; easing.type: Easing.OutQuad }
                    NumberAnimation { target: ripple; property: "opacity"; from: 0.8; to: 0; duration: 400; easing.type: Easing.OutQuad }
                }

                Connections {
                    target: cursorState
                    function onLeftClickPulse() {
                        ripple.border.color = cursorState.leftClickColor
                        rippleAnim.restart()
                    }
                    function onRightClickPulse() {
                        ripple.border.color = cursorState.rightClickColor
                        rippleAnim.restart()
                    }
                }
            }
        }
    }
}
