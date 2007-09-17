# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ratha/sourceforge.net/translate/trunk/pootling/ui/page.ui'
#
# Created: Tue May  8 10:22:02 2007
#      by: PyQt4 UI code generator 4-snapshot-20070212
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_page2(object):
    def setupUi(self, page2):
        page2.setObjectName("page2")
        page2.resize(QtCore.QSize(QtCore.QRect(0,0,388,238).size()).expandedTo(page2.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(page2)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.label = QtGui.QLabel(page2)

        font = QtGui.QFont(self.label.font())
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,1)

        self.frame = QtGui.QFrame(page2)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.gridlayout1 = QtGui.QGridLayout(self.frame)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.chbSubinDirectory = QtGui.QCheckBox(self.frame)
        self.chbSubinDirectory.setObjectName("chbSubinDirectory")
        self.gridlayout1.addWidget(self.chbSubinDirectory,3,0,1,1)

        self.listWidget = QtGui.QListWidget(self.frame)
        self.listWidget.setObjectName("listWidget")
        self.gridlayout1.addWidget(self.listWidget,0,0,3,1)

        self.btnDelete = QtGui.QPushButton(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDelete.sizePolicy().hasHeightForWidth())
        self.btnDelete.setSizePolicy(sizePolicy)
        self.btnDelete.setIcon(QtGui.QIcon("../images/removeTM.png"))
        self.btnDelete.setObjectName("btnDelete")
        self.gridlayout1.addWidget(self.btnDelete,1,1,1,1)

        self.btnAdd = QtGui.QPushButton(self.frame)
        self.btnAdd.setIcon(QtGui.QIcon("../images/addTM.png"))
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout1.addWidget(self.btnAdd,0,1,1,1)

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem,2,1,2,1)
        self.gridlayout.addWidget(self.frame,1,0,1,1)

        self.retranslateUi(page2)
        QtCore.QMetaObject.connectSlotsByName(page2)

    def retranslateUi(self, page2):
        page2.setWindowTitle(QtGui.QApplication.translate("page2", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("page2", "Add item to list widget", None, QtGui.QApplication.UnicodeUTF8))
        self.chbSubinDirectory.setText(QtGui.QApplication.translate("page2", "Sub In Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.listWidget.setWhatsThis(QtGui.QApplication.translate("page2", "Listwidget is displayed items from user add files or folders.", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDelete.setToolTip(QtGui.QApplication.translate("page2", "Delete TM", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDelete.setWhatsThis(QtGui.QApplication.translate("page2", "You can delete po, xliff files or another folders of files from listwidget.", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDelete.setText(QtGui.QApplication.translate("page2", " De&lete", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setToolTip(QtGui.QApplication.translate("page2", "Add TM", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setWhatsThis(QtGui.QApplication.translate("page2", "You can add po, xliff files or another folders of files on your local into listwidget.", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("page2", " &Add", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    page2 = QtGui.QWidget()
    ui = Ui_page2()
    ui.setupUi(page2)
    page2.show()
    sys.exit(app.exec_())
