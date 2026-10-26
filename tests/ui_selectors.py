"""Find named QML controls in the visual tree, including Repeater delegates."""
from PySide6.QtQuick import QQuickItem


def find_item(window, name):
    pending = [window.contentItem()]
    while pending:
        item = pending.pop()
        if item.objectName() == name:
            return item
        pending.extend(child for child in item.childItems() if isinstance(child, QQuickItem))
    raise AssertionError("QML control not found: " + name)
