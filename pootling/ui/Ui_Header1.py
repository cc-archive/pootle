# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ratha/sourceforge.net/translate/trunk/pootling/ui/Header.ui'
#
# Created: Tue Jul  3 11:58:10 2007
#      by: PyQt4 UI code generator 4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_frmHeader(object):
    def setupUi(self, frmHeader):
        frmHeader.setObjectName("frmHeader")
        frmHeader.resize(QtCore.QSize(QtCore.QRect(0,0,598,634).size()).expandedTo(frmHeader.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(frmHeader)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.splitter = QtGui.QSplitter(frmHeader)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")

        self.dockWidget1 = QtGui.QDockWidget(self.splitter)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidget1.sizePolicy().hasHeightForWidth())
        self.dockWidget1.setSizePolicy(sizePolicy)
        self.dockWidget1.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.dockWidget1.setAcceptDrops(True)
        self.dockWidget1.setAutoFillBackground(False)
        self.dockWidget1.setFloating(False)
        self.dockWidget1.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        self.dockWidget1.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.NoDockWidgetArea|QtCore.Qt.RightDockWidgetArea|QtCore.Qt.TopDockWidgetArea)
        self.dockWidget1.setObjectName("dockWidget1")

        self.dockWidgetContents_2 = QtGui.QWidget(self.dockWidget1)
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")

        self.gridlayout1 = QtGui.QGridLayout(self.dockWidgetContents_2)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.txtOtherComments = QtGui.QTextEdit(self.dockWidgetContents_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(3))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtOtherComments.sizePolicy().hasHeightForWidth())
        self.txtOtherComments.setSizePolicy(sizePolicy)
        self.txtOtherComments.setTabChangesFocus(True)
        self.txtOtherComments.setObjectName("txtOtherComments")
        self.gridlayout1.addWidget(self.txtOtherComments,0,0,1,1)
        self.dockWidget1.setWidget(self.dockWidgetContents_2)

        self.dockWidget2 = QtGui.QDockWidget(self.splitter)
        self.dockWidget2.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        self.dockWidget2.setObjectName("dockWidget2")

        self.dockWidgetContents = QtGui.QWidget(self.dockWidget2)
        self.dockWidgetContents.setObjectName("dockWidgetContents")

        self.gridlayout2 = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        self.frame = QtGui.QFrame(self.dockWidgetContents)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.gridlayout3 = QtGui.QGridLayout(self.frame)
        self.gridlayout3.setMargin(9)
        self.gridlayout3.setSpacing(6)
        self.gridlayout3.setObjectName("gridlayout3")

        self.btnUp = QtGui.QPushButton(self.frame)
        self.btnUp.setEnabled(False)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnUp.sizePolicy().hasHeightForWidth())
        self.btnUp.setSizePolicy(sizePolicy)
        self.btnUp.setIcon(QtGui.QIcon("../images/up.png"))
        self.btnUp.setObjectName("btnUp")
        self.gridlayout3.addWidget(self.btnUp,0,1,1,1)

        self.btnInsertRow = QtGui.QPushButton(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnInsertRow.sizePolicy().hasHeightForWidth())
        self.btnInsertRow.setSizePolicy(sizePolicy)

        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.btnInsertRow.setFont(font)
        self.btnInsertRow.setIcon(QtGui.QIcon("../images/add.png"))
        self.btnInsertRow.setObjectName("btnInsertRow")
        self.gridlayout3.addWidget(self.btnInsertRow,3,1,1,1)

        self.btnDown = QtGui.QPushButton(self.frame)
        self.btnDown.setEnabled(False)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDown.sizePolicy().hasHeightForWidth())
        self.btnDown.setSizePolicy(sizePolicy)
        self.btnDown.setIcon(QtGui.QIcon("../images/down.png"))
        self.btnDown.setObjectName("btnDown")
        self.gridlayout3.addWidget(self.btnDown,1,1,1,1)

        self.tableHeader = QtGui.QTableWidget(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableHeader.sizePolicy().hasHeightForWidth())
        self.tableHeader.setSizePolicy(sizePolicy)
        self.tableHeader.setMouseTracking(False)
        self.tableHeader.setFocusPolicy(QtCore.Qt.TabFocus)
        self.tableHeader.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.tableHeader.setAcceptDrops(False)
        self.tableHeader.setLineWidth(1)
        self.tableHeader.setMidLineWidth(1)
        self.tableHeader.setTabKeyNavigation(False)
        self.tableHeader.setProperty("showDropIndicator",QtCore.QVariant(False))
        self.tableHeader.setDragEnabled(False)
        self.tableHeader.setAlternatingRowColors(True)
        self.tableHeader.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableHeader.setShowGrid(True)
        self.tableHeader.setObjectName("tableHeader")
        self.gridlayout3.addWidget(self.tableHeader,0,0,5,1)

        self.btnDeleteRow = QtGui.QPushButton(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDeleteRow.sizePolicy().hasHeightForWidth())
        self.btnDeleteRow.setSizePolicy(sizePolicy)

        palette = QtGui.QPalette()

        brush = QtGui.QBrush(QtGui.QColor(0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.WindowText,brush)

        brush = QtGui.QBrush(QtGui.QColor(221,223,228))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Button,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Light,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Midlight,brush)

        brush = QtGui.QBrush(QtGui.QColor(85,85,85))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Dark,brush)

        brush = QtGui.QBrush(QtGui.QColor(199,199,199))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Mid,brush)

        brush = QtGui.QBrush(QtGui.QColor(0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Text,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.BrightText,brush)

        brush = QtGui.QBrush(QtGui.QColor(0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.ButtonText,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Base,brush)

        brush = QtGui.QBrush(QtGui.QColor(239,239,239))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Window,brush)

        brush = QtGui.QBrush(QtGui.QColor(0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Shadow,brush)

        brush = QtGui.QBrush(QtGui.QColor(103,141,178))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Highlight,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.HighlightedText,brush)

        brush = QtGui.QBrush(QtGui.QColor(0,0,238))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Link,brush)

        brush = QtGui.QBrush(QtGui.QColor(82,24,139))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.LinkVisited,brush)

        brush = QtGui.QBrush(QtGui.QColor(232,232,232))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.AlternateBase,brush)

        brush = QtGui.QBrush(QtGui.QColor(0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.WindowText,brush)

        brush = QtGui.QBrush(QtGui.QColor(221,223,228))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Button,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Light,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Midlight,brush)

        brush = QtGui.QBrush(QtGui.QColor(85,85,85))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Dark,brush)

        brush = QtGui.QBrush(QtGui.QColor(199,199,199))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Mid,brush)

        brush = QtGui.QBrush(QtGui.QColor(0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Text,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.BrightText,brush)

        brush = QtGui.QBrush(QtGui.QColor(0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.ButtonText,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Base,brush)

        brush = QtGui.QBrush(QtGui.QColor(239,239,239))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Window,brush)

        brush = QtGui.QBrush(QtGui.QColor(0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Shadow,brush)

        brush = QtGui.QBrush(QtGui.QColor(103,141,178))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Highlight,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.HighlightedText,brush)

        brush = QtGui.QBrush(QtGui.QColor(0,0,238))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Link,brush)

        brush = QtGui.QBrush(QtGui.QColor(82,24,139))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.LinkVisited,brush)

        brush = QtGui.QBrush(QtGui.QColor(232,232,232))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.AlternateBase,brush)

        brush = QtGui.QBrush(QtGui.QColor(128,128,128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.WindowText,brush)

        brush = QtGui.QBrush(QtGui.QColor(221,223,228))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Button,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Light,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Midlight,brush)

        brush = QtGui.QBrush(QtGui.QColor(85,85,85))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Dark,brush)

        brush = QtGui.QBrush(QtGui.QColor(199,199,199))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Mid,brush)

        brush = QtGui.QBrush(QtGui.QColor(199,199,199))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Text,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.BrightText,brush)

        brush = QtGui.QBrush(QtGui.QColor(128,128,128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.ButtonText,brush)

        brush = QtGui.QBrush(QtGui.QColor(239,239,239))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Base,brush)

        brush = QtGui.QBrush(QtGui.QColor(239,239,239))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Window,brush)

        brush = QtGui.QBrush(QtGui.QColor(0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Shadow,brush)

        brush = QtGui.QBrush(QtGui.QColor(86,117,148))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Highlight,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.HighlightedText,brush)

        brush = QtGui.QBrush(QtGui.QColor(0,0,238))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Link,brush)

        brush = QtGui.QBrush(QtGui.QColor(82,24,139))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.LinkVisited,brush)

        brush = QtGui.QBrush(QtGui.QColor(232,232,232))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.AlternateBase,brush)
        self.btnDeleteRow.setPalette(palette)

        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.btnDeleteRow.setFont(font)
        self.btnDeleteRow.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.btnDeleteRow.setIcon(QtGui.QIcon("../images/minus.png"))
        self.btnDeleteRow.setObjectName("btnDeleteRow")
        self.gridlayout3.addWidget(self.btnDeleteRow,4,1,1,1)

        spacerItem = QtGui.QSpacerItem(20,141,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout3.addItem(spacerItem,2,1,1,1)
        self.gridlayout2.addWidget(self.frame,0,0,1,1)
        self.dockWidget2.setWidget(self.dockWidgetContents)

        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName("widget")

        self.hboxlayout = QtGui.QHBoxLayout(self.widget)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.resetButton = QtGui.QPushButton(self.widget)
        self.resetButton.setEnabled(True)
        self.resetButton.setObjectName("resetButton")
        self.hboxlayout.addWidget(self.resetButton)

        self.applyButton = QtGui.QPushButton(self.widget)
        self.applyButton.setObjectName("applyButton")
        self.hboxlayout.addWidget(self.applyButton)

        spacerItem1 = QtGui.QSpacerItem(131,31,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)

        self.okButton = QtGui.QPushButton(self.widget)
        self.okButton.setObjectName("okButton")
        self.hboxlayout.addWidget(self.okButton)

        self.cancelButton = QtGui.QPushButton(self.widget)
        self.cancelButton.setObjectName("cancelButton")
        self.hboxlayout.addWidget(self.cancelButton)
        self.gridlayout.addWidget(self.splitter,1,0,1,1)

        self.label_2 = QtGui.QLabel(frmHeader)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2,2,0,1,1)

        self.label = QtGui.QLabel(frmHeader)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,1)

        self.retranslateUi(frmHeader)
        QtCore.QMetaObject.connectSlotsByName(frmHeader)

    def retranslateUi(self, frmHeader):
        frmHeader.setWindowTitle(QtGui.QApplication.translate("frmHeader", "Header", None, QtGui.QApplication.UnicodeUTF8))
        self.btnUp.setToolTip(QtGui.QApplication.translate("frmHeader", "Move up", None, QtGui.QApplication.UnicodeUTF8))
        self.btnUp.setText(QtGui.QApplication.translate("frmHeader", "&Up", None, QtGui.QApplication.UnicodeUTF8))
        self.btnInsertRow.setToolTip(QtGui.QApplication.translate("frmHeader", "Insert row", None, QtGui.QApplication.UnicodeUTF8))
        self.btnInsertRow.setText(QtGui.QApplication.translate("frmHeader", " &Insert", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDown.setToolTip(QtGui.QApplication.translate("frmHeader", "Move down", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDown.setText(QtGui.QApplication.translate("frmHeader", "&Down", None, QtGui.QApplication.UnicodeUTF8))
        self.tableHeader.setColumnCount(2)
        self.tableHeader.clear()
        self.tableHeader.setColumnCount(2)
        self.tableHeader.setRowCount(0)
        self.btnDeleteRow.setToolTip(QtGui.QApplication.translate("frmHeader", "delete row", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDeleteRow.setText(QtGui.QApplication.translate("frmHeader", " &Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.resetButton.setText(QtGui.QApplication.translate("frmHeader", "Re&set", None, QtGui.QApplication.UnicodeUTF8))
        self.applyButton.setText(QtGui.QApplication.translate("frmHeader", "&Apply Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("frmHeader", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("frmHeader", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("frmHeader", "Header", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("frmHeader", "Comment", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    frmHeader = QtGui.QDialog()
    ui = Ui_frmHeader()
    ui.setupUi(frmHeader)
    frmHeader.show()
    sys.exit(app.exec_())
