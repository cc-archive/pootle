# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ratha/sourceforge.net/Converter/ui/KConverter.ui'
#
# Created: Mon Aug 27 11:04:24 2007
#      by: PyQt4 UI code generator 4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_kconvert(object):
    def setupUi(self, kconvert):
        kconvert.setObjectName("kconvert")
        kconvert.resize(QtCore.QSize(QtCore.QRect(0,0,462,461).size()).expandedTo(kconvert.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(kconvert)
        self.centralwidget.setObjectName("centralwidget")

        self.gridlayout = QtGui.QGridLayout(self.centralwidget)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")

        self.tab1 = QtGui.QWidget()
        self.tab1.setObjectName("tab1")

        self.gridlayout1 = QtGui.QGridLayout(self.tab1)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.groupBox_2 = QtGui.QGroupBox(self.tab1)
        self.groupBox_2.setObjectName("groupBox_2")

        self.gridlayout2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout2.addItem(spacerItem,2,2,1,1)

        self.spinBoxLCode = QtGui.QSpinBox(self.groupBox_2)
        self.spinBoxLCode.setObjectName("spinBoxLCode")
        self.gridlayout2.addWidget(self.spinBoxLCode,2,4,1,1)

        self.label_11 = QtGui.QLabel(self.groupBox_2)
        self.label_11.setObjectName("label_11")
        self.gridlayout2.addWidget(self.label_11,2,3,1,1)

        self.chbOverridesizeLCode = QtGui.QCheckBox(self.groupBox_2)
        self.chbOverridesizeLCode.setObjectName("chbOverridesizeLCode")
        self.gridlayout2.addWidget(self.chbOverridesizeLCode,2,1,1,1)

        self.label_9 = QtGui.QLabel(self.groupBox_2)
        self.label_9.setObjectName("label_9")
        self.gridlayout2.addWidget(self.label_9,0,0,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.lineFilenameOutLCode = QtGui.QLineEdit(self.groupBox_2)
        self.lineFilenameOutLCode.setObjectName("lineFilenameOutLCode")
        self.hboxlayout.addWidget(self.lineFilenameOutLCode)

        self.btnBrowseLCode1 = QtGui.QPushButton(self.groupBox_2)
        self.btnBrowseLCode1.setIcon(QtGui.QIcon("../image/open.png"))
        self.btnBrowseLCode1.setObjectName("btnBrowseLCode1")
        self.hboxlayout.addWidget(self.btnBrowseLCode1)
        self.gridlayout2.addLayout(self.hboxlayout,0,1,1,4)

        self.lineFontLCode = QtGui.QLineEdit(self.groupBox_2)
        self.lineFontLCode.setObjectName("lineFontLCode")
        self.gridlayout2.addWidget(self.lineFontLCode,1,1,1,4)

        self.label_10 = QtGui.QLabel(self.groupBox_2)
        self.label_10.setObjectName("label_10")
        self.gridlayout2.addWidget(self.label_10,1,0,1,1)
        self.gridlayout1.addWidget(self.groupBox_2,1,0,1,1)

        self.groupBox = QtGui.QGroupBox(self.tab1)
        self.groupBox.setObjectName("groupBox")

        self.gridlayout3 = QtGui.QGridLayout(self.groupBox)
        self.gridlayout3.setMargin(9)
        self.gridlayout3.setSpacing(6)
        self.gridlayout3.setObjectName("gridlayout3")

        self.lineFilenameLCode = QtGui.QLineEdit(self.groupBox)
        self.lineFilenameLCode.setObjectName("lineFilenameLCode")
        self.gridlayout3.addWidget(self.lineFilenameLCode,0,1,1,1)

        self.cmbDocumentLCode = QtGui.QComboBox(self.groupBox)
        self.cmbDocumentLCode.setObjectName("cmbDocumentLCode")
        self.gridlayout3.addWidget(self.cmbDocumentLCode,1,1,1,2)

        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridlayout3.addWidget(self.label_2,1,0,1,1)

        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridlayout3.addWidget(self.label,0,0,1,1)

        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridlayout3.addWidget(self.label_3,2,0,1,1)

        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridlayout3.addWidget(self.label_4,3,0,1,1)

        self.btnBrowseLCode = QtGui.QPushButton(self.groupBox)
        self.btnBrowseLCode.setIcon(QtGui.QIcon("../image/open.png"))
        self.btnBrowseLCode.setObjectName("btnBrowseLCode")
        self.gridlayout3.addWidget(self.btnBrowseLCode,0,2,1,1)

        self.cmbEncodingLCode = QtGui.QComboBox(self.groupBox)
        self.cmbEncodingLCode.setObjectName("cmbEncodingLCode")
        self.gridlayout3.addWidget(self.cmbEncodingLCode,3,1,1,2)

        self.cmbFontLCode = QtGui.QComboBox(self.groupBox)
        self.cmbFontLCode.setObjectName("cmbFontLCode")
        self.gridlayout3.addWidget(self.cmbFontLCode,2,1,1,2)
        self.gridlayout1.addWidget(self.groupBox,0,0,1,1)
        self.tabWidget.addTab(self.tab1,"")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.gridlayout4 = QtGui.QGridLayout(self.tab)
        self.gridlayout4.setMargin(9)
        self.gridlayout4.setSpacing(6)
        self.gridlayout4.setObjectName("gridlayout4")

        self.groupBox_4 = QtGui.QGroupBox(self.tab)
        self.groupBox_4.setObjectName("groupBox_4")

        self.gridlayout5 = QtGui.QGridLayout(self.groupBox_4)
        self.gridlayout5.setMargin(9)
        self.gridlayout5.setSpacing(6)
        self.gridlayout5.setObjectName("gridlayout5")

        self.spinBoxUCode = QtGui.QSpinBox(self.groupBox_4)
        self.spinBoxUCode.setObjectName("spinBoxUCode")
        self.gridlayout5.addWidget(self.spinBoxUCode,2,4,1,1)

        self.label_13 = QtGui.QLabel(self.groupBox_4)
        self.label_13.setObjectName("label_13")
        self.gridlayout5.addWidget(self.label_13,2,3,1,1)

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout5.addItem(spacerItem1,2,2,1,1)

        self.chbOverridesizeUCode = QtGui.QCheckBox(self.groupBox_4)
        self.chbOverridesizeUCode.setObjectName("chbOverridesizeUCode")
        self.gridlayout5.addWidget(self.chbOverridesizeUCode,2,1,1,1)

        self.lineFontUCode = QtGui.QLineEdit(self.groupBox_4)
        self.lineFontUCode.setObjectName("lineFontUCode")
        self.gridlayout5.addWidget(self.lineFontUCode,1,1,1,4)

        self.label_15 = QtGui.QLabel(self.groupBox_4)
        self.label_15.setObjectName("label_15")
        self.gridlayout5.addWidget(self.label_15,1,0,1,1)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.lineFilenameOutUCode = QtGui.QLineEdit(self.groupBox_4)
        self.lineFilenameOutUCode.setObjectName("lineFilenameOutUCode")
        self.hboxlayout1.addWidget(self.lineFilenameOutUCode)

        self.btnBrowseUCode1 = QtGui.QPushButton(self.groupBox_4)
        self.btnBrowseUCode1.setIcon(QtGui.QIcon("../image/open.png"))
        self.btnBrowseUCode1.setObjectName("btnBrowseUCode1")
        self.hboxlayout1.addWidget(self.btnBrowseUCode1)
        self.gridlayout5.addLayout(self.hboxlayout1,0,1,1,4)

        self.label_14 = QtGui.QLabel(self.groupBox_4)
        self.label_14.setObjectName("label_14")
        self.gridlayout5.addWidget(self.label_14,0,0,1,1)
        self.gridlayout4.addWidget(self.groupBox_4,1,0,1,1)

        self.groupBox_3 = QtGui.QGroupBox(self.tab)
        self.groupBox_3.setObjectName("groupBox_3")

        self.gridlayout6 = QtGui.QGridLayout(self.groupBox_3)
        self.gridlayout6.setMargin(9)
        self.gridlayout6.setSpacing(6)
        self.gridlayout6.setObjectName("gridlayout6")

        self.label_6 = QtGui.QLabel(self.groupBox_3)
        self.label_6.setObjectName("label_6")
        self.gridlayout6.addWidget(self.label_6,0,0,1,1)

        self.btnBrowseUCode = QtGui.QPushButton(self.groupBox_3)
        self.btnBrowseUCode.setIcon(QtGui.QIcon("../image/open.png"))
        self.btnBrowseUCode.setObjectName("btnBrowseUCode")
        self.gridlayout6.addWidget(self.btnBrowseUCode,0,2,1,1)

        self.label_5 = QtGui.QLabel(self.groupBox_3)
        self.label_5.setObjectName("label_5")
        self.gridlayout6.addWidget(self.label_5,1,0,1,1)

        self.cmbDocumentUCode = QtGui.QComboBox(self.groupBox_3)
        self.cmbDocumentUCode.setObjectName("cmbDocumentUCode")
        self.gridlayout6.addWidget(self.cmbDocumentUCode,1,1,1,2)

        self.lineFilenameUCode = QtGui.QLineEdit(self.groupBox_3)
        self.lineFilenameUCode.setObjectName("lineFilenameUCode")
        self.gridlayout6.addWidget(self.lineFilenameUCode,0,1,1,1)
        self.gridlayout4.addWidget(self.groupBox_3,0,0,1,1)

        spacerItem2 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout4.addItem(spacerItem2,2,0,1,1)
        self.tabWidget.addTab(self.tab,"")
        self.gridlayout.addWidget(self.tabWidget,0,0,1,3)

        self.btnReset = QtGui.QPushButton(self.centralwidget)
        self.btnReset.setObjectName("btnReset")
        self.gridlayout.addWidget(self.btnReset,1,1,1,1)

        spacerItem3 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem3,1,2,1,1)

        self.btnConvert = QtGui.QPushButton(self.centralwidget)
        self.btnConvert.setObjectName("btnConvert")
        self.gridlayout.addWidget(self.btnConvert,1,0,1,1)
        kconvert.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(kconvert)
        self.menubar.setGeometry(QtCore.QRect(0,0,462,28))
        self.menubar.setObjectName("menubar")

        self.menu_Help = QtGui.QMenu(self.menubar)
        self.menu_Help.setObjectName("menu_Help")

        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        kconvert.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(kconvert)
        self.statusbar.setObjectName("statusbar")
        kconvert.setStatusBar(self.statusbar)

        self.actionQuit = QtGui.QAction(kconvert)
        self.actionQuit.setIcon(QtGui.QIcon("../image/exit.png"))
        self.actionQuit.setObjectName("actionQuit")

        self.actionLegacy_to_Unicode = QtGui.QAction(kconvert)
        self.actionLegacy_to_Unicode.setObjectName("actionLegacy_to_Unicode")

        self.actionUnicode_to_Legacy = QtGui.QAction(kconvert)
        self.actionUnicode_to_Legacy.setObjectName("actionUnicode_to_Legacy")

        self.actionAbout_KhmerUnicode = QtGui.QAction(kconvert)
        self.actionAbout_KhmerUnicode.setObjectName("actionAbout_KhmerUnicode")

        self.actionAboutQt = QtGui.QAction(kconvert)
        self.actionAboutQt.setObjectName("actionAboutQt")
        self.menu_Help.addAction(self.actionAbout_KhmerUnicode)
        self.menu_Help.addAction(self.actionAboutQt)
        self.menu_File.addAction(self.actionQuit)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(kconvert)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(kconvert)
        kconvert.setTabOrder(self.tabWidget,self.lineFilenameLCode)
        kconvert.setTabOrder(self.lineFilenameLCode,self.btnBrowseUCode)
        kconvert.setTabOrder(self.btnBrowseUCode,self.cmbDocumentLCode)
        kconvert.setTabOrder(self.cmbDocumentLCode,self.cmbFontLCode)
        kconvert.setTabOrder(self.cmbFontLCode,self.cmbEncodingLCode)
        kconvert.setTabOrder(self.cmbEncodingLCode,self.btnConvert)
        kconvert.setTabOrder(self.btnConvert,self.btnReset)

    def retranslateUi(self, kconvert):
        kconvert.setWindowTitle(QtGui.QApplication.translate("kconvert", "Khmer Converter", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("kconvert", "Output File", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("kconvert", "Size:", None, QtGui.QApplication.UnicodeUTF8))
        self.chbOverridesizeLCode.setText(QtGui.QApplication.translate("kconvert", "Override size", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("kconvert", "Filename:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("kconvert", "Font:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("kconvert", "Input File", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("kconvert", "Document type:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("kconvert", "Filename:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("kconvert", "Font:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("kconvert", "Encoding:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab1), QtGui.QApplication.translate("kconvert", "Legacy to Unicode", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("kconvert", "Output File", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setText(QtGui.QApplication.translate("kconvert", "Size:", None, QtGui.QApplication.UnicodeUTF8))
        self.chbOverridesizeUCode.setText(QtGui.QApplication.translate("kconvert", "Override size", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setText(QtGui.QApplication.translate("kconvert", "Font:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setText(QtGui.QApplication.translate("kconvert", "Filename:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("kconvert", "Input File", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("kconvert", "Filename:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("kconvert", "Document type:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("kconvert", "Unicode to Legacy", None, QtGui.QApplication.UnicodeUTF8))
        self.btnReset.setText(QtGui.QApplication.translate("kconvert", "&Reset", None, QtGui.QApplication.UnicodeUTF8))
        self.btnConvert.setText(QtGui.QApplication.translate("kconvert", "&Convert", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Help.setTitle(QtGui.QApplication.translate("kconvert", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_File.setTitle(QtGui.QApplication.translate("kconvert", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("kconvert", "&Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setShortcut(QtGui.QApplication.translate("kconvert", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLegacy_to_Unicode.setText(QtGui.QApplication.translate("kconvert", "Legacy to Unicode", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLegacy_to_Unicode.setShortcut(QtGui.QApplication.translate("kconvert", "Ctrl+L", None, QtGui.QApplication.UnicodeUTF8))
        self.actionUnicode_to_Legacy.setText(QtGui.QApplication.translate("kconvert", "Unicode to Legacy", None, QtGui.QApplication.UnicodeUTF8))
        self.actionUnicode_to_Legacy.setShortcut(QtGui.QApplication.translate("kconvert", "Ctrl+U", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_KhmerUnicode.setText(QtGui.QApplication.translate("kconvert", "About Khmer Unicode", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAboutQt.setText(QtGui.QApplication.translate("kconvert", "About Qt", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    kconvert = QtGui.QMainWindow()
    ui = Ui_kconvert()
    ui.setupUi(kconvert)
    kconvert.show()
    sys.exit(app.exec_())
