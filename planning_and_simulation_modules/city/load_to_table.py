import os
import os.path

from PyQt5.QtGui import QColor, QPixmap, QIcon, QBrush
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit


def insert_toTable(table, ncol, list):
    if ncol == 1:
        cell = QTableWidgetItem(str(list[0]) + " %")
        cell1 = QTableWidgetItem(str(list[1]) + " %")
        cell2 = QTableWidgetItem(str(list[2]) + " %")
        cell3 = QTableWidgetItem(str(list[3]) + " %")
        cell4 = QTableWidgetItem(str(list[4]) + " %")
        cell5 = QTableWidgetItem(str(list[5]) + " %")
        cell6 = QTableWidgetItem(str(list[6]) + " %")
        cell7 = QTableWidgetItem(str(list[7]) + " %")
        cell8 = QTableWidgetItem(str(list[8]) + " %")
        cell9 = QTableWidgetItem(str(list[9]) + " %")
        cell10 = QTableWidgetItem(str(list[10]) + " %")
        cell11 = QTableWidgetItem(str(list[11]) + " %")
        cell12 = QTableWidgetItem(str(list[12]) + " %")
        cell13 = QTableWidgetItem(str(list[13]) + " %")
        cell14 = QTableWidgetItem(str(list[14]) + " %")

    else:
        cell = QTableWidgetItem(str(list[0]))
        cell1 = QTableWidgetItem(str(list[1]))
        cell2 = QTableWidgetItem(str(list[2]))
        cell3 = QTableWidgetItem(str(list[3]))
        cell4 = QTableWidgetItem(str(list[4]))
        cell5 = QTableWidgetItem(str(list[5]))
        cell6 = QTableWidgetItem(str(list[6]))
        cell7 = QTableWidgetItem(str(list[7]))
        cell8 = QTableWidgetItem(str(list[8]))
        cell9 = QTableWidgetItem(str(list[9]))
        cell10 = QTableWidgetItem(str(list[10]))
        cell11 = QTableWidgetItem(str(list[11]))
        cell12 = QTableWidgetItem(str(list[12]))
        cell13 = QTableWidgetItem(str(list[13]))
        cell14 = QTableWidgetItem(str(list[14]))

    cell.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(2, ncol, cell)

    cell1.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(3, ncol, cell1)

    cell2.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(4, ncol, cell2)

    cell3.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(5, ncol, cell3)

    cell4.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(7, ncol, cell4)

    cell5.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(8, ncol, cell5)

    cell6.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(9, ncol, cell6)

    cell7.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(10, ncol, cell7)

    cell8.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(11, ncol, cell8)

    cell9.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(13, ncol, cell9)

    cell10.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(14, ncol, cell10)

    cell11.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(16, ncol, cell11)

    cell12.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(18, ncol, cell12)

    cell13.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(20, ncol, cell13)

    cell14.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem(22, ncol, cell14)

def insert_toTableCool(table, ncol, list):

        if ncol == 1:
            cell = QTableWidgetItem(str(list[0]) + " %")
            cell1 = QTableWidgetItem(str(list[1]) + " %")
            cell2 = QTableWidgetItem(str(list[2]) + " %")
            cell3 = QTableWidgetItem(str(list[3]) + " %")
            cell4 = QTableWidgetItem(str(list[4]) + " %")
            cell5 = QTableWidgetItem(str(list[5]) + " %")
            cell6 = QTableWidgetItem(str(list[6]) + " %")
            cell7 = QTableWidgetItem(str(list[7]) + " %")

        else:
            cell = QTableWidgetItem(str(list[0]))
            cell1 = QTableWidgetItem(str(list[1]))
            cell2 = QTableWidgetItem(str(list[2]))
            cell3 = QTableWidgetItem(str(list[3]))
            cell4 = QTableWidgetItem(str(list[4]))
            cell5 = QTableWidgetItem(str(list[5]))
            cell6 = QTableWidgetItem(str(list[6]))
            cell7 = QTableWidgetItem(str(list[7]))


        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(2, ncol, cell)

        cell1.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(3, ncol, cell1)

        cell2.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(4, ncol, cell2)

        cell3.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(6, ncol, cell3)

        cell4.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(7, ncol, cell4)

        cell5.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(8, ncol, cell5)

        cell6.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(10, ncol, cell6)

        cell7.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(12, ncol, cell7)


def table_and_check(table, lista_In, nCol):
    table = table
    tot = sum(lista_In)
    ref = 100
    ref2 = tot
    dif34 = tot - ref2
    dif012 = tot - ref

    if nCol == 3 or nCol == 4:
        table.setItem(0, nCol, QTableWidgetItem(str(round(tot, 2))))
        table.setItem(1, nCol, QTableWidgetItem(str(round(ref2, 2)) + " %"))
        table.setItem(2, nCol, QTableWidgetItem(str(round(dif34, 2))))
    if nCol == 0 or nCol == 1 or nCol == 2:
        table.setItem(0, nCol, QTableWidgetItem(str(round(tot, 2)) + " %"))
        table.setItem(1, nCol, QTableWidgetItem(str(ref) + " %"))
        table.setItem(2, nCol, QTableWidgetItem(str(round(dif012, 2))))


    if dif34 == float(0.0) or dif012 == float(0.0):
        val = "ok!"
        table.setItem(3, nCol, QTableWidgetItem(str(val)))
        table.item(3, nCol).setForeground(QColor(0, 255, 0))
    else:
        val = " Wrong!"
        table.setItem(3, nCol, QTableWidgetItem(str(val)))
        table.item(3, nCol).setForeground(QColor(0, 255, 0))


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