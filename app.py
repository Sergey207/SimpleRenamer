import os
import sys

from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QListWidgetItem, QAbstractItemView, \
    QFileDialog

from Designs.mainWindow import Ui_MainWindow


def get_extension(path: str):
    if path[0] != '.':
        if os.path.isfile(path):
            if '.' in path:
                return '.' + path.split('.')[-1]
            else:
                return ''
        else:
            return 'Папка'
    else:
        return ''


class Window(QMainWindow, Ui_MainWindow):
    files = []
    ERROR_SYMBOLS = r'/\):*?"<>|'

    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)
        self.openFilesAction.triggered.connect(self.openFiles)
        self.rotateListAction.triggered.connect(self.rotateList)
        self.renameButton.clicked.connect(self.rename)
        self.nameBeforeIndex.textEdited.connect(self.nameChanged)
        self.indexSpinBox.valueChanged.connect(self.updateList)
        self.nameAfterIndex.textEdited.connect(self.nameChanged)
        self.listWidget.setDragDropMode(QAbstractItemView.InternalMove)
        self.listWidget.model().rowsMoved.connect(self.updateMovedList)
        self.updateList()

    def nameChanged(self):
        try:
            sender = self.sender()
            result = ''.join(
                list(filter(lambda x: x not in self.ERROR_SYMBOLS, list(sender.text()))))
            sender.setText(result)
            self.updateList()
        except BaseException as e:
            print('nameChanged:', e)

    def openFiles(self):
        self.files = QFileDialog.getOpenFileNames(self, "Выберите файлы для переименовывания")[0]
        self.updateList()

    def rotateList(self):
        self.files = self.files[::-1]
        self.updateList()

    def updateList(self):
        try:
            self.listWidget.clear()
            for i, file in enumerate(self.files):
                self.listWidget.addItem(
                    QListWidgetItem(
                        f'{file} -> {self.get_new_name(i + int(self.indexSpinBox.text()), file)}'))
        except BaseException as e:
            print('updateList:', e)

    def updateMovedList(self):
        try:
            self.files = []
            for i in range(self.listWidget.count()):
                self.files.append(self.listWidget.item(i).text().split(' -> ')[0])
            self.updateList()
        except BaseException as e:
            print("updateMovedList:", e)

    def get_new_name(self, index: int, file: str) -> str:
        result = []
        if self.nameBeforeIndex.text():
            result.append(self.nameBeforeIndex.text())
        result.append(str(index))
        if self.nameAfterIndex.text():
            result.append(self.nameAfterIndex.text())
        return (' '.join(result) + get_extension(file)) \
            if get_extension(file) != 'Папка' else ' '.join(result)

    def rename(self):
        for_rename = []
        for i in range(self.listWidget.count()):
            old_name, new_name = self.listWidget.item(i).text().split(' -> ')
            new_name = f"{'/'.join(old_name.split('/')[:-1])}/{new_name}"
            for_rename.append((old_name, new_name))
        self.listWidget.clear()
        for old_name, new_name in for_rename:
            try:
                os.rename(old_name, new_name)
                ok = True
            except (OSError, SystemError):
                ok = False
            new_item = QListWidgetItem(f'{old_name} -> {new_name.split("/")[-1]}')
            new_item.setForeground(QColor(0, 255, 0) if ok else QColor(255, 0, 0))
            self.listWidget.addItem(new_item)


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('Images/Rename-icon.png'))
    window = Window()
    window.setWindowIcon(QIcon('Images/Rename-icon.png'))
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
