# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Wed Feb  7 14:52:24 2007
#      by: PyQt4 UI code generator 4.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,605,492).size()).expandedTo(MainWindow.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(400,300))
        MainWindow.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        MainWindow.setWindowIcon(QtGui.QIcon("../images/pootling.png"))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,605,30))
        self.menubar.setObjectName("menubar")

        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")

        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menuOpen_Recent = QtGui.QMenu(self.menuFile)
        self.menuOpen_Recent.setIcon(QtGui.QIcon("../images/open.png"))
        self.menuOpen_Recent.setObjectName("menuOpen_Recent")

        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")

        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setEnabled(True)
        self.menuView.setObjectName("menuView")

        self.menuGo = QtGui.QMenu(self.menubar)
        self.menuGo.setObjectName("menuGo")

        self.menuWindow = QtGui.QMenu(self.menubar)
        self.menuWindow.setObjectName("menuWindow")

        self.menuToolbars = QtGui.QMenu(self.menuWindow)
        self.menuToolbars.setObjectName("menuToolbars")

        self.menuBookmark = QtGui.QMenu(self.menubar)
        self.menuBookmark.setObjectName("menuBookmark")

        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")

        self.menu_Tool = QtGui.QMenu(self.menubar)
        self.menu_Tool.setObjectName("menu_Tool")

        self.menu_TM = QtGui.QMenu(self.menu_Tool)
        self.menu_TM.setIcon(QtGui.QIcon("../images/memory.png"))
        self.menu_TM.setObjectName("menu_TM")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.toolStandard = QtGui.QToolBar(MainWindow)
        self.toolStandard.setEnabled(True)
        self.toolStandard.setOrientation(QtCore.Qt.Horizontal)
        self.toolStandard.setObjectName("toolStandard")
        MainWindow.addToolBar(self.toolStandard)

        self.toolNavigation = QtGui.QToolBar(MainWindow)
        self.toolNavigation.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.toolNavigation.setAcceptDrops(False)
        self.toolNavigation.setOrientation(QtCore.Qt.Horizontal)
        self.toolNavigation.setObjectName("toolNavigation")
        MainWindow.addToolBar(self.toolNavigation)

        self.toolFilter = QtGui.QToolBar(MainWindow)
        self.toolFilter.setOrientation(QtCore.Qt.Horizontal)
        self.toolFilter.setObjectName("toolFilter")
        MainWindow.addToolBar(self.toolFilter)

        self.actionNew = QtGui.QAction(MainWindow)
        self.actionNew.setIcon(QtGui.QIcon("../images/new.png"))
        self.actionNew.setObjectName("actionNew")

        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setIcon(QtGui.QIcon("../images/open.png"))
        self.actionOpen.setObjectName("actionOpen")

        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setEnabled(False)
        self.actionSave.setIcon(QtGui.QIcon("../images/save.png"))
        self.actionSave.setObjectName("actionSave")

        self.actionSaveas = QtGui.QAction(MainWindow)
        self.actionSaveas.setEnabled(False)
        self.actionSaveas.setIcon(QtGui.QIcon("../images/saveAs.png"))
        self.actionSaveas.setObjectName("actionSaveas")

        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setIcon(QtGui.QIcon("../images/exit.png"))
        self.actionExit.setObjectName("actionExit")

        self.actionUndo = QtGui.QAction(MainWindow)
        self.actionUndo.setEnabled(False)
        self.actionUndo.setIcon(QtGui.QIcon("../images/undo.png"))
        self.actionUndo.setObjectName("actionUndo")

        self.actionRedo = QtGui.QAction(MainWindow)
        self.actionRedo.setEnabled(False)
        self.actionRedo.setIcon(QtGui.QIcon("../images/redo.png"))
        self.actionRedo.setObjectName("actionRedo")

        self.actionCut = QtGui.QAction(MainWindow)
        self.actionCut.setEnabled(False)
        self.actionCut.setIcon(QtGui.QIcon("../images/cut.png"))
        self.actionCut.setObjectName("actionCut")

        self.actionCopy = QtGui.QAction(MainWindow)
        self.actionCopy.setCheckable(False)
        self.actionCopy.setEnabled(False)
        self.actionCopy.setIcon(QtGui.QIcon("../images/copy.png"))
        self.actionCopy.setObjectName("actionCopy")

        self.actionPaste = QtGui.QAction(MainWindow)
        self.actionPaste.setEnabled(False)
        self.actionPaste.setIcon(QtGui.QIcon("../images/paste.png"))
        self.actionPaste.setObjectName("actionPaste")

        self.actionFind = QtGui.QAction(MainWindow)
        self.actionFind.setEnabled(False)
        self.actionFind.setIcon(QtGui.QIcon("../images/find.png"))
        self.actionFind.setObjectName("actionFind")

        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")

        self.actionShowMenuBar = QtGui.QAction(MainWindow)
        self.actionShowMenuBar.setObjectName("actionShowMenuBar")

        self.actionShowTUview = QtGui.QAction(MainWindow)
        self.actionShowTUview.setObjectName("actionShowTUview")

        self.actionAboutQT = QtGui.QAction(MainWindow)
        self.actionAboutQT.setObjectName("actionAboutQT")

        self.actionShow_MenuBar = QtGui.QAction(MainWindow)
        self.actionShow_MenuBar.setObjectName("actionShow_MenuBar")

        self.actionShow_TUview = QtGui.QAction(MainWindow)
        self.actionShow_TUview.setObjectName("actionShow_TUview")

        self.actionFirst = QtGui.QAction(MainWindow)
        self.actionFirst.setEnabled(False)
        self.actionFirst.setIcon(QtGui.QIcon("../images/first.png"))
        self.actionFirst.setObjectName("actionFirst")

        self.actionPrevious = QtGui.QAction(MainWindow)
        self.actionPrevious.setEnabled(False)
        self.actionPrevious.setIcon(QtGui.QIcon("../images/previous.png"))
        self.actionPrevious.setObjectName("actionPrevious")

        self.actionNext = QtGui.QAction(MainWindow)
        self.actionNext.setEnabled(False)
        self.actionNext.setIcon(QtGui.QIcon("../images/next.png"))
        self.actionNext.setObjectName("actionNext")

        self.actionLast = QtGui.QAction(MainWindow)
        self.actionLast.setEnabled(False)
        self.actionLast.setIcon(QtGui.QIcon("../images/last.png"))
        self.actionLast.setObjectName("actionLast")

        self.actionCopySource2Target = QtGui.QAction(MainWindow)
        self.actionCopySource2Target.setEnabled(False)
        self.actionCopySource2Target.setObjectName("actionCopySource2Target")

        self.actionToggleFuzzy = QtGui.QAction(MainWindow)
        self.actionToggleFuzzy.setEnabled(False)
        self.actionToggleFuzzy.setObjectName("actionToggleFuzzy")

        self.actionFile = QtGui.QAction(MainWindow)
        self.actionFile.setObjectName("actionFile")

        self.actionFind_Previous = QtGui.QAction(MainWindow)
        self.actionFind_Previous.setEnabled(False)
        self.actionFind_Previous.setObjectName("actionFind_Previous")

        self.actionFind_Next = QtGui.QAction(MainWindow)
        self.actionFind_Next.setEnabled(False)
        self.actionFind_Next.setObjectName("actionFind_Next")

        self.actionReplace = QtGui.QAction(MainWindow)
        self.actionReplace.setEnabled(False)
        self.actionReplace.setObjectName("actionReplace")

        self.actionFindNext = QtGui.QAction(MainWindow)
        self.actionFindNext.setEnabled(False)
        self.actionFindNext.setObjectName("actionFindNext")

        self.actionOpenInNewWindow = QtGui.QAction(MainWindow)
        self.actionOpenInNewWindow.setIcon(QtGui.QIcon("../images/window_new.png"))
        self.actionOpenInNewWindow.setVisible(False)
        self.actionOpenInNewWindow.setObjectName("actionOpenInNewWindow")

        self.actionFindPrevious = QtGui.QAction(MainWindow)
        self.actionFindPrevious.setEnabled(False)
        self.actionFindPrevious.setObjectName("actionFindPrevious")

        self.actionSelectAll = QtGui.QAction(MainWindow)
        self.actionSelectAll.setEnabled(False)
        self.actionSelectAll.setObjectName("actionSelectAll")

        self.actionEdit_Header = QtGui.QAction(MainWindow)
        self.actionEdit_Header.setEnabled(False)
        self.actionEdit_Header.setObjectName("actionEdit_Header")

        self.actionPreferences = QtGui.QAction(MainWindow)
        self.actionPreferences.setIcon(QtGui.QIcon("../images/configure.png"))
        self.actionPreferences.setObjectName("actionPreferences")

        self.actionToolbars = QtGui.QAction(MainWindow)
        self.actionToolbars.setObjectName("actionToolbars")

        self.actionFilterFuzzy = QtGui.QAction(MainWindow)
        self.actionFilterFuzzy.setCheckable(True)
        self.actionFilterFuzzy.setChecked(True)
        self.actionFilterFuzzy.setEnabled(False)
        self.actionFilterFuzzy.setIcon(QtGui.QIcon("../images/fuzzy.png"))
        self.actionFilterFuzzy.setObjectName("actionFilterFuzzy")

        self.actionFilterTranslated = QtGui.QAction(MainWindow)
        self.actionFilterTranslated.setCheckable(True)
        self.actionFilterTranslated.setChecked(True)
        self.actionFilterTranslated.setEnabled(False)
        self.actionFilterTranslated.setIcon(QtGui.QIcon("../images/translated.png"))
        self.actionFilterTranslated.setObjectName("actionFilterTranslated")

        self.actionFilterUntranslated = QtGui.QAction(MainWindow)
        self.actionFilterUntranslated.setCheckable(True)
        self.actionFilterUntranslated.setChecked(True)
        self.actionFilterUntranslated.setEnabled(False)
        self.actionFilterUntranslated.setIcon(QtGui.QIcon("../images/untranslated.png"))
        self.actionFilterUntranslated.setObjectName("actionFilterUntranslated")

        self.action_Close = QtGui.QAction(MainWindow)
        self.action_Close.setEnabled(False)
        self.action_Close.setIcon(QtGui.QIcon("../images/fileclose.png"))
        self.action_Close.setObjectName("action_Close")

        self.actionClear = QtGui.QAction(MainWindow)
        self.actionClear.setObjectName("actionClear")

        self.actionGoTo = QtGui.QAction(MainWindow)
        self.actionGoTo.setEnabled(False)
        self.actionGoTo.setObjectName("actionGoTo")

        self.actionAddBookmarks = QtGui.QAction(MainWindow)
        self.actionAddBookmarks.setEnabled(False)
        self.actionAddBookmarks.setIcon(QtGui.QIcon("../images/bookmarkadd.png"))
        self.actionAddBookmarks.setObjectName("actionAddBookmarks")

        self.actionClearBookmarks = QtGui.QAction(MainWindow)
        self.actionClearBookmarks.setObjectName("actionClearBookmarks")

        self.action_lookup_Text = QtGui.QAction(MainWindow)
        self.action_lookup_Text.setObjectName("action_lookup_Text")

        self.actionAuto_translate = QtGui.QAction(MainWindow)
        self.actionAuto_translate.setObjectName("actionAuto_translate")

        self.action_TM = QtGui.QAction(MainWindow)
        self.action_TM.setIcon(QtGui.QIcon("../images/memory.png"))
        self.action_TM.setObjectName("action_TM")

        self.actionCatalogManager = QtGui.QAction(MainWindow)
        self.actionCatalogManager.setObjectName("actionCatalogManager")
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAboutQT)
        self.menuOpen_Recent.addAction(self.actionClear)
        self.menuOpen_Recent.addSeparator()
        self.menuFile.addAction(self.actionOpenInNewWindow)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.menuOpen_Recent.menuAction())
        self.menuFile.addAction(self.action_Close)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveas)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionSelectAll)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionFind)
        self.menuEdit.addAction(self.actionFindPrevious)
        self.menuEdit.addAction(self.actionFindNext)
        self.menuEdit.addAction(self.actionReplace)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCopySource2Target)
        self.menuEdit.addAction(self.actionToggleFuzzy)
        self.menuEdit.addAction(self.actionEdit_Header)
        self.menuView.addAction(self.actionFilterFuzzy)
        self.menuView.addAction(self.actionFilterTranslated)
        self.menuView.addAction(self.actionFilterUntranslated)
        self.menuGo.addAction(self.actionFirst)
        self.menuGo.addAction(self.actionPrevious)
        self.menuGo.addAction(self.actionNext)
        self.menuGo.addAction(self.actionLast)
        self.menuGo.addSeparator()
        self.menuGo.addAction(self.actionGoTo)
        self.menuWindow.addSeparator()
        self.menuWindow.addSeparator()
        self.menuWindow.addAction(self.menuToolbars.menuAction())
        self.menuBookmark.addAction(self.actionAddBookmarks)
        self.menuBookmark.addAction(self.actionClearBookmarks)
        self.menuBookmark.addSeparator()
        self.menuSettings.addAction(self.actionPreferences)
        self.menuSettings.addAction(self.action_TM)
        self.menu_TM.addAction(self.action_lookup_Text)
        self.menu_TM.addAction(self.actionAuto_translate)
        self.menu_Tool.addSeparator()
        self.menu_Tool.addAction(self.menu_TM.menuAction())
        self.menu_Tool.addAction(self.actionCatalogManager)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuGo.menuAction())
        self.menubar.addAction(self.menuBookmark.menuAction())
        self.menubar.addAction(self.menu_Tool.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuWindow.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolStandard.addAction(self.actionSave)
        self.toolStandard.addSeparator()
        self.toolStandard.addAction(self.actionCut)
        self.toolStandard.addAction(self.actionCopy)
        self.toolStandard.addAction(self.actionPaste)
        self.toolStandard.addSeparator()
        self.toolStandard.addAction(self.actionUndo)
        self.toolStandard.addAction(self.actionRedo)
        self.toolNavigation.addAction(self.actionFirst)
        self.toolNavigation.addAction(self.actionPrevious)
        self.toolNavigation.addAction(self.actionNext)
        self.toolNavigation.addAction(self.actionLast)
        self.toolFilter.addAction(self.actionFilterFuzzy)
        self.toolFilter.addAction(self.actionFilterTranslated)
        self.toolFilter.addAction(self.actionFilterUntranslated)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def tr(self, string):
        return QtGui.QApplication.translate("MainWindow", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(self.tr("Form"))
        self.menuHelp.setTitle(self.tr("&Help"))
        self.menuFile.setTitle(self.tr("&File"))
        self.menuOpen_Recent.setTitle(self.tr("Open &Recent"))
        self.menuEdit.setTitle(self.tr("&Edit"))
        self.menuView.setTitle(self.tr("&View"))
        self.menuGo.setTitle(self.tr("&Go"))
        self.menuWindow.setTitle(self.tr("&Window"))
        self.menuToolbars.setTitle(self.tr("Toolbars"))
        self.menuBookmark.setTitle(self.tr("&Bookmarks"))
        self.menuSettings.setTitle(self.tr("&Settings"))
        self.menu_Tool.setTitle(self.tr("&Tool"))
        self.menu_TM.setTitle(self.tr("&TM"))
        self.toolStandard.setWindowTitle(self.tr("Standard Toolbar"))
        self.toolNavigation.setWindowTitle(self.tr("Navigation Toolbar"))
        self.toolFilter.setWindowTitle(self.tr("Filter Toolbar"))
        self.actionNew.setText(self.tr("&New"))
        self.actionNew.setShortcut(self.tr("Ctrl+N"))
        self.actionOpen.setText(self.tr("&Open"))
        self.actionOpen.setWhatsThis(self.tr("<h3>open a file</h3>You will be asked for the name of a file to be opened and open recent file in an editor window."))
        self.actionOpen.setShortcut(self.tr("Ctrl+O"))
        self.actionSave.setText(self.tr("&Save"))
        self.actionSave.setWhatsThis(self.tr("<h3>Save a file</h3>Save the contents of current editor window."))
        self.actionSave.setShortcut(self.tr("Ctrl+S"))
        self.actionSaveas.setText(self.tr("Save &As"))
        self.actionExit.setText(self.tr("&Quit"))
        self.actionExit.setStatusTip(self.tr("Quit the application"))
        self.actionExit.setWhatsThis(self.tr("<h3>Quit the application</h3>You will be asked to save the opened file that is being edited."))
        self.actionExit.setShortcut(self.tr("Ctrl+Q"))
        self.actionUndo.setText(self.tr("Undo"))
        self.actionUndo.setWhatsThis(self.tr("<h3>Undo</h3>Undo the last change done in the current editor."))
        self.actionUndo.setShortcut(self.tr("Ctrl+Z"))
        self.actionRedo.setText(self.tr("Redo"))
        self.actionRedo.setWhatsThis(self.tr("<h3>Redo</h3>Redo the last change done in the current editor."))
        self.actionRedo.setShortcut(self.tr("Ctrl+Shift+Z"))
        self.actionCut.setText(self.tr("Cut"))
        self.actionCut.setWhatsThis(self.tr("<h3>Cut</h3>Cut the selected text of the current editor to the clipboard."))
        self.actionCut.setShortcut(self.tr("Ctrl+X"))
        self.actionCopy.setText(self.tr("Copy"))
        self.actionCopy.setWhatsThis(self.tr("<h3>Copy</h3>Copy the selected text of the current editor to the clipboard."))
        self.actionCopy.setShortcut(self.tr("Ctrl+C"))
        self.actionPaste.setText(self.tr("Paste"))
        self.actionPaste.setIconText(self.tr("Paste"))
        self.actionPaste.setToolTip(self.tr("Paste"))
        self.actionPaste.setWhatsThis(self.tr("<h3>Paste</h3>Paste the last cut/copies text from the clipboard to the current editor."))
        self.actionPaste.setShortcut(self.tr("Ctrl+V"))
        self.actionFind.setText(self.tr("Find"))
        self.actionFind.setShortcut(self.tr("Ctrl+F"))
        self.actionAbout.setText(self.tr("About"))
        self.actionShowMenuBar.setText(self.tr("Show MenuBar"))
        self.actionShowMenuBar.setShortcut(self.tr("Ctrl+M"))
        self.actionShowTUview.setText(self.tr("Show TUview"))
        self.actionShowTUview.setShortcut(self.tr("Ctrl+T"))
        self.actionAboutQT.setText(self.tr("About QT"))
        self.actionShow_MenuBar.setText(self.tr("Show MenuBar"))
        self.actionShow_TUview.setText(self.tr("Show TUview"))
        self.actionFirst.setText(self.tr("&First"))
        self.actionFirst.setWhatsThis(self.tr("<h3>First</h3>Move to first row of the table."))
        self.actionFirst.setShortcut(self.tr("Ctrl+PgUp"))
        self.actionPrevious.setText(self.tr("&Previous"))
        self.actionPrevious.setWhatsThis(self.tr("<h3>Previous</h3>Move to previous row inside the table."))
        self.actionPrevious.setShortcut(self.tr("PgUp"))
        self.actionNext.setText(self.tr("&Next"))
        self.actionNext.setWhatsThis(self.tr("<h3>Next</h3>Move to next row inside the table."))
        self.actionNext.setShortcut(self.tr("PgDown"))
        self.actionLast.setText(self.tr("&Last"))
        self.actionLast.setWhatsThis(self.tr("<h3>Last</h3>Move to last row of the table."))
        self.actionLast.setShortcut(self.tr("Ctrl+PgDown"))
        self.actionCopySource2Target.setText(self.tr("Copy Source to Target"))
        self.actionCopySource2Target.setShortcut(self.tr("F2"))
        self.actionToggleFuzzy.setText(self.tr("Toggle fuzzy"))
        self.actionToggleFuzzy.setShortcut(self.tr("Ctrl+U"))
        self.actionFile.setText(self.tr("file"))
        self.actionFind_Previous.setText(self.tr("Find Previous"))
        self.actionFind_Next.setText(self.tr("Find Next"))
        self.actionReplace.setText(self.tr("&Replace"))
        self.actionReplace.setShortcut(self.tr("Ctrl+R"))
        self.actionFindNext.setText(self.tr("Find Next"))
        self.actionFindNext.setIconText(self.tr("Find Next"))
        self.actionFindNext.setToolTip(self.tr("Find Next"))
        self.actionFindNext.setShortcut(self.tr("F3"))
        self.actionOpenInNewWindow.setText(self.tr("Open in New Window"))
        self.actionFindPrevious.setText(self.tr("Find Previous"))
        self.actionFindPrevious.setShortcut(self.tr("Shift+F3"))
        self.actionSelectAll.setText(self.tr("Select &All"))
        self.actionSelectAll.setShortcut(self.tr("Ctrl+A"))
        self.actionEdit_Header.setText(self.tr("Header..."))
        self.actionEdit_Header.setStatusTip(self.tr("Open the dialog to edit the header information."))
        self.actionEdit_Header.setShortcut(self.tr("Ctrl+H"))
        self.actionPreferences.setText(self.tr("&Preferences..."))
        self.actionToolbars.setText(self.tr("Toolbars"))
        self.actionFilterFuzzy.setText(self.tr("Fuzzy"))
        self.actionFilterFuzzy.setToolTip(self.tr("Hide/Show Fuzzy Items"))
        self.actionFilterFuzzy.setStatusTip(self.tr("Hide/Show Fuzzy Items"))
        self.actionFilterFuzzy.setShortcut(self.tr("Ctrl+Alt+F"))
        self.actionFilterTranslated.setText(self.tr("Translated"))
        self.actionFilterTranslated.setToolTip(self.tr("Hide/Show Translated Items"))
        self.actionFilterTranslated.setStatusTip(self.tr("Hide/Show Translated Items"))
        self.actionFilterTranslated.setShortcut(self.tr("Ctrl+Alt+T"))
        self.actionFilterUntranslated.setText(self.tr("Untranslated"))
        self.actionFilterUntranslated.setToolTip(self.tr("Hide/Show Untranslated Items"))
        self.actionFilterUntranslated.setStatusTip(self.tr("Hide/Show Untranslated Items"))
        self.actionFilterUntranslated.setShortcut(self.tr("Ctrl+Alt+U"))
        self.action_Close.setText(self.tr("&Close"))
        self.action_Close.setStatusTip(self.tr("Close the current opened file"))
        self.action_Close.setWhatsThis(self.tr("<h3>Close the current opened file</h3>You will be asked whether to save the current opened file."))
        self.action_Close.setShortcut(self.tr("Ctrl+W"))
        self.actionClear.setText(self.tr("Clear"))
        self.actionGoTo.setText(self.tr("GoTo Line"))
        self.actionGoTo.setShortcut(self.tr("Ctrl+G"))
        self.actionAddBookmarks.setText(self.tr("&Add Bookmarks"))
        self.actionAddBookmarks.setShortcut(self.tr("Ctrl+B"))
        self.actionClearBookmarks.setText(self.tr("&Clear Bookmarks"))
        self.action_lookup_Text.setText(self.tr("&Lookup Unit"))
        self.actionAuto_translate.setText(self.tr("&Auto Translate"))
        self.action_TM.setText(self.tr("&TM"))
        self.actionCatalogManager.setText(self.tr("Catalog Manager"))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
