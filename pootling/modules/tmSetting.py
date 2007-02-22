#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Pootling
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (29 December 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# See the LICENSE file for more details. 
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module is providing an setting path of translation memory dialog 

import sys, os
from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_tmSetting import Ui_tmsetting
from pootling.modules import World
from pootling.modules import FileDialog
from pootling.modules import pickleTM

class tmSetting(QtGui.QDialog):
    """Code for setting path of translation memory dialog."""
    
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = None
        self.subscan = None
        
    def showDialog(self):
        """Make the Translation Memory Setting dialog visible."""
        #lazy init
        if (not self.ui):
            self.ui = Ui_tmsetting()
            self.ui.setupUi(self)
            self.setWindowTitle("Setting Translation Memory")
            self.setModal(True)
            self.loadItemToList()
            self.connect(self.ui.btnAdd, QtCore.SIGNAL("clicked(bool)"), self.showFileDialog)
            self.filedialog = FileDialog.fileDialog(self)
            self.connect(self.filedialog, QtCore.SIGNAL("location"), self.addLocation)
            self.connect(self.ui.btnOk, QtCore.SIGNAL("clicked(bool)"), self.createTM)
            self.connect(self.ui.btnRemove, QtCore.SIGNAL("clicked(bool)"), self.removeLocation)
            self.connect(self.ui.btnRemoveAll, QtCore.SIGNAL("clicked(bool)"), self.ui.listWidget.clear)
            self.connect(self.ui.btnEnable, QtCore.SIGNAL("clicked(bool)"), self.setChecked)
            self.connect(self.ui.btnDisable, QtCore.SIGNAL("clicked(bool)"), self.setUnchecked)
            self.connect(self.ui.checkBox, QtCore.SIGNAL("stateChanged(int)"), self.rememberOptions)
            self.ui.listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.ui.checkBox.setChecked(World.settings.value("diveIntoSub").toBool())
        self.ui.progressBar.setValue(0)
        self.show()
    
    def loadItemToList(self):
        """Load remembered item to list."""
        TMpath = World.settings.value("TMPath").toStringList()
        disableTM = set(World.settings.value("disabledTM").toStringList())
        for path in TMpath:
            item = QtGui.QListWidgetItem(path)
            item.setCheckState((not path in disableTM) and QtCore.Qt.Checked or QtCore.Qt.Unchecked)
            self.ui.listWidget.addItem(item)
        
    def showFileDialog(self):
        """Show Translation Memory setting dialog."""
        self.filedialog.show()
    
    def addLocation(self, TMpath):
        """Add TMpath to TM list.
        
        @param TMpath: Filename as string
        
        """
        items = self.ui.listWidget.findItems(TMpath, QtCore.Qt.MatchCaseSensitive)
        if (not items):
            item = QtGui.QListWidgetItem(TMpath)
            item.setCheckState(QtCore.Qt.Checked)
            self.ui.listWidget.addItem(item)
    
    def removeLocation(self):
        """Remove selected path TM list."""
        items = self.ui.listWidget.selectedItems()
        for item in items:
            self.ui.listWidget.setCurrentItem(item)
            self.ui.listWidget.takeItem(self.ui.listWidget.currentRow())
            
    def rememberOptions(self):
        World.settings.setValue("diveIntoSub", QtCore.QVariant(self.ui.checkBox.isChecked()))
        
    def closeEvent(self, event):
        """Rememer TMpath before closing.
        
        @param event: CloseEvent Object
        
        """
        stringlist = QtCore.QStringList()
        for i in range(self.ui.listWidget.count()):
            path = self.ui.listWidget.item(i).text()
            stringlist.append(path)
        World.settings.setValue("TMPath", QtCore.QVariant(stringlist))
        QtGui.QDialog.closeEvent(self, event)
    
    def createTM(self):
        """Build base object of checked files in lists.
        
        @signal matcher: This signal is emitted when there is matcher
        
        """
        stringlist = []
        count = self.ui.listWidget.count()

        for i in range(count):
            item = self.ui.listWidget.item(i)
            if (item.checkState()):
                stringlist.append(item.text())
        
        matcher = None
        try:
            matcher = pickleTM.buildMatcher(stringlist)
        except Exception, e:
            self.emit(QtCore.SIGNAL("noTM"), str(e))
        
        self.emit(QtCore.SIGNAL("matcher"), matcher)
        self.close()

    def setChecked(self):
        """Set state of selectedItems as checked."""
        items = self.ui.listWidget.selectedItems()
        for item in items:
            item.setCheckState(QtCore.Qt.Checked)
        
    def setUnchecked(self):
        """Set state of selectedItems as unchecked."""
        items = self.ui.listWidget.selectedItems()
        for item in items:
            item.setCheckState(QtCore.Qt.Unchecked)
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tm = tmSetting(None)
    tm.showDialog()
    sys.exit(tm.exec_())

