#!/usr/bin/python
# -*- coding: utf8 -*-

# Pootling
# Copyright 2006 WordForge Foundation
# Copyright 2006 WordForge Foundation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
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
# This module is working on Preferences


from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_Preference import Ui_frmPreference
from translate.lang import common
import pootling.modules.World as World
import translate.lang.data as data

class Preference(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = None

    def initUI(self):
        """ get values and display them """
        self.overviewFont = self.getFont(self.widget[0])
        self.setCaption(self.ui.lblOverView, self.overviewFont)
        self.ui.lblOverView.setWhatsThis("<h3>Overview Font</h3>Here, it will currently displayed font name, style and size of overview font on top Dock Widget Area of MainEditor.")
        self.tuSourceFont = self.getFont(self.widget[1])
        self.setCaption(self.ui.lblSource, self.tuSourceFont)
        self.ui.lblSource.setWhatsThis("<h3>Source Font</h3>Here, it will currently displayed font name, style and size of txtsource font on below overview of MainEditor.")
        self.tuTargetFont = self.getFont(self.widget[2])
        self.setCaption(self.ui.lblTarget, self.tuTargetFont )
        self.ui.lblTarget.setWhatsThis("<h3>Target Font</h3>Here, it will currently displayed font name, style and size of txtTarget font on below txtSource of MainEditor.")
        self.commentFont = self.getFont(self.widget[3])
        self.setCaption(self.ui.lblComment, self.commentFont)
        self.ui.lblComment.setWhatsThis("<h3>Comment Font</h3>Here, it will currently displayed font name, style and size of comment font on the right side of MainEditor.")
        self.overviewHeaderFont = self.getFont(self.widget[4])
        self.setCaption(self.ui.lblOverViewHeader, self.overviewHeaderFont)
        self.ui.lblOverViewHeader.setWhatsThis("<h3>Overview Header Font</h3>Here, it will currently displayed font name, style and size of overview header on MainEditor.")

        self.overviewColorObj = self.getColor(self.widget[0])
        self.setTextColor(self.ui.lblOverView, self.overviewColorObj)
        self.ui.lblOverView.setWhatsThis("<h3>Overview Color</h3>Here, it will currently displayed color of overview on top Dock Widget Area of MainEditor.")
        self.tuSourceColorObj = self.getColor(self.widget[1])
        self.setTextColor(self.ui.lblSource, self.tuSourceColorObj)
        self.ui.lblSource.setWhatsThis("<h3>Source Color</h3>Here, it will currently displayed color of txtSource on below overview of MainEditor.")
        self.tuTargetColorObj = self.getColor(self.widget[2])
        self.setTextColor(self.ui.lblTarget, self.tuTargetColorObj)
        self.ui.lblTarget.setWhatsThis("<h3>Target Color</h3>it will currently displayed color of txtTarget on below txtSource of MainEditor.")
        self.commentColorObj = self.getColor(self.widget[3])
        self.setTextColor(self.ui.lblComment, self.commentColorObj)
        self.ui.lblComment.setWhatsThis("<h3>Comment Color</h3>it will currently displayed color of comment on the right side of MainEditor.")

        self.ui.UserName.setText(World.settings.value("UserName").toString())
        self.ui.UserName.setWhatsThis("<h3>UserName</h3>User can fill in cell of own name.")
        self.ui.EmailAddress.setText(World.settings.value("EmailAddress").toString())
        self.ui.EmailAddress.setWhatsThis("<h3>EmailAddress</h3>User can fill in cell of own email.")
        self.ui.cbxFullLanguage.setEditText(World.settings.value("FullLanguage").toString())
        self.ui.cbxFullLanguage.setWhatsThis("<h3>Language</h3>Choose your own language.")
        self.ui.cbxLanguageCode.setEditText(World.settings.value("Code").toString())
        self.ui.cbxLanguageCode.setWhatsThis("<h3>Code</h3>Choose your own Code.")
        self.ui.SupportTeam.setText(World.settings.value("SupportTeam").toString())
        self.ui.SupportTeam.setWhatsThis("<h3>Support</h3>Type email support address.")
        self.ui.cbxTimeZone.setEditText(World.settings.value("TimeZone").toString())
        self.ui.cbxTimeZone.setWhatsThis("<h3>TimeZone</h3>Choose timeZone of your country.")
        self.ui.spinBox.setValue(World.settings.value("nPlural").toInt()[0])
        self.ui.spinBox.setWhatsThis("<h3>Singular/Plural forms</h3>Set plural forms for a specific language")
        self.ui.lineEqaution.setText(World.settings.value("equation").toString())
        self.ui.lineEqaution.setWhatsThis("<h3>Plural equation</h3>Set plural equation for a specific language. Pootling try to set this value for you. If no information provided, you should fill up by yourself. ")
        checkState = World.settings.value("headerAuto", QtCore.QVariant(True))
        if (checkState.toBool()):
            self.ui.chkHeaderAuto.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.chkHeaderAuto.setCheckState(QtCore.Qt.Unchecked)
        
        # TODO: set checkstateOptions of TM preference here when applicaiton is running
        TMpreference = World.settings.value("TMpreference").toInt()[0]
        self.ui.chbAutoTranslate.setChecked(TMpreference & 1 and True or False)
        self.ui.chbIgnoreFuzzy.setChecked(TMpreference & 2 and True or False)
        self.ui.chbAddTraslation.setChecked(TMpreference & 4 and True or False)
        
        GlossaryPreference = World.settings.value("GlossaryPreference").toInt()[0]
        self.ui.chbAutoIdentTerm.setChecked(GlossaryPreference & 1 and True or False)
        self.ui.chbChangeTerm.setChecked(GlossaryPreference & 2 and True or False)
        self.ui.chbMatchTerm.setChecked(GlossaryPreference & 4 and True or False)
        self.ui.chbDetectTerm.setChecked(GlossaryPreference & 8 and True or False)
        self.ui.chbAddNewTerm.setChecked(GlossaryPreference & 16 and True or False)
        self.ui.chbSuggestTranslation.setChecked(GlossaryPreference & 32 and True or False)
    
    def accepted(self):
        """ slot ok pressed """
        self.rememberFont(self.widget[0], self.overviewFont)
        self.rememberFont(self.widget[1], self.tuSourceFont)
        self.rememberFont(self.widget[2], self.tuTargetFont)
        self.rememberFont(self.widget[3], self.commentFont)
        self.rememberFont(self.widget[4], self.overviewHeaderFont)

        self.rememberColor(self.widget[0], self.overviewColorObj)
        self.rememberColor(self.widget[1], self.tuSourceColorObj)
        self.rememberColor(self.widget[2], self.tuTargetColorObj)
        self.rememberColor(self.widget[3], self.commentColorObj)

        World.settings.setValue("UserName", QtCore.QVariant(self.ui.UserName.text()))
        World.settings.setValue("EmailAddress", QtCore.QVariant(self.ui.EmailAddress.text()))
        World.settings.setValue("FullLanguage", QtCore.QVariant(self.ui.cbxFullLanguage.currentText()))
        World.settings.setValue("Code", QtCore.QVariant(self.ui.cbxLanguageCode.currentText()))
        World.settings.setValue("SupportTeam", QtCore.QVariant(self.ui.SupportTeam.text()))
        World.settings.setValue("TimeZone", QtCore.QVariant(self.ui.cbxTimeZone.currentText()))
        World.settings.setValue("nPlural", QtCore.QVariant(self.ui.spinBox.value()))
        World.settings.setValue("equation", QtCore.QVariant(self.ui.lineEqaution.text()))
        World.settings.setValue("headerAuto", QtCore.QVariant(self.ui.chkHeaderAuto.checkState() == QtCore.Qt.Checked))
        self.emit(QtCore.SIGNAL("settingsChanged"))

    def rememberFont(self, obj, fontObj):
        """ remember Font in Qsettings
        @param obj: input as string
        @param fontObj: stored font"""
        World.settings.setValue(str(obj + "Font"), QtCore.QVariant(fontObj.toString()))

    def rememberColor(self, obj, colorObj):
        """ remember Color in Qsettings
        @param obj: input as string
        @param colorObj: stored color"""
        World.settings.setValue(str(obj + "Color"), QtCore.QVariant(colorObj.name()))

    def fontOverview(self):
        """ slot to open font selection dialog """
        self.overviewFont = self.setFont(self.widget[0])
        self.setCaption(self.ui.lblOverView, self.overviewFont)
        
    def fontSource(self):
        """ slot to open font selection dialog """
        self.tuSourceFont = self.setFont(self.widget[1])
        self.setCaption(self.ui.lblSource, self.tuSourceFont)
        
    def fontTarget(self):
        """ slot to open font selection dialog """
        self.tuTargetFont = self.setFont(self.widget[2])
        self.setCaption(self.ui.lblTarget, self.tuTargetFont)

    def fontComment(self):
        """ slot to open font selection dialog """
        self.commentFont = self.setFont(self.widget[3])
        self.setCaption(self.ui.lblComment, self.commentFont)
        
    def fontOverviewHeader(self):
        """ slot to open font selection dialog """
        self.overviewHeaderFont = self.setFont(self.widget[4])
        self.setCaption(self.ui.lblOverViewHeader, self.overviewHeaderFont)

    def colorOverview(self):
        """ slot to open color selection dialog """
        self.overviewColorObj = self.setColor(self.widget[0])
        self.setTextColor(self.ui.lblOverView, self.overviewColorObj)

    def colorSource(self):
        """ slot to open color selection dialog """
        self.tuSourceColorObj = self.setColor(self.widget[1])
        self.setTextColor(self.ui.lblSource, self.tuSourceColorObj)

    def colorTarget(self):
        """ slot to open color selection dialog """
        self.tuTargetColorObj = self.setColor(self.widget[2])
        self.setTextColor(self.ui.lblTarget, self.tuTargetColorObj)

    def colorComment(self):
        """ slot to open font selection dialog """
        self.commentColorObj = self.setColor(self.widget[3])
        self.setTextColor(self.ui.lblComment, self.commentColorObj)

    def getFont(self, obj):
        """@return obj: font object created from settings
        @param obj: widget whose font is gotten from"""
        font = World.settings.value(str(obj + "Font"), QtCore.QVariant(self.defaultFont.toString()))
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
                return fontObj
        return self.defaultFont

    def getColor(self, obj):
        """@return obj: color object created from settings
        @param obj: widget whose color is gotten from"""
        color = World.settings.value(str(obj + "Color"), QtCore.QVariant(self.defaultColor.name()))
        colorObj = QtGui.QColor(color.toString())
        return colorObj

    def defaultFonts(self):
        """slot Set default fonts"""
        self.setCaption(self.ui.lblOverView, self.defaultFont)
        self.overviewFont = self.defaultFont
        self.setCaption(self.ui.lblOverViewHeader, self.defaultFont)
        self.overviewHeaderFont = self.defaultFont
        self.setCaption(self.ui.lblSource, self.defaultFont)
        self.tuSourceFont = self.defaultFont
        self.setCaption(self.ui.lblTarget, self.defaultFont)
        self.tuTargetFont = self.defaultFont
        self.setCaption(self.ui.lblComment, self.defaultFont)
        self.commentFont = self.defaultFont

    def defaultColors(self):
        """slot Set default colors"""
        self.setTextColor(self.ui.lblOverView, self.defaultColor)
        self.overviewColorObj = self.defaultColor
        self.setTextColor(self.ui.lblSource, self.defaultColor)
        self.tuSourceColorObj = self.defaultColor
        self.setTextColor(self.ui.lblTarget, self.defaultColor)
        self.tuTargetColorObj = self.defaultColor
        self.setTextColor(self.ui.lblComment, self.defaultColor)
        self.commentColorObj = self.defaultColor

    def setCaption(self, lbl, fontObj):
        """ create the text from the font object and set the widget lable
        @param lbl: label widget for setting Font information to
        @param fontObj:  font whose information is set to label widget"""
        newText = fontObj.family() +",  "+ str(fontObj.pointSize())
        if (fontObj.bold()):
            newText.append(", " + self.tr("bold"))
        if (fontObj.italic()):
            newText.append(", " + self.tr("italic"))
        if (fontObj.underline()):
            newText.append(", " + self.tr("underline"))
        lbl.setText(newText)
        
    def setTextColor(self, lbl, colorObj):
        """ set color to the text of lable widget
        @param lbl: label widget for setting color to
        @param colorObj: Color to set to label widget"""
        palette = QtGui.QPalette(lbl.palette())
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(QtGui.QPalette.WindowText), colorObj)
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(QtGui.QPalette.WindowText), colorObj)
        lbl.setPalette(palette)

    def setFont(self, obj):
        """ open font dialog 
        @return selected new font object or the old one if cancel was pressed 
        @param obj: widget whose font is gotten from"""
        oldFont = self.getFont(obj)
        newFont, okPressed = QtGui.QFontDialog.getFont(oldFont)
        if (okPressed):
            return newFont
        return oldFont

    def setColor(self, obj):
        """ open color dialog 
        @return selected new color object or the old one if cancel was pressed
        @param obj: widget whose color is gotten from"""
        oldColor = self.getColor(obj)
        newColor = QtGui.QColorDialog.getColor(QtCore.Qt.white)
        if (newColor.isValid()):
            return newColor
        return oldColor
       
    def showDialog(self):
        """ make the dialog visible """
        # lazy init 
        if (not self.ui):
            self.setWindowTitle(self.tr("Preferences"))
            self.setModal(True)
            self.defaultFont = QtGui.QFont("Serif", 10)
            self.defaultColor = QtGui.QColor(QtCore.Qt.black)
            self.ui = Ui_frmPreference()
            self.ui.setupUi(self)
            self.ui.listWidget.addItem(QtGui.QListWidgetItem(QtGui.QIcon("../images/identity.png"), self.tr("Personalize")))
            self.ui.listWidget.addItem(QtGui.QListWidgetItem(QtGui.QIcon("../images/colorize.png"), self.tr("Font & Color")))
            self.ui.listWidget.addItem(QtGui.QListWidgetItem(QtGui.QIcon("../images/memory.png"), self.tr("Glossary-TM")))
            self.ui.listWidget.setViewMode(QtGui.QListView.IconMode)
            self.ui.listWidget.setCurrentRow(0)
            self.ui.listWidget.setResizeMode(QtGui.QListView.Fixed)
            self.ui.listWidget.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
            self.connect(self.ui.listWidget, QtCore.SIGNAL("currentRowChanged(int)"), self.changedPaged)
            
            # TM page signals
            self.connect(self.ui.chbAutoTranslate, QtCore.SIGNAL("stateChanged(int)"), self.emitTMOptions)
            self.connect(self.ui.chbIgnoreFuzzy, QtCore.SIGNAL("stateChanged(int)"), self.emitTMOptions)
            self.connect(self.ui.chbAddTraslation, QtCore.SIGNAL("stateChanged(int)"), self.emitTMOptions)
            
            # Glossary page signals
            self.connect(self.ui.chbAutoIdentTerm, QtCore.SIGNAL("stateChanged(int)"), self.emitGlossaryOptions)
            self.connect(self.ui.chbChangeTerm, QtCore.SIGNAL("stateChanged(int)"), self.emitGlossaryOptions)
            self.connect(self.ui.chbMatchTerm, QtCore.SIGNAL("stateChanged(int)"), self.emitGlossaryOptions)
            self.connect(self.ui.chbDetectTerm, QtCore.SIGNAL("stateChanged(int)"), self.emitGlossaryOptions)
            self.connect(self.ui.chbAddNewTerm, QtCore.SIGNAL("stateChanged(int)"), self.emitGlossaryOptions)
            self.connect(self.ui.chbSuggestTranslation, QtCore.SIGNAL("stateChanged(int)"), self.emitGlossaryOptions)
            
            # connect signals
            self.connect(self.ui.chkHeaderAuto, QtCore.SIGNAL("stateChanged(int)"), self.ui.chkHeaderAuto.checkState) 
            self.connect(self.ui.bntFontOverview, QtCore.SIGNAL("clicked()"), self.fontOverview) 
            self.ui.bntFontOverview.setWhatsThis("<h3>Overview Font</h3>You can click Choose button and select color ever you want to be used on Overview.")
            self.connect(self.ui.bntFontOverviewHeader, QtCore.SIGNAL("clicked()"), self.fontOverviewHeader)
            self.ui.bntFontOverviewHeader.setWhatsThis("<h3>Overview Header Font</h3>You can click Choose button and select color ever you want to be used on Overview Header.")
            self.connect(self.ui.bntFontSource, QtCore.SIGNAL("clicked()"), self.fontSource) 
            self.ui.bntFontSource.setWhatsThis("<h3>Source Font</h3>You can click Choose button and select color ever you want to be used on txtSource.")
            self.connect(self.ui.bntFontTarget, QtCore.SIGNAL("clicked()"), self.fontTarget)
            self.ui.bntFontTarget.setWhatsThis("<h3>Target Font</h3>You can click Choose button and select color ever you want to be used on txtTarget.")
            self.connect(self.ui.bntFontComment, QtCore.SIGNAL("clicked()"), self.fontComment) 
            self.ui.bntFontComment.setWhatsThis("<h3>Comment Font</h3>You can click Choose button and select color ever you want to be used on Comment.")
            self.connect(self.ui.bntDefaultsFont, QtCore.SIGNAL("clicked()"), self.defaultFonts)
            self.ui.bntDefaultsFont.setWhatsThis("<h3>Defaults font</h3>You can click here if you would like Overview, Overview Header, Source, Target and Comment as default font.")

            # for color
            self.connect(self.ui.btnColorComment, QtCore.SIGNAL("clicked()"), self.colorComment) 
            self.ui.btnColorComment.setWhatsThis("<h3>Comment Color</h3>You can click Choose button and select color ever you want to be used on Comment.")
            self.connect(self.ui.btnColorSource, QtCore.SIGNAL("clicked()"), self.colorSource) 
            self.ui.btnColorSource.setWhatsThis("<h3>Source Color</h3>You can click Choose button and select color ever you want to be used on txtSource.")
            self.connect(self.ui.btnColorTarget, QtCore.SIGNAL("clicked()"), self.colorTarget) 
            self.ui.btnColorTarget.setWhatsThis("<h3>Target Color</h3>You can click Choose button and select color ever you want to be used on txtTarget.")
            self.connect(self.ui.btnColorOverview, QtCore.SIGNAL("clicked()"), self.colorOverview) 
            self.ui.btnColorOverview.setWhatsThis("<h3>Overview Color</h3>You can click Choose button and select color ever you want to be used on Overview.")
            self.connect(self.ui.bntDefaultsColor, QtCore.SIGNAL("clicked()"), self.defaultColors)
            self.ui.bntDefaultsColor.setWhatsThis("<h3>Defaults color</h3>You can click here if you would like Overview, Source, Target and Comment as default color.")
            
            self.connect(self.ui.okButton, QtCore.SIGNAL("clicked()"), self.accepted)
            self.connect(self.ui.cbxFullLanguage, QtCore.SIGNAL("currentIndexChanged(int)"), self.setCodeIndex)
            self.connect(self.ui.cbxLanguageCode, QtCore.SIGNAL("currentIndexChanged(int)"), self.setLanguageIndex)
            self.connect(self.ui.cbxLanguageCode, QtCore.SIGNAL("currentIndexChanged(const QString &)"), self.setNPlural)
            self.widget = ["overview","tuSource","tuTarget","comment", "overviewHeader"]
            code =[]
            language = []
            for langCode, langInfo in data.languages.iteritems():
                code.append(langCode)
                language.append(langInfo[0])
                
            self.ui.cbxFullLanguage.addItems(language)
            self.ui.cbxLanguageCode.addItems(code)
            timeZone = ['(GMT-11:00) Midway Island, Samoa','(GMT-10:00) Hawaii','(GMT-09:00) Alaska','(GMT-08:00) Pacific Time(US & Canada); Tijuana','(GMT-07:00) Arizona','(GMT-07:00) Chihuahua, La Paz, Mazatlan','(GMT-07:00) Mountain Time(US & Canada)','(GMT-06:00) Central America','(GMT-06:00) Central Time(US & Canada)','(GMT-06:00) Guadalajara, Mexico City, Monterrey ','(GMT-06:00) Saskatchewan','(GMT-05:00) Bogota, Lima, Quito','(GMT-05:00) Eastern Time(US & Canada)','(GMT-05:00) Indiana (East)','(GMT-04:00) Atlantic Time (Canada)','(GMT-04:00) Caracas, La Paz','(GMT-04:00) Santiago','(GMT-03:30) NewFoundland','(GMT-03:00) Brasilia','(GMT-03:00) Buenos Aires, Georgetown','(GMT-03:00) Greenland','(GMT-02:00) Mid-Atlantic','(GMT-01:00) Azores','(GMT-01:00) Cape Verde Is.','(GMT) Casablanca, Monrovia','(GMT) Greenwich Mean Time: Dublin, Edinburgh, Lisbon, London','(GMT+01:00) Amsterdam, Berlin, Bern, Rome, Stockholm, Viena','(GMT+01:00) Belgrade, Bratislava, Budapest, Ljubljana, Prague','(GMT+01:00) Brussels, Copenhagen, Madrid, Paris','(GMT+01:00) Sarajevo, Skopje, Warsaw, Zagreb','(GMT+01:00) West Central Africa','(GMT+02:00) Athens, Beirut, Istanbul, Minsk','(GMT+02:00)  Bucharest','(GMT+02:00) Cairo','(GMT+02:00) Harare, Pretoria','(GMT+02:00) Helsinki, kyiv, Riga, Sofia, Tailinn, Vilnius','(GMT+02:00) Jerusalem','(GMT+03:00) Baghdad','(GMT+03:00) Brasilia','(GMT+03:00) Kuwait, Riyadh','(GMT+03:00) Moscow, St. Petersburg, Volgograd','(GMT+03:00) Nairobi','(GMT+03:30) Tehran','(GMT+04:00) Abu Dhabi, Muscat','(GMT+04:00) Baku, Tbilisi, Yerevan','(GMT+04:30) Kabul','(GMT+05:00) Ekaterinburg','(GMT+05:00) Islamabad, Karachi, Tashkent','(GMT+05:30) Chennai, Kolkata, Mumbia, New Delhi','(GMT+05:45) Kathmandu','(GMT+06:00) Almaty, Novosibirsk','(GMT+06:00) Astana, Dhaka','(GMT+06:00) Sri Jayawardenpura','(GMT+06:30) Rangoon','(GMT+07:00) Bangkok, Hanoi, Jakarta','(GMT+07:00) Krasnoyarsk','(GMT+08:00) Beijing, Chongging, Hong Kong, Urumqi','(GMT+08:00) Irkutsk, UlaanBataar','(GMT+08:00)   Kuala Lumpur, Singapore','(GMT+08:00) Perth','(GMT+08:00) Taipei','(GMT+08:00) Osaka, Sapporo, Tokyo','(GMT+09:00) Seoul','(GMT+09:00) Yakutsk','(GMT+09:30) Adelaide','(GMT+09:30) Darwin','(GMT+10:00) Brisbane','(GMT+10:00) Canberra, Melbourne, Sydney','(GMT+10:00)   Guam, Port Moresby','(GMT+10:00) Hobert','(GMT+10:00) Vladivostok','(GMT+11:00) Magada, Solomon Is, New Caledonia','(GMT+12:00) Auckland, Wellington','(GMT+12:00) Fiji, Kamchatka, Marshall Is','(GMT+13:00) Nuku alofa']
            self.ui.cbxTimeZone.addItems(timeZone)
        self.initUI()
        self.show()
        
    def setCodeIndex(self, index):
        """SetIndex for language code combo box.
        @param index: list's item correspond to index """
        self.ui.cbxLanguageCode.setCurrentIndex(index)
  
    def setLanguageIndex(self, index):
        """SetIndex for language name combo box.
        @param index: list's item correspond to index """
        self.ui.cbxFullLanguage.setCurrentIndex(index)
    
    def setNPlural(self, langCode):
        """Set nplurals for specific language.
        @param langCode: as Qstring type. """
        language = common.Common(str(langCode))
        self.ui.spinBox.setValue(language.nplurals)
        self.ui.lineEqaution.setText(language.pluralequation)
    
    def changedPaged(self):
        '''show a page of stackedWidget according to selected item in listwidget.
        '''
        self.ui.stackedWidget.setCurrentIndex(self.ui.listWidget.currentRow())
    
    def emitTMOptions(self):
        TMpreference = 0
        if (self.ui.chbAutoTranslate.isChecked()):
            TMpreference +=1
        if (self.ui.chbIgnoreFuzzy.isChecked()):
            TMpreference +=2
        if (self.ui.chbAddTraslation.isChecked()):
            TMpreference +=4
        self.emit(QtCore.SIGNAL("TMpreference"), TMpreference)
        World.settings.setValue("TMpreference", QtCore.QVariant(TMpreference))
    
    def emitGlossaryOptions(self):
        GlossaryPreference = 0
        if (self.ui.chbAutoIdentTerm.isChecked()):
            GlossaryPreference +=1
        if (self.ui.chbChangeTerm.isChecked()):
            GlossaryPreference +=2
        if (self.ui.chbMatchTerm.isChecked()):
            GlossaryPreference +=4
        if (self.ui.chbDetectTerm.isChecked()):
            GlossaryPreference +=8
        if (self.ui.chbAddNewTerm.isChecked()):
            GlossaryPreference +=16
        if (self.ui.chbSuggestTranslation.isChecked()):
            GlossaryPreference +=32
        self.emit(QtCore.SIGNAL("GlossaryPreference"), GlossaryPreference)
        World.settings.setValue("GlossaryPreference", QtCore.QVariant(GlossaryPreference))
    
if __name__ == "__main__":
    import sys, os
    # set the path for QT in order to find the icons
    QtCore.QDir.setCurrent(os.path.join(sys.path[0], "..", "ui"))
    app = QtGui.QApplication(sys.argv)
    user = Preference(None)
    user.showDialog()
    sys.exit(app.exec_())
