import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5 import uic
import pandas as pd
import sqlite3

con = sqlite3.connect("coffee.sqlite")
cur = con.cursor()


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

    def onClickedRow(self, index=None):
        print(index.row(), index.column(), self.messageList.data(index, QtCore.Qt.DisplayRole))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        a = [str(i + 1) for i in range(len(cur.execute("""SELECT * FROM fer""").fetchall()))]
        data = pd.DataFrame([
            list(i) for i in cur.execute("""SELECT * FROM fer""").fetchall()
        ], columns=['ID', 'сорт', 'обжарка', 'молотый/зерна', 'вкус', 'цена', 'объем'],
            index=a)

        self.model = TableModel(data)
        self.tableView.setModel(self.model)

        self.setCentralWidget(self.tableView)


class AddWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.pushButton.clicked.connect(self.add)
        self.pushButton_2.clicked.connect(self.delete)
        self.pushButton_3.clicked.connect(self.uppdate)
        self.tableView.clicked.connect(self.onClickedRow)
        self.cords = 0, 0
        self.k = 0
        self.update()

    def onClickedRow(self, index=None):
        self.cords = index.column(), index.row()
        s = list(self.data[list(self.data.keys())[index.column()]])[index.row()]
        self.lineEdit.setText(str(s))

    def uppdate(self):
        col = ['id', 'sort', 'level', 'molZ', 'opis', 'tsena', 'obem'][self.cords[0]]
        row = self.cords[1]
        t = self.lineEdit.text()
        cur.execute(f"""UPDATE fer SET {col} = '{t}' WHERE ID = {row}""")
        con.commit()
        self.update()

    def delete(self):
        cur.execute(f"""delete from fer where ID = {self.cords[1]}""")
        self.update()

    def add(self):
        cur.execute(f"""INSERT INTO fer(ID) VALUES({self.k});""")
        con.commit()
        self.update()

    def update(self):
        a = [str(i + 1) for i in range(len(cur.execute("""SELECT * FROM fer""").fetchall()))]
        self.data = pd.DataFrame([
            list(i) for i in cur.execute("""SELECT * FROM fer""").fetchall()
        ], columns=['ID', 'сорт', 'обжарка', 'молотый/зерна', 'вкус', 'цена', 'объем'],
            index=a)
        self.k = len([list(i) for i in cur.execute("""SELECT * FROM fer""").fetchall()])
        self.model = TableModel(self.data)
        self.tableView.setModel(self.model)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    if input('Чтобы попасть в режим редактирования введите что угодно\n'
             'иначе оставьте строку пустой '):
        window = AddWindow()
    else:
        window = MainWindow()
    window.show()
    app.exec_()

# ID лучше не менять
