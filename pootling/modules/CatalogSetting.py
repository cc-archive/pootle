#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Pootling
# Copyright 2006 WordForge Foundation
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
# This module is providing an setting path of catalog dialog 

import sys, os
from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_CatalogSetting import Ui_catalogSetting
from pootling.modules import World

class CatalogSetting(QtGui.QDialog):
    """
    Code for setting path of catalog dialog
    """
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_catalogSetting()
        self.ui.setupUi(self)
        self.setWindowTitle("Setting Catalog Manager")
        self.connect(self.ui.btnAdd, QtCore.SIGNAL("clicked(bool)"), self.showFileDialog)
        self.connect(self.ui.btnOk, QtCore.SIGNAL("clicked(bool)"), QtCore.SLOT("close()"))
        self.connect(self.ui.btnDelete, QtCore.SIGNAL("clicked(bool)"), self.removeLocation)
        self.connect(self.ui.btnClear, QtCore.SIGNAL("clicked(bool)"), self.clearLocation)
        self.connect(self.ui.btnMoveUp, QtCore.SIGNAL("clicked(bool)"), self.moveUp)
        self.connect(self.ui.btnMoveDown, QtCore.SIGNAL("clicked(bool)"), self.moveDown)
        self.connect(self.ui.chbDiveIntoSubfolders, QtCore.SIGNAL("stateChanged(int)"), self.rememberDive)
        self.setModal(True)
        
        self.catalogModified = False
        
    def showFileDialog(self):
        """
        Open the file dialog where you can choose both file and directory.
        Add path to Catalog list.
        """
        self.directory = World.settings.value("workingDir").toString()
        dialog = QtGui.QFileDialog()
        filenames = dialog.getOpenFileNames(
                    self,
                    self.tr("Open File"),
                    self.directory,
                    self.tr("All Supported Files (*.po *.pot *.xliff *.xlf *.tmx *.tbx);;PO Files and PO Template Files (*.po *.pot);;XLIFF Files (*.xliff *.xlf);;Translation Memory eXchange (TMX) Files (*.tmx);;TermBase eXchange (TBX) Files (*.tbx);;All Files (*)"))
        
        if (filenames):
            for filename in filenames:
                items = self.ui.listWidget.findItems(filename, QtCore.Qt.MatchCaseSensitive)
                if (not items):
                    item = QtGui.QListWidgetItem(filename)
                    self.ui.listWidget.addItem(item)
                    self.catalogModified = True
    
    def clearLocation(self):
        """Clear all paths from the Catalog List and also unchecked DiveIntoSubCatalog checkbox."""
        self.ui.listWidget.clear()
        self.catalogModified = True
        self.ui.chbDiveIntoSubfolders.setChecked(False)
    
    def removeLocation(self):
        """Remove the selected path from the Catalog list."""
        self.ui.listWidget.takeItem(self.ui.listWidget.currentRow())
        self.catalogModified = True
    
    def moveItem(self, distance):
        '''move an item up or down depending on distance
        @param distance: int'''
        currentrow = self.ui.listWidget.currentRow()
        currentItem = self.ui.listWidget.item(currentrow)
        distanceItem = self.ui.listWidget.item(currentrow + distance)
        if (distanceItem):
            temp = distanceItem.text()
            distanceItem.setText(currentItem.text())
            currentItem.setText(temp)
            self.ui.listWidget.setCurrentRow(currentrow + distance)
        
    def moveUp(self):
        '''move item up'''
        self.moveItem(-1)
    
    def moveDown(self):
        '''move item down'''
        self.moveItem(1)
    
    def rememberDive(self):
        """ Remember the check state of diveIntoSubCatalog"""
        World.settings.setValue("diveIntoSubCatalog", QtCore.QVariant(self.ui.chbDiveIntoSubfolders.isChecked()))
        self.catalogModified = True
    
    def showEvent(self, event):
        self.ui.listWidget.clear()
        self.ui.listWidget.addItems(World.settings.value("CatalogPath").toStringList())
        self.ui.chbDiveIntoSubfolders.setChecked(World.settings.value("diveIntoSubCatalog").toBool())
    
    def closeEvent(self, event):
        """
        Save CatalogPath to Qsettings before closing dialog. Then emit singnal updateCatalog.
        @param QCloseEvent Object: received close event when closing widget
        
        @signal updateCatalog: emitted when CatalogPath is modified.
        """
        stringlist = QtCore.QStringList()
        for i in range(self.ui.listWidget.count()):
            stringlist.append(self.ui.listWidget.item(i).text())
        World.settings.setValue("CatalogPath", QtCore.QVariant(stringlist))
        QtGui.QDialog.closeEvent(self, event)
        
        if (self.catalogModified):
            self.emit(QtCore.SIGNAL("updateCatalog"))
            self.catalogModified = False


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    tm = CatalogSetting(None)
    tm.show()
    sys.exit(tm.exec_())

