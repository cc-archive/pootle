# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ratha/sourceforge.net/translate/trunk/pootling/ui/FindFile.ui'
#
# Created: Mon Apr  9 14:47:29 2007
#      by: PyQt4 UI code generator 4-snapshot-20070212
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,378,165).size()).expandedTo(Form.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Form)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.frame = QtGui.QFrame(Form)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.gridlayout1 = QtGui.QGridLayout(self.frame)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.label = QtGui.QLabel(self.frame)
        self.label.setFrameShape(QtGui.QFrame.StyledPanel)
        self.label.setObjectName("label")
        self.gridlayout1.addWidget(self.label,0,1,1,1)

        self.btnAdd = QtGui.QPushButton(self.frame)
        self.btnAdd.setObjectName("btnAdd")
        self.gridlayout1.addWidget(self.btnAdd,1,2,1,1)

        self.btnFind = QtGui.QPushButton(self.frame)
        self.btnFind.setObjectName("btnFind")
        self.gridlayout1.addWidget(self.btnFind,2,2,1,1)

        self.listWidget = QtGui.QListWidget(self.frame)
        self.listWidget.setObjectName("listWidget")
        self.gridlayout1.addWidget(self.listWidget,1,0,3,2)

        self.btnDelete = QtGui.QPushButton(self.frame)
        self.btnDelete.setObjectName("btnDelete")
        self.gridlayout1.addWidget(self.btnDelete,3,2,1,1)

        self.lblfind = QtGui.QLabel(self.frame)

        font = QtGui.QFont(self.lblfind.font())
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.lblfind.setFont(font)
        self.lblfind.setObjectName("lblfind")
        self.gridlayout1.addWidget(self.lblfind,0,0,1,1)
        self.gridlayout.addWidget(self.frame,0,0,1,1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("Form", "&Add", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setShortcut(QtGui.QApplication.translate("Form", "Ctrl+F", None, QtGui.QApplication.UnicodeUTF8))
        self.btnFind.setText(QtGui.QApplication.translate("Form", "&Find", None, QtGui.QApplication.UnicodeUTF8))
        self.btnFind.setShortcut(QtGui.QApplication.translate("Form", "Ctrl+F", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDelete.setText(QtGui.QApplication.translate("Form", "&Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDelete.setShortcut(QtGui.QApplication.translate("Form", "Ctrl+F", None, QtGui.QApplication.UnicodeUTF8))
        self.lblfind.setText(QtGui.QApplication.translate("Form", "Find File:", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
