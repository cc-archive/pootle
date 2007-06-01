#!/usr/bin/python
# -*- coding: utf8 -*-

# Pootling
# Copyright 2006 WordForge Foundation
#
# This program is free sofware; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your op tion) any later version.
#
# See the LICENSE file for more details. 
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module is working on source and target of current TU.

from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_TUview import Ui_TUview
from pootling.modules import World
from pootling.modules.highlighter import Highlighter

class TUview(QtGui.QDockWidget):
    def __init__(self, parent):
        QtGui.QDockWidget.__init__(self, parent)
        self.setObjectName("detailDock")
        self.setWindowTitle(self.tr("Detail"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_TUview()
        self.ui.setupUi(self.form)
        self.setWidget(self.form)
        self.setFeatures(QtGui.QDockWidget.DockWidgetClosable)
        self.ui.lblComment.hide()
        self.applySettings()
        self.connect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentIndex)
        
        # create highlighter
        self.sourceLength = 0
        
        self.sourceHighlighter = Highlighter(self.ui.txtSource)
        self.targetHighlighter = Highlighter(self.ui.txtTarget)
    
    def setPattern(self, patternList):
        """
        call highlighter.setPattern()
        """
        self.sourceHighlighter.setPattern(patternList)
    
    def setSearchString(self, searchString, textField):
        """
        call highlighter.setSearchString()
        """
        if (textField == World.source):
            self.sourceHighlighter.setSearchString(searchString)
            self.targetHighlighter.setSearchString("")
        elif (textField == World.target):
            self.targetHighlighter.setSearchString(searchString)
            self.sourceHighlighter.setSearchString("")
    
    def setHighlightGlossary(self, bool):
        """
        call highlighter.setHighlightGlossary()
        """
        self.sourceHighlighter.setHighlightGlossary(bool)
    
    def closeEvent(self, event):
        """
        set text of action object to 'show Detail' before closing TUview
        @param QCloseEvent Object: received close event when closing widget
        """
        QtGui.QDockWidget.closeEvent(self, event)
        self.toggleViewAction().setChecked(False)
    
    def setScrollbarValue(self, value):
        """@param value: the new value for the scrollbar"""
        if (value < 0):
            value = 0
        self.disconnect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentIndex)
        self.ui.fileScrollBar.setValue(value)
        self.connect(self.ui.fileScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.emitCurrentIndex)
        self.ui.fileScrollBar.setToolTip("%s / %s" % (value + 1,  self.ui.fileScrollBar.maximum() + 1))

    def filterChanged(self, filter, lenFilter):
        """Adjust the scrollbar maximum according to lenFilter.
        @param filter: helper constants for filtering
        @param lenFilter: len of filtered items."""
        self.viewSetting(lenFilter)
        self.ui.fileScrollBar.setMaximum(max(lenFilter - 1, 0))
        self.ui.fileScrollBar.setEnabled(bool(lenFilter))
    
    @QtCore.pyqtSignature("int")
    def emitCurrentIndex(self, value):
        """emit "scrollToRow" signal with value as row start from 0.
        @param value: current row."""
        self.emit(QtCore.SIGNAL("scrollToRow"), value)
    
    def getTargets(self):
        """
        return target of unit which is string or list of string (plural).
        """
        if ((not hasattr(self, "secondpage")) or  (not self.secondpage)):
            target = unicode(self.ui.txtTarget.toPlainText())
        else:
            target = []
            for i in range(self.ui.tabWidgetTarget.count()):
                textbox = self.ui.tabWidgetTarget.widget(i).children()[1]
                target.append(unicode(textbox.toPlainText()))
        return target
    
    def updateView(self, unit):
        """Update the text in source and target, set the scrollbar position,
        remove a value from scrollbar if the unit is not in filter.
        Then recalculate scrollbar maximum value.
        @param unit: unit to set in target and source.
        @param index: value in the scrollbar to be removed.""" 
        #self.disconnect(self.ui.txtTarget, QtCore.SIGNAL("textChanged()"), self.emitTargetChanged)
        self.disconnect(self.ui.txtTarget, QtCore.SIGNAL("textChanged()"), self.textChanged)
        if (not unit):
            return
        
        if hasattr(self, "contentDirty") and self.contentDirty:
            target = self.getTargets()
            self.emit(QtCore.SIGNAL("targetChanged"), target, self.lastUnit)
        self.contentDirty = False
        
        self.ui.txtTarget.setReadOnly(False)
        comment = unit.getcontext()
        comment += unit.getnotes("developer")
        if (comment == ""):
            self.ui.lblComment.hide()
        else:
            self.ui.lblComment.show()
            self.ui.lblComment.setText(unicode(comment))
        self.showUnit(unit)
        # set the scrollbar position
        self.setScrollbarValue(unit.x_editor_row)
        #self.connect(self.ui.txtTarget, QtCore.SIGNAL("textChanged()"), self.emitTargetChanged)
        self.connect(self.ui.txtTarget, QtCore.SIGNAL("textChanged()"), self.textChanged)
        
        self.lastUnit = unit
        
    def showUnit(self, unit):
        ''' show unit's source and target in a normal text box if unit is single or 
        in multi tab if unit is plural and number of plural forms setting is more than 1.

        @param unit: to show into source and target.
        '''
        if (not unit.hasplural()):
            """This will be called when unit is singular.
            @param unit: unit to consider if signal or not."""
            # hide tab for plural unit and show the normal text boxes for signal unit.
            # display on first page which is normal text box page
            self.secondpage = False
            self.ui.sourceStacked.setCurrentIndex(0)
            self.ui.targetStacked.setCurrentIndex(0)
            if (unicode(unit.source) !=  unicode(self.ui.txtSource.toPlainText())):
                self.ui.txtSource.setPlainText(unit.source)
                self.emit(QtCore.SIGNAL("lookupTranslation"))
            if (unicode(unit.target) !=  unicode(self.ui.txtTarget.toPlainText())):
                self.ui.txtTarget.setPlainText(unit.target)
                #move the cursor to the end of sentence.
                cursor = self.ui.txtTarget.textCursor()
                cursor.setPosition(len(unit.target))
                self.ui.txtTarget.setTextCursor(cursor)
        else:
            # create source tab
            self.ui.sourceStacked.setCurrentIndex(1)
            self.addRemoveTabWidget(self.ui.tabWidgetSource, len(unit.source.strings), unit.source.strings)
            
            # create target tab
            nplurals = World.settings.value("nPlural").toInt()[0]
            self.ui.targetStacked.setCurrentIndex((nplurals > 1) and 1 or 0)
            if (not (nplurals > 1)):
                if (unicode(unit.target) !=  unicode(self.ui.txtTarget.toPlainText())):
                    self.ui.txtTarget.setPlainText(unit.target)
                # display on first page which is normal text box page
                self.secondpage = False
            else:
                # display on second page which is tabwidget page; second page means unit is plural and number of plurals form setting is more than 1.
                self.secondpage = True
                self.addRemoveTabWidget(self.ui.tabWidgetTarget, nplurals, unit.target.strings)
                for i in range(self.ui.tabWidgetTarget.count()):
                    # make sure it is not emit signal targetchanged everytime when unit is updated.
                    textbox = self.ui.tabWidgetTarget.widget(i).children()[1]
                    textbox.setReadOnly(False)
                    #self.disconnect(textbox, QtCore.SIGNAL("textChanged()"), self.emitTargetChanged)
                    self.disconnect(textbox, QtCore.SIGNAL("textChanged()"), self.textChanged)
                    # everytime display a unit, connect signal
                    #self.connect(textbox, QtCore.SIGNAL("textChanged()"), self.emitTargetChanged)
                    self.connect(textbox, QtCore.SIGNAL("textChanged()"), self.textChanged)
        
    def addRemoveTabWidget(self, tabWidget, length, msg_strings):
        '''Add or remove tab to a Tab widget.
        
        @param tabWidget: QTabWidget
        @param length: amount of tab as int type
        @param msg_strings: list of strings to set to textbox in each tab of tabWidget
        
        '''
        count = tabWidget.count()
        if (not (count  == length)):
            while (count > length):
                count -= 1
                tabWidget.removeTab(count)
            while (count < length):
                count += 1
                widget = QtGui.QWidget()
                gridlayout = QtGui.QGridLayout(widget)
                gridlayout.setMargin(0)
                gridlayout.setSpacing(0)
                textedit = QtGui.QTextEdit()
                gridlayout.addWidget(textedit)
                tabWidget.addTab(widget, "Plural " + str(count))
            # add each source string of a unit to widget
        minloop = min(count, len(msg_strings))
        for i in range(minloop):
            textbox = tabWidget.widget(i).children()[1]
            if (unicode(msg_strings[i]) != unicode(textbox.toPlainText())):
                textbox.setPlainText(msg_strings[i])
            textbox.setReadOnly(True)
    
    
    def textChanged(self):
        """
        @emit textchanged signal for widget that need to update text while typing.
        """
        #TODO: emit targetChanged when target content is dirty, not by keypressed.
        self.contentDirty = True
        text = unicode(self.ui.txtTarget.toPlainText())
        self.emit(QtCore.SIGNAL("textChanged"), text)
    
