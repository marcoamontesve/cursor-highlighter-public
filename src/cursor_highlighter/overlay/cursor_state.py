"""Estado del cursor expuesto a QML via setContextProperty."""

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

DEFAULT_COLOR = "#ff5555"
DEFAULT_SHAPE = "circle"
DEFAULT_SIZE = 60
DEFAULT_OPACITY = 0.6
DEFAULT_RING_THICKNESS = 4
DEFAULT_LEFT_CLICK_COLOR = "#4a9eff"
DEFAULT_RIGHT_CLICK_COLOR = "#4aff8f"


class CursorState(QObject):
    xChanged = pyqtSignal()
    yChanged = pyqtSignal()
    colorChanged = pyqtSignal()
    shapeChanged = pyqtSignal()
    sizeChanged = pyqtSignal()
    opacityChanged = pyqtSignal()
    ringThicknessChanged = pyqtSignal()
    leftClickColorChanged = pyqtSignal()
    rightClickColorChanged = pyqtSignal()

    # Pulsos disparados en cada click (izq/der); QML los escucha para animar
    # el anillo de onda expansiva. No llevan datos, son solo un "trigger".
    leftClickPulse = pyqtSignal()
    rightClickPulse = pyqtSignal()

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._x = 0
        self._y = 0
        self._color = DEFAULT_COLOR
        self._shape = DEFAULT_SHAPE
        self._size = DEFAULT_SIZE
        self._opacity = DEFAULT_OPACITY
        self._ring_thickness = DEFAULT_RING_THICKNESS
        self._left_click_color = DEFAULT_LEFT_CLICK_COLOR
        self._right_click_color = DEFAULT_RIGHT_CLICK_COLOR

    def getX(self) -> int:
        return self._x

    def setX(self, value: int) -> None:
        if value != self._x:
            self._x = value
            self.xChanged.emit()

    x = pyqtProperty(int, fget=getX, fset=setX, notify=xChanged)

    def getY(self) -> int:
        return self._y

    def setY(self, value: int) -> None:
        if value != self._y:
            self._y = value
            self.yChanged.emit()

    y = pyqtProperty(int, fget=getY, fset=setY, notify=yChanged)

    @pyqtSlot(int, int)
    def updatePosition(self, x: int, y: int) -> None:
        self.setX(x)
        self.setY(y)

    def getColor(self) -> str:
        return self._color

    def setColor(self, value: str) -> None:
        if value != self._color:
            self._color = value
            self.colorChanged.emit()

    color = pyqtProperty(str, fget=getColor, fset=setColor, notify=colorChanged)

    def getShape(self) -> str:
        return self._shape

    def setShape(self, value: str) -> None:
        if value != self._shape:
            self._shape = value
            self.shapeChanged.emit()

    shape = pyqtProperty(str, fget=getShape, fset=setShape, notify=shapeChanged)

    def getSize(self) -> int:
        return self._size

    def setSize(self, value: int) -> None:
        if value != self._size:
            self._size = value
            self.sizeChanged.emit()

    size = pyqtProperty(int, fget=getSize, fset=setSize, notify=sizeChanged)

    def getOpacity(self) -> float:
        return self._opacity

    def setOpacity(self, value: float) -> None:
        if value != self._opacity:
            self._opacity = value
            self.opacityChanged.emit()

    opacity = pyqtProperty(float, fget=getOpacity, fset=setOpacity, notify=opacityChanged)

    def getRingThickness(self) -> int:
        return self._ring_thickness

    def setRingThickness(self, value: int) -> None:
        if value != self._ring_thickness:
            self._ring_thickness = value
            self.ringThicknessChanged.emit()

    ringThickness = pyqtProperty(
        int, fget=getRingThickness, fset=setRingThickness, notify=ringThicknessChanged
    )

    def getLeftClickColor(self) -> str:
        return self._left_click_color

    def setLeftClickColor(self, value: str) -> None:
        if value != self._left_click_color:
            self._left_click_color = value
            self.leftClickColorChanged.emit()

    leftClickColor = pyqtProperty(
        str, fget=getLeftClickColor, fset=setLeftClickColor, notify=leftClickColorChanged
    )

    def getRightClickColor(self) -> str:
        return self._right_click_color

    def setRightClickColor(self, value: str) -> None:
        if value != self._right_click_color:
            self._right_click_color = value
            self.rightClickColorChanged.emit()

    rightClickColor = pyqtProperty(
        str, fget=getRightClickColor, fset=setRightClickColor, notify=rightClickColorChanged
    )

    @pyqtSlot()
    def triggerLeftClick(self) -> None:
        self.leftClickPulse.emit()

    @pyqtSlot()
    def triggerRightClick(self) -> None:
        self.rightClickPulse.emit()
