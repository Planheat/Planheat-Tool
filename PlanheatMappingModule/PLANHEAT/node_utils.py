import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QBrush, QFont
from PyQt5.QtWidgets import QTreeWidgetItemIterator, QTreeWidgetItem
from .enums import AlgorithmEnum

def add_node(tree, db_node):
    if db_node.main_node_id is not None:
        parent_node = find_parent_node(tree, db_node.main_node_id)
        if parent_node:
            node = QTreeWidgetItem(parent_node)
        else:
            return db_node
    else:
        node = QTreeWidgetItem(tree)
    node.setData(0, Qt.UserRole, db_node)
    node.setFlags(node.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
    node.setText(0, str(db_node.description))
    set_node_icon(node)
    if is_input_file_node(node):
        node.setFlags(node.flags() | ~Qt.ItemIsDropEnabled | ~Qt.ItemIsEditable)
    else:
        myFont = QFont()
        myFont.setBold(True)
        node.setFont(0,myFont)
        if get_node_data(node).algorithm_selection != AlgorithmEnum.SUM and (not get_node_data(node).parameters or get_node_data(node).parameters[1].value == '-1'):
            node.setForeground(0, QBrush(Qt.lightGray))
        else:
            node.setForeground(0, QBrush(Qt.black))
    if db_node.selected == 1:
        node.setCheckState(0, Qt.Checked)
    else:
        node.setCheckState(0, Qt.Unchecked)

    node.setExpanded(True)
    return None


def set_node_icon(node):
    node_data = get_node_data(node)
    icon_prefix = os.path.dirname(os.path.realpath(__file__)) + "/icons/"
    icon_suffix = ".jpg"

    if node_data.icon is not None:
        node.setIcon(0, QIcon(icon_prefix + node_data.icon + icon_suffix))
    elif node_data.algorithm_id is not None:
        node.setIcon(0, QIcon(icon_prefix + node_data.algorithm.icon + icon_suffix))

def find_parent_node(tree, parent_id):
    iterator = QTreeWidgetItemIterator(tree)
    while iterator.value():
        node = iterator.value()
        if get_node_data(node).node_id == parent_id:
            return node
        iterator += 1
    return None


def get_node_data(node):
    return node.data(0, Qt.UserRole)


def is_checked(node):
    if node.checkState(0) == Qt.Checked or node.checkState(0) == Qt.PartiallyChecked:
        return True
    return False


def delete_node(node):
    node.parent().removeChild(node)


def has_checked_input_file_node_children(node):
    iterator = QTreeWidgetItemIterator(node)
    while iterator.value():
        child_node = iterator.value()
        node_data = get_node_data(child_node)
        if node_data.map_selection or node_data.file:
            return True
        iterator += 1
    return False


def is_algorithm_node(node):
    return get_node_data(node).algorithm_id


def is_input_file_node(node):
    return (get_node_data(node).map_selection or get_node_data(node).file)  and not get_node_data(node).algorithm_id


def count_items(tree):
    count = 1
    for i in range(tree.invisibleRootItem().childCount()):
        count += 1
        count += count_child_items(tree.invisibleRootItem().child(i))
    return count


def count_child_items(node):
    count = 0
    for i in range(node.childCount()):
        if is_algorithm_node(node.child(i)):
            count += count_child_items(node.child(i))
    count += 1
    return count
