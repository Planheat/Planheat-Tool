import os
import os.path

from PyQt5.QtGui import QColor, QPixmap, QIcon, QBrush
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit


def insert_toTable(table, ncol, list):
    flag = QtCore.Qt.ItemIsEnabled
    empty_item = QTableWidgetItem()
    empty_item.setFlags(flag)
    cell = []
    if ncol == 1:
        for i in range(15):
            try:
                cell.append(QTableWidgetItem(str(list[i]) + " %"))
                cell[i].setFlags(flag)
            except Exception:
                cell.append(empty_item.clone())
    else:
        for i in range(15):
            try:
                cell.append(QTableWidgetItem(str(list[i])))
                cell[i].setFlags(flag)
            except Exception:
                cell.append(empty_item.clone())

    table.setItem(2, ncol, cell[0])
    table.setItem(3, ncol, cell[1])
    table.setItem(4, ncol, cell[2])
    table.setItem(5, ncol, cell[3])
    table.setItem(7, ncol, cell[4])
    table.setItem(8, ncol, cell[5])
    table.setItem(9, ncol, cell[6])
    table.setItem(10, ncol, cell[7])
    table.setItem(11, ncol, cell[8])
    table.setItem(13, ncol, cell[9])
    table.setItem(14, ncol, cell[10])
    table.setItem(16, ncol, cell[11])
    table.setItem(18, ncol, cell[12])
    table.setItem(20, ncol, cell[13])
    table.setItem(22, ncol, cell[14])


def insert_toTableCool(table, ncol, list):
    flag = QtCore.Qt.ItemIsEnabled
    empty_item = QTableWidgetItem()
    empty_item.setFlags(flag)
    cell = []

    if ncol == 1:
        for i in range(8):
            try:
                cell.append(QTableWidgetItem(str(list[i]) + " %"))
                cell[i].setFlags(flag)
            except Exception:
                cell.append(empty_item.clone())
    else:
        for i in range(15):
            try:
                cell.append(QTableWidgetItem(str(list[i])))
                cell[i].setFlags(flag)
            except Exception:
                cell.append(empty_item.clone())

    table.setItem(2, ncol, cell[0])
    table.setItem(3, ncol, cell[1])
    table.setItem(4, ncol, cell[2])
    table.setItem(6, ncol, cell[3])
    table.setItem(7, ncol, cell[4])
    table.setItem(8, ncol, cell[5])
    table.setItem(10, ncol, cell[6])
    table.setItem(12, ncol, cell[7])


def table_and_check(table, lista_In, nCol):
    table = table
    tot = sum(lista_In)
    ref = 100
    ref2 = tot
    dif34 = tot - ref2
    dif012 = tot - ref

    flag = QtCore.Qt.ItemIsEnabled

    if nCol == 3 or nCol == 4:
        table.setItem(0, nCol, QTableWidgetItem(str(round(tot, 2))))
        table.setItem(1, nCol, QTableWidgetItem(str(round(ref2, 2)) + " %"))
        table.setItem(2, nCol, QTableWidgetItem(str(round(dif34, 2))))
        table.item(0, nCol).setFlags(flag)
        table.item(1, nCol).setFlags(flag)
        table.item(2, nCol).setFlags(flag)

    if nCol == 0 or nCol == 1 or nCol == 2:
        table.setItem(0, nCol, QTableWidgetItem(str(round(tot, 2)) + " %"))
        table.setItem(1, nCol, QTableWidgetItem(str(ref) + " %"))
        table.setItem(2, nCol, QTableWidgetItem(str(round(dif012, 2))))
        table.item(0, nCol).setFlags(flag)
        table.item(1, nCol).setFlags(flag)
        table.item(2, nCol).setFlags(flag)


    if dif34 == float(0.0) or dif012 == float(0.0):
        val = "ok!"
        table.setItem(3, nCol, QTableWidgetItem(str(val)))
        table.item(3, nCol).setForeground(QColor(0, 255, 0))
        table.item(3, nCol).setFlags(flag)
    else:
        val = " Wrong!"
        table.setItem(3, nCol, QTableWidgetItem(str(val)))
        table.item(3, nCol).setForeground(QColor(0, 255, 0))
        table.item(3, nCol).setFlags(flag)


def copy_table(tab_in, tab_dest, col_in, col_dest):
    source = tab_in
    target = tab_dest
    for i in range(source.rowCount()):
        item = source.item(i, col_in)
        try:
            target.setItem(i, col_dest, QTableWidgetItem(item)) #QTableWidgetItem(item).setForeground(QColor(0, 0, 0)))
        except:
            pass


def calculate_fec(fec, avg, ued):
    # b =ued Col 0 # c =  avg col 1 # f = fec calcolata prima col4
    dh_losses_cool = []
    for f in fec:
        for c in avg:
            for b in ued:
                loss = round((f * c - b), 2)
                dh_losses_cool.append(loss)
    return dh_losses_cool

def calcola_tot_perc(table, col):
    list = []
    for i in range(table.rowCount()):
        try:
            val = float((table.item(i, col)).text())
            list.append(val)
        except:
            pass

    tot_perc_input = round(sum(list),2)
    if tot_perc_input >= 100.0:
        tot_perc_input.setForeground(QColor(0, 255, 0))
    else:
        tot_perc_input.setForeground(QColor(255, 0, 0))
    return tot_perc_input

def calcola_tot(table, col):
    list = []
    for i in range(table.rowCount()):
        try:
            val = float((table.item(i, col)).text())
            list.append(val)
        except:
            pass
    tot = round(sum(list), 2)
    return tot


def calcola_prodotto(listaA,listaB):

        list=[]
        for i in listaA:
            for j in listaB:
                val = i*j
            list.append(val)

        return list

def calc_dif_pro(listaA, listaB, em_fac):
    list=[]
    for i in listaA:
        for j in listaB:
            for k in em_fac:
                val = round(((i - j) * k),2)
            list.append(val)
    return list

def insert_to_source_table(table,nCol, list):
    for i in range(table.rowCount()):
        for j in list:
            table.setItem(i, nCol, QTableWidgetItem(str(j)))



def Qdialog_save_file(folder):

    filename, ok = QInputDialog.getText(None, 'Almost Done !', 'Insert name your file .csv :')
    if ok:
        return os.path.join(folder,filename)

def updata_dic(table, filename):
    d = {}
    # with open(filename, 'wb') as f:
    for i in range(table.columnCount()):
        item_val = []
        for j in range(table.rowCount()):
            it = table.item(j, i)
            item_val.append(it.text() if it is not None else "")
        h_item = table.horizontalHeaderItem(i)
        n_column = str(i) if h_item is None else h_item.text()
        d[n_column + "_" + table.objectName()] = item_val

    updata_file(filename, d)


def updata_file(filename, d):
    try:
        with open(filename, 'a') as f:
            for key in d.keys():
                f.write("%s,%s\n" % (key, d[key]))
    except IOError:
        print("I/O error")