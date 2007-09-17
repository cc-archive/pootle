# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ratha/sourceforge.net/translate/trunk/pootling/ui/Statistic.ui'
#
# Created: Mon Mar 19 15:40:18 2007
#      by: PyQt4 UI code generator 4-snapshot-20070212
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,313,204).size()).expandedTo(Form.minimumSizeHint()))

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

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout1.addItem(spacerItem,4,1,1,1)

        self.lblfuzzy = QtGui.QLabel(self.frame)
        self.lblfuzzy.setObjectName("lblfuzzy")
        self.gridlayout1.addWidget(self.lblfuzzy,3,0,1,1)

        self.label_8 = QtGui.QLabel(self.frame)
        self.label_8.setWindowModality(QtCore.Qt.NonModal)
        self.label_8.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.gridlayout1.addWidget(self.label_8,2,1,1,1)

        self.lbluntranslate = QtGui.QLabel(self.frame)
        self.lbluntranslate.setObjectName("lbluntranslate")
        self.gridlayout1.addWidget(self.lbluntranslate,2,0,1,1)

        self.lbltranslated = QtGui.QLabel(self.frame)
        self.lbltranslated.setWindowModality(QtCore.Qt.NonModal)
        self.lbltranslated.setFrameShape(QtGui.QFrame.NoFrame)
        self.lbltranslated.setAlignment(QtCore.Qt.AlignCenter)
        self.lbltranslated.setObjectName("lbltranslated")
        self.gridlayout1.addWidget(self.lbltranslated,1,1,1,1)

        self.label_4 = QtGui.QLabel(self.frame)
        self.label_4.setObjectName("label_4")
        self.gridlayout1.addWidget(self.label_4,1,0,1,1)

        self.lblname = QtGui.QLabel(self.frame)
        self.lblname.setWindowModality(QtCore.Qt.NonModal)
        self.lblname.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblname.setTextFormat(QtCore.Qt.PlainText)
        self.lblname.setAlignment(QtCore.Qt.AlignCenter)
        self.lblname.setObjectName("lblname")
        self.gridlayout1.addWidget(self.lblname,0,1,1,1)

        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setObjectName("label_3")
        self.gridlayout1.addWidget(self.label_3,0,0,1,1)

        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setWindowModality(QtCore.Qt.NonModal)
        self.label_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridlayout1.addWidget(self.label_2,3,1,1,1)
        self.gridlayout.addWidget(self.frame,0,0,1,2)

        self.btnOk = QtGui.QPushButton(Form)
        self.btnOk.setObjectName("btnOk")
        self.gridlayout.addWidget(self.btnOk,1,1,1,1)

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1,1,0,1,1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.lblfuzzy.setText(QtGui.QApplication.translate("Form", "- Fuzzy of message:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbluntranslate.setText(QtGui.QApplication.translate("Form", "- Untranslated of message:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "- Translated of message:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "- Name of message:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOk.setText(QtGui.QApplication.translate("Form", "OK", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
