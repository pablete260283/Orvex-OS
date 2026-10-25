from PySide6.QtCore import QObject, Property, Signal, Slot
from .store import catalog

class Bridge(QObject):
    changed = Signal()
    def __init__(self, store):
        super().__init__()
        self.store = store
    @Property("QVariantList", constant=True)
    def catalog(self):
        return catalog()
    @Property(bool, notify=changed)
    def reducedMotion(self):
        return self.store.get("reduced_motion", False)
    @Slot()
    def toggleMotion(self):
        self.store.set("reduced_motion", not self.reducedMotion)
        self.changed.emit()
