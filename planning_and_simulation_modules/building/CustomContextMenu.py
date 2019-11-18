from PyQt5.QtWidgets import QTreeWidget, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor


class CustomContextMenu:

    @staticmethod
    def set_building_context_menu(widget: QTreeWidget):
        widget.setContextMenuPolicy(Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(lambda pos: CustomContextMenu.open_building_menu(pos, widget))

    @staticmethod
    def open_building_menu(pos, widget):
        item = widget.itemAt(pos)
        try:
            top_level_item = item.parent().parent()
        except AttributeError:
            return
        if top_level_item is None:
            return
        menu = QMenu(widget)
        action = menu.addAction("Remove technology")
        action.triggered.connect(lambda: CustomContextMenu.erode_method(top_level_item,
                                                                        service=item.parent().text(0)))
        menu.exec_(QCursor.pos())

    @staticmethod
    def erode_method(item, service=None):
        if item is None:
            return
        for i in range(item.childCount()):
            if service is None:
                check = True
            else:
                if item.child(i).text(0) == service:
                    check = True
                else:
                    check = False
            if check:
                for j in range(item.child(i).childCount()-1, -1, -1):
                    item.child(i).removeChild(item.child(i).child(j))

    @staticmethod
    def get_top_level(item):
        if item is None:
            return None
        if item.parent() is None:
            return item
        else:
            return CustomContextMenu.get_top_level(item.parent())
