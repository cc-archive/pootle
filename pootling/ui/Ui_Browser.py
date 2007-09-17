# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ratha/sourceforge.net/translate/trunk/pootling/ui/Browser.ui'
#
# Created: Fri Apr  6 15:28:38 2007
#      by: PyQt4 UI code generator 4-snapshot-20070212
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,520,296).size()).expandedTo(Dialog.minimumSizeHint()))
        Dialog.setModal(False)

        self.gridlayout = QtGui.QGridLayout(Dialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setObjectName("btnClose")
        self.gridlayout.addWidget(self.btnClose,2,3,1,1)

        spacerItem = QtGui.QSpacerItem(91,28,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,2,1,1,1)

        self.lineLocation = QtGui.QLineEdit(Dialog)
        self.lineLocation.setObjectName("lineLocation")
        self.gridlayout.addWidget(self.lineLocation,1,1,1,3)

        self.treeView = QtGui.QTreeView(Dialog)
        self.treeView.setObjectName("treeView")
        self.gridlayout.addWidget(self.treeView,0,1,1,3)

        self.btnOk = QtGui.QPushButton(Dialog)
        self.btnOk.setObjectName("btnOk")
        self.gridlayout.addWidget(self.btnOk,2,2,1,1)

        self.frame = QtGui.QFrame(Dialog)
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setLineWidth(1)
        self.frame.setObjectName("frame")

        self.gridlayout1 = QtGui.QGridLayout(self.frame)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem1,3,0,1,1)

        self.btnDesktop = QtGui.QPushButton(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDesktop.sizePolicy().hasHeightForWidth())
        self.btnDesktop.setSizePolicy(sizePolicy)
        self.btnDesktop.setIcon(QtGui.QIcon("../images/desktop.png"))
        self.btnDesktop.setIconSize(QtCore.QSize(32,32))
        self.btnDesktop.setFlat(True)
        self.btnDesktop.setObjectName("btnDesktop")
        self.gridlayout1.addWidget(self.btnDesktop,1,0,1,1)

        self.btnHome = QtGui.QPushButton(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnHome.sizePolicy().hasHeightForWidth())
        self.btnHome.setSizePolicy(sizePolicy)
        self.btnHome.setIcon(QtGui.QIcon("../images/folder_home.png"))
        self.btnHome.setIconSize(QtCore.QSize(32,32))
        self.btnHome.setFlat(True)
        self.btnHome.setObjectName("btnHome")
        self.gridlayout1.addWidget(self.btnHome,0,0,1,1)

        self.btnDoc = QtGui.QPushButton(self.frame)
        self.btnDoc.setIcon(QtGui.QIcon("../images/document.png"))
        self.btnDoc.setIconSize(QtCore.QSize(32,32))
        self.btnDoc.setAutoDefault(True)
        self.btnDoc.setFlat(True)
        self.btnDoc.setObjectName("btnDoc")
        self.gridlayout1.addWidget(self.btnDoc,2,0,1,1)
        self.gridlayout.addWidget(self.frame,0,0,2,1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.btnHome,self.btnDesktop)
        Dialog.setTabOrder(self.btnDesktop,self.btnDoc)
        Dialog.setTabOrder(self.btnDoc,self.treeView)
        Dialog.setTabOrder(self.treeView,self.lineLocation)
        Dialog.setTabOrder(self.lineLocation,self.btnOk)
        Dialog.setTabOrder(self.btnOk,self.btnClose)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Select a file or a location", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Dialog", "&Close", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOk.setText(QtGui.QApplication.translate("Dialog", "&Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDesktop.setToolTip(QtGui.QApplication.translate("Dialog", "go to Desktop folder", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDesktop.setText(QtGui.QApplication.translate("Dialog", " &Desktop", None, QtGui.QApplication.UnicodeUTF8))
        self.btnHome.setToolTip(QtGui.QApplication.translate("Dialog", "go to Home folder", None, QtGui.QApplication.UnicodeUTF8))
        self.btnHome.setText(QtGui.QApplication.translate("Dialog", " &Home", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDoc.setToolTip(QtGui.QApplication.translate("Dialog", "go to Document folder", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDoc.setText(QtGui.QApplication.translate("Dialog", " Docu&ments", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