##    def emitTargetChanged(self):
##        """
##        emit targetChanged signal if target in TUview is changed.
##        """
##        if ((not hasattr(self, "secondpage")) or  (not self.secondpage)):
##            self.emit(QtCore.SIGNAL("targetChanged"), unicode(self.ui.txtTarget.toPlainText()))
##        else:
##            list = []
##            for i in range(self.ui.tabWidgetTarget.count()):
##                textbox = self.ui.tabWidgetTarget.widget(i).children()[1]
##                list.append(unicode(textbox.toPlainText()))
##                # prevent infinit loop of textchanged signal everytime a plural unit target string is changed.
##                #self.disconnect(textbox, QtCore.SIGNAL("textChanged()"), self.emitTargetChanged)
##                self.disconnect(textbox, QtCore.SIGNAL("textChanged()"), self.textChanged)
##            self.emit(QtCore.SIGNAL("targetChanged"), list)
            
    def source2target(self):
        """Copy the text from source to target."""
        # if secondpage means unit is plural and number of plural forms setting is more than 1.
        if (self.secondpage):
            targettab =self.ui.tabWidgetTarget
            targettabindex = targettab.currentIndex()
            sourcetab = self.ui.tabWidgetSource
            sourcetabindex = sourcetab.currentIndex()
            targettab.widget(targettabindex).children()[1].setPlainText(sourcetab.widget(sourcetabindex).children()[1].toPlainText())
        else:
            # here targetview is always normal text box, but unit could be single or plural.
            sourceview_as_tab = self.ui.sourceStacked.currentIndex()
            if (not sourceview_as_tab):
                self.ui.txtTarget.setPlainText(self.ui.txtSource.toPlainText())
            else:
                sourcetab = self.ui.tabWidgetSource
                sourcetabindex = sourcetab.currentIndex()
                self.ui.txtTarget.setPlainText(sourcetab.widget(sourcetabindex).children()[1].toPlainText())
    
    def replaceText(self, textField, position, length, replacedText):
        """replace the string (at position and length) with replacedText in txtTarget.
        @param textField: source or target text box.
        @param position: old string's start point.
        @param length: old string's length.
        @param replacedText: string to replace."""
        if (textField != World.target):
            return
        text = self.ui.txtTarget.toPlainText()
        text.replace(position, length, replacedText);
        self.ui.txtTarget.setPlainText(text)

    def applySettings(self):
        """ set font and color to txtSource and txtTarget"""
        sourceColor = World.settings.value("tuSourceColor")
        if (sourceColor.isValid()):
            colorObj = QtGui.QColor(sourceColor.toString())
            palette = QtGui.QPalette(self.ui.txtSource.palette())
            palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            palette.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            self.ui.txtSource.setPalette(palette)

        targetColor = World.settings.value("tuTargetColor")
        if (targetColor.isValid()):
            colorObj = QtGui.QColor(targetColor.toString())
            palette = QtGui.QPalette(self.ui.txtTarget.palette())
            palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            palette.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            self.ui.txtTarget.setPalette(palette)

        fontObj = QtGui.QFont()
        sourcefont = World.settings.value("tuSourceFont")
        if (sourcefont.isValid() and fontObj.fromString(sourcefont.toString())):
            self.ui.txtSource.setFont(fontObj)
            self.ui.txtSource.setTabStopWidth(QtGui.QFontMetrics(fontObj).width("m"*8))

        targetfont = World.settings.value("tuTargetFont")
        if (targetfont.isValid() and fontObj.fromString(targetfont.toString())):
            self.ui.txtTarget.setFont(fontObj)
            self.ui.txtTarget.setTabStopWidth(QtGui.QFontMetrics(fontObj).width("m"*8))
    
    def viewSetting(self, arg = None):
        
        if (type(arg) is list):
            lenFilter = len(arg)
            self.ui.fileScrollBar.setMaximum(max(lenFilter - 1, 0))
            self.ui.fileScrollBar.setEnabled(bool(lenFilter))
        
        value = (arg and True or False)
        if (value == False):
            self.ui.lblComment.clear()
            self.ui.txtSource.clear()
            self.ui.txtTarget.clear()
            for i in range(self.ui.tabWidgetSource.count()):
                self.ui.tabWidgetSource.widget(i).children()[1].clear()
            for i in range(self.ui.tabWidgetTarget.count()):
                self.ui.tabWidgetTarget.widget(i).children()[1].clear()
        self.ui.lblComment.setVisible(value)
        self.ui.sourceStacked.setEnabled(value)
        self.ui.targetStacked.setEnabled(value)
    
if __name__ == "__main__":
    import sys, os
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    Form = TUview(None)
    Form.show()
    sys.exit(app.exec_())
