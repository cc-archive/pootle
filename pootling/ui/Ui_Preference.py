# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ks/programming/wordforge/trunk/pootling/ui/Preference.ui'
#
# Created: Mon Mar 19 18:00:58 2007
#      by: PyQt4 UI code generator 4-snapshot-20070212
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_frmPreference(object):
    def setupUi(self, frmPreference):
        frmPreference.setObjectName("frmPreference")
        frmPreference.resize(QtCore.QSize(QtCore.QRect(0,0,582,459).size()).expandedTo(frmPreference.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmPreference.sizePolicy().hasHeightForWidth())
        frmPreference.setSizePolicy(sizePolicy)

        self.gridlayout = QtGui.QGridLayout(frmPreference)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.stackedWidget = QtGui.QStackedWidget(frmPreference)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.stackedWidget.setFrameShape(QtGui.QFrame.StyledPanel)
        self.stackedWidget.setFrameShadow(QtGui.QFrame.Plain)
        self.stackedWidget.setLineWidth(1)
        self.stackedWidget.setObjectName("stackedWidget")

        self.personal = QtGui.QWidget()
        self.personal.setObjectName("personal")

        self.gridlayout1 = QtGui.QGridLayout(self.personal)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem,5,0,1,1)

        self.frame_2 = QtGui.QFrame(self.personal)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")

        self.gridlayout2 = QtGui.QGridLayout(self.frame_2)
        self.gridlayout2.setMargin(9)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        self.lineEqaution = QtGui.QLineEdit(self.frame_2)
        self.lineEqaution.setObjectName("lineEqaution")
        self.gridlayout2.addWidget(self.lineEqaution,2,0,1,2)

        self.label_2 = QtGui.QLabel(self.frame_2)
        self.label_2.setObjectName("label_2")
        self.gridlayout2.addWidget(self.label_2,1,0,1,1)

        self.label_3 = QtGui.QLabel(self.frame_2)
        self.label_3.setObjectName("label_3")
        self.gridlayout2.addWidget(self.label_3,0,0,1,1)

        self.spinBox = QtGui.QSpinBox(self.frame_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBox.sizePolicy().hasHeightForWidth())
        self.spinBox.setSizePolicy(sizePolicy)
        self.spinBox.setMaximum(10)
        self.spinBox.setMinimum(1)
        self.spinBox.setSingleStep(1)
        self.spinBox.setProperty("value",QtCore.QVariant(2))
        self.spinBox.setObjectName("spinBox")
        self.gridlayout2.addWidget(self.spinBox,0,1,1,1)
        self.gridlayout1.addWidget(self.frame_2,3,0,1,1)

        self.frame = QtGui.QFrame(self.personal)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFocusPolicy(QtCore.Qt.NoFocus)
        self.frame.setAutoFillBackground(True)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.gridlayout3 = QtGui.QGridLayout(self.frame)
        self.gridlayout3.setMargin(9)
        self.gridlayout3.setSpacing(6)
        self.gridlayout3.setObjectName("gridlayout3")

        self.label5 = QtGui.QLabel(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label5.sizePolicy().hasHeightForWidth())
        self.label5.setSizePolicy(sizePolicy)
        self.label5.setObjectName("label5")
        self.gridlayout3.addWidget(self.label5,3,0,1,1)

        self.cbxLanguageCode = QtGui.QComboBox(self.frame)
        self.cbxLanguageCode.setEnabled(True)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxLanguageCode.sizePolicy().hasHeightForWidth())
        self.cbxLanguageCode.setSizePolicy(sizePolicy)
        self.cbxLanguageCode.setAcceptDrops(False)
        self.cbxLanguageCode.setEditable(True)
        self.cbxLanguageCode.setObjectName("cbxLanguageCode")
        self.gridlayout3.addWidget(self.cbxLanguageCode,2,3,1,1)

        self.label6 = QtGui.QLabel(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label6.sizePolicy().hasHeightForWidth())
        self.label6.setSizePolicy(sizePolicy)
        self.label6.setObjectName("label6")
        self.gridlayout3.addWidget(self.label6,4,0,1,1)

        self.cbxFullLanguage = QtGui.QComboBox(self.frame)
        self.cbxFullLanguage.setEnabled(True)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxFullLanguage.sizePolicy().hasHeightForWidth())
        self.cbxFullLanguage.setSizePolicy(sizePolicy)
        self.cbxFullLanguage.setEditable(True)
        self.cbxFullLanguage.setObjectName("cbxFullLanguage")
        self.gridlayout3.addWidget(self.cbxFullLanguage,2,1,1,1)

        self.cbxTimeZone = QtGui.QComboBox(self.frame)
        self.cbxTimeZone.setEnabled(True)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxTimeZone.sizePolicy().hasHeightForWidth())
        self.cbxTimeZone.setSizePolicy(sizePolicy)
        self.cbxTimeZone.setEditable(True)
        self.cbxTimeZone.setObjectName("cbxTimeZone")
        self.gridlayout3.addWidget(self.cbxTimeZone,4,1,1,3)

        self.label1 = QtGui.QLabel(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label1.sizePolicy().hasHeightForWidth())
        self.label1.setSizePolicy(sizePolicy)
        self.label1.setTextFormat(QtCore.Qt.AutoText)
        self.label1.setObjectName("label1")
        self.gridlayout3.addWidget(self.label1,0,0,1,1)

        self.label3 = QtGui.QLabel(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label3.sizePolicy().hasHeightForWidth())
        self.label3.setSizePolicy(sizePolicy)
        self.label3.setObjectName("label3")
        self.gridlayout3.addWidget(self.label3,2,0,1,1)

        self.label2 = QtGui.QLabel(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label2.sizePolicy().hasHeightForWidth())
        self.label2.setSizePolicy(sizePolicy)
        self.label2.setObjectName("label2")
        self.gridlayout3.addWidget(self.label2,1,0,1,1)

        self.label4 = QtGui.QLabel(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label4.sizePolicy().hasHeightForWidth())
        self.label4.setSizePolicy(sizePolicy)
        self.label4.setObjectName("label4")
        self.gridlayout3.addWidget(self.label4,2,2,1,1)

        self.UserName = QtGui.QLineEdit(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.UserName.sizePolicy().hasHeightForWidth())
        self.UserName.setSizePolicy(sizePolicy)
        self.UserName.setMaxLength(32768)
        self.UserName.setObjectName("UserName")
        self.gridlayout3.addWidget(self.UserName,0,1,1,3)

        self.EmailAddress = QtGui.QLineEdit(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.EmailAddress.sizePolicy().hasHeightForWidth())
        self.EmailAddress.setSizePolicy(sizePolicy)
        self.EmailAddress.setObjectName("EmailAddress")
        self.gridlayout3.addWidget(self.EmailAddress,1,1,1,3)

        self.SupportTeam = QtGui.QLineEdit(self.frame)
        self.SupportTeam.setObjectName("SupportTeam")
        self.gridlayout3.addWidget(self.SupportTeam,3,1,1,3)
        self.gridlayout1.addWidget(self.frame,2,0,1,1)

        self.label = QtGui.QLabel(self.personal)

        font = QtGui.QFont(self.label.font())
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridlayout1.addWidget(self.label,0,0,1,1)

        self.line = QtGui.QFrame(self.personal)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridlayout1.addWidget(self.line,1,0,1,1)

        self.chkHeaderAuto = QtGui.QCheckBox(self.personal)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkHeaderAuto.sizePolicy().hasHeightForWidth())
        self.chkHeaderAuto.setSizePolicy(sizePolicy)
        self.chkHeaderAuto.setChecked(True)
        self.chkHeaderAuto.setObjectName("chkHeaderAuto")
        self.gridlayout1.addWidget(self.chkHeaderAuto,4,0,1,1)
        self.stackedWidget.addWidget(self.personal)

        self.interface = QtGui.QWidget()
        self.interface.setObjectName("interface")

        self.gridlayout4 = QtGui.QGridLayout(self.interface)
        self.gridlayout4.setMargin(9)
        self.gridlayout4.setSpacing(6)
        self.gridlayout4.setObjectName("gridlayout4")

        self.label_4 = QtGui.QLabel(self.interface)

        font = QtGui.QFont(self.label_4.font())
        font.setPointSize(9)
        font.setWeight(75)
        font.setBold(True)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridlayout4.addWidget(self.label_4,0,0,1,1)

        self.line_2 = QtGui.QFrame(self.interface)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridlayout4.addWidget(self.line_2,1,0,1,3)

        self.frame2 = QtGui.QFrame(self.interface)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame2.sizePolicy().hasHeightForWidth())
        self.frame2.setSizePolicy(sizePolicy)
        self.frame2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame2.setObjectName("frame2")

        self.gridlayout5 = QtGui.QGridLayout(self.frame2)
        self.gridlayout5.setMargin(9)
        self.gridlayout5.setSpacing(6)
        self.gridlayout5.setObjectName("gridlayout5")

        self.label2_4 = QtGui.QLabel(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label2_4.sizePolicy().hasHeightForWidth())
        self.label2_4.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.label2_4.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label2_4.setFont(font)
        self.label2_4.setScaledContents(True)
        self.label2_4.setWordWrap(True)
        self.label2_4.setIndent(0)
        self.label2_4.setObjectName("label2_4")
        self.gridlayout5.addWidget(self.label2_4,0,0,1,1)

        self.bntFontOverviewHeader = QtGui.QPushButton(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bntFontOverviewHeader.sizePolicy().hasHeightForWidth())
        self.bntFontOverviewHeader.setSizePolicy(sizePolicy)
        self.bntFontOverviewHeader.setObjectName("bntFontOverviewHeader")
        self.gridlayout5.addWidget(self.bntFontOverviewHeader,0,2,1,1)

        self.lblOverViewHeader = QtGui.QLabel(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblOverViewHeader.sizePolicy().hasHeightForWidth())
        self.lblOverViewHeader.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.lblOverViewHeader.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblOverViewHeader.setFont(font)
        self.lblOverViewHeader.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblOverViewHeader.setObjectName("lblOverViewHeader")
        self.gridlayout5.addWidget(self.lblOverViewHeader,0,1,1,1)

        self.btnColorOverview = QtGui.QPushButton(self.frame2)
        self.btnColorOverview.setObjectName("btnColorOverview")
        self.gridlayout5.addWidget(self.btnColorOverview,1,3,1,1)

        self.bntFontOverview = QtGui.QPushButton(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bntFontOverview.sizePolicy().hasHeightForWidth())
        self.bntFontOverview.setSizePolicy(sizePolicy)
        self.bntFontOverview.setObjectName("bntFontOverview")
        self.gridlayout5.addWidget(self.bntFontOverview,1,2,1,1)

        self.lblOverView = QtGui.QLabel(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblOverView.sizePolicy().hasHeightForWidth())
        self.lblOverView.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.lblOverView.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblOverView.setFont(font)
        self.lblOverView.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblOverView.setObjectName("lblOverView")
        self.gridlayout5.addWidget(self.lblOverView,1,1,1,1)

        self.label2_5 = QtGui.QLabel(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label2_5.sizePolicy().hasHeightForWidth())
        self.label2_5.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.label2_5.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label2_5.setFont(font)
        self.label2_5.setScaledContents(True)
        self.label2_5.setWordWrap(True)
        self.label2_5.setIndent(0)
        self.label2_5.setObjectName("label2_5")
        self.gridlayout5.addWidget(self.label2_5,1,0,1,1)

        self.bntFontTarget = QtGui.QPushButton(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bntFontTarget.sizePolicy().hasHeightForWidth())
        self.bntFontTarget.setSizePolicy(sizePolicy)
        self.bntFontTarget.setObjectName("bntFontTarget")
        self.gridlayout5.addWidget(self.bntFontTarget,3,2,1,1)

        self.lblComment = QtGui.QLabel(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblComment.sizePolicy().hasHeightForWidth())
        self.lblComment.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.lblComment.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblComment.setFont(font)
        self.lblComment.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblComment.setObjectName("lblComment")
        self.gridlayout5.addWidget(self.lblComment,4,1,1,1)

        self.lblTarget = QtGui.QLabel(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblTarget.sizePolicy().hasHeightForWidth())
        self.lblTarget.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.lblTarget.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblTarget.setFont(font)
        self.lblTarget.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblTarget.setObjectName("lblTarget")
        self.gridlayout5.addWidget(self.lblTarget,3,1,1,1)

        self.lblSource = QtGui.QLabel(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblSource.sizePolicy().hasHeightForWidth())
        self.lblSource.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.lblSource.font())
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblSource.setFont(font)
        self.lblSource.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblSource.setObjectName("lblSource")
        self.gridlayout5.addWidget(self.lblSource,2,1,1,1)

        self.Source_2 = QtGui.QLabel(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Source_2.sizePolicy().hasHeightForWidth())
        self.Source_2.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.Source_2.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.Source_2.setFont(font)
        self.Source_2.setObjectName("Source_2")
        self.gridlayout5.addWidget(self.Source_2,2,0,1,1)

        self.bntFontSource = QtGui.QPushButton(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bntFontSource.sizePolicy().hasHeightForWidth())
        self.bntFontSource.setSizePolicy(sizePolicy)
        self.bntFontSource.setObjectName("bntFontSource")
        self.gridlayout5.addWidget(self.bntFontSource,2,2,1,1)

        self.lblsupportteam_2 = QtGui.QLabel(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblsupportteam_2.sizePolicy().hasHeightForWidth())
        self.lblsupportteam_2.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.lblsupportteam_2.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.lblsupportteam_2.setFont(font)
        self.lblsupportteam_2.setObjectName("lblsupportteam_2")
        self.gridlayout5.addWidget(self.lblsupportteam_2,4,0,1,1)

        self.bntFontComment = QtGui.QPushButton(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bntFontComment.sizePolicy().hasHeightForWidth())
        self.bntFontComment.setSizePolicy(sizePolicy)
        self.bntFontComment.setObjectName("bntFontComment")
        self.gridlayout5.addWidget(self.bntFontComment,4,2,1,1)

        self.label4_3 = QtGui.QLabel(self.frame2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label4_3.sizePolicy().hasHeightForWidth())
        self.label4_3.setSizePolicy(sizePolicy)

        font = QtGui.QFont(self.label4_3.font())
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label4_3.setFont(font)
        self.label4_3.setObjectName("label4_3")
        self.gridlayout5.addWidget(self.label4_3,3,0,1,1)

        self.btnColorSource = QtGui.QPushButton(self.frame2)
        self.btnColorSource.setObjectName("btnColorSource")
        self.gridlayout5.addWidget(self.btnColorSource,2,3,1,1)

        self.btnColorTarget = QtGui.QPushButton(self.frame2)
        self.btnColorTarget.setObjectName("btnColorTarget")
        self.gridlayout5.addWidget(self.btnColorTarget,3,3,1,1)

        self.btnColorComment = QtGui.QPushButton(self.frame2)
        self.btnColorComment.setObjectName("btnColorComment")
        self.gridlayout5.addWidget(self.btnColorComment,4,3,1,1)
        self.gridlayout4.addWidget(self.frame2,2,0,1,3)

        self.bntDefaultsFont = QtGui.QPushButton(self.interface)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bntDefaultsFont.sizePolicy().hasHeightForWidth())
        self.bntDefaultsFont.setSizePolicy(sizePolicy)
        self.bntDefaultsFont.setObjectName("bntDefaultsFont")
        self.gridlayout4.addWidget(self.bntDefaultsFont,3,1,1,1)

        self.bntDefaultsColor = QtGui.QPushButton(self.interface)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bntDefaultsColor.sizePolicy().hasHeightForWidth())
        self.bntDefaultsColor.setSizePolicy(sizePolicy)
        self.bntDefaultsColor.setObjectName("bntDefaultsColor")
        self.gridlayout4.addWidget(self.bntDefaultsColor,3,2,1,1)

        spacerItem1 = QtGui.QSpacerItem(20,51,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout4.addItem(spacerItem1,4,0,1,1)
        self.stackedWidget.addWidget(self.interface)
        self.gridlayout.addWidget(self.stackedWidget,0,1,1,1)

        self.listWidget = QtGui.QListWidget(frmPreference)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setResizeMode(QtGui.QListView.Adjust)
        self.listWidget.setObjectName("listWidget")
        self.gridlayout.addWidget(self.listWidget,0,0,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(5)
        self.hboxlayout.setObjectName("hboxlayout")

        spacerItem2 = QtGui.QSpacerItem(287,31,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem2)

        self.okButton = QtGui.QPushButton(frmPreference)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.okButton.sizePolicy().hasHeightForWidth())
        self.okButton.setSizePolicy(sizePolicy)
        self.okButton.setObjectName("okButton")
        self.hboxlayout.addWidget(self.okButton)

        self.cancelButton = QtGui.QPushButton(frmPreference)
        self.cancelButton.setObjectName("cancelButton")
        self.hboxlayout.addWidget(self.cancelButton)
        self.gridlayout.addLayout(self.hboxlayout,1,1,1,1)

        self.retranslateUi(frmPreference)
        self.stackedWidget.setCurrentIndex(0)
        self.cbxFullLanguage.setCurrentIndex(-1)
        QtCore.QObject.connect(self.cancelButton,QtCore.SIGNAL("clicked()"),frmPreference.reject)
        QtCore.QObject.connect(self.okButton,QtCore.SIGNAL("clicked()"),frmPreference.accept)
        QtCore.QMetaObject.connectSlotsByName(frmPreference)
        frmPreference.setTabOrder(self.okButton,self.cancelButton)

    def retranslateUi(self, frmPreference):
        frmPreference.setWindowTitle(QtGui.QApplication.translate("frmPreference", "Preference", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("frmPreference", "Plural equation:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("frmPreference", "Number of single/plural form:", None, QtGui.QApplication.UnicodeUTF8))
        self.label5.setText(QtGui.QApplication.translate("frmPreference", "Support team", None, QtGui.QApplication.UnicodeUTF8))
        self.label6.setText(QtGui.QApplication.translate("frmPreference", "Time zone", None, QtGui.QApplication.UnicodeUTF8))
        self.label1.setText(QtGui.QApplication.translate("frmPreference", "User name", None, QtGui.QApplication.UnicodeUTF8))
        self.label3.setText(QtGui.QApplication.translate("frmPreference", "Full language name", None, QtGui.QApplication.UnicodeUTF8))
        self.label2.setText(QtGui.QApplication.translate("frmPreference", "Email address", None, QtGui.QApplication.UnicodeUTF8))
        self.label4.setText(QtGui.QApplication.translate("frmPreference", "Language Code", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("frmPreference", "Setting personal information", None, QtGui.QApplication.UnicodeUTF8))
        self.chkHeaderAuto.setText(QtGui.QApplication.translate("frmPreference", "Automatically update header on save", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("frmPreference", "Setting font & color", None, QtGui.QApplication.UnicodeUTF8))
        self.label2_4.setText(QtGui.QApplication.translate("frmPreference", "Overview header", None, QtGui.QApplication.UnicodeUTF8))
        self.bntFontOverviewHeader.setText(QtGui.QApplication.translate("frmPreference", "Font", None, QtGui.QApplication.UnicodeUTF8))
        self.btnColorOverview.setText(QtGui.QApplication.translate("frmPreference", "Color", None, QtGui.QApplication.UnicodeUTF8))
        self.bntFontOverview.setText(QtGui.QApplication.translate("frmPreference", "Font", None, QtGui.QApplication.UnicodeUTF8))
        self.label2_5.setText(QtGui.QApplication.translate("frmPreference", "Overview", None, QtGui.QApplication.UnicodeUTF8))
        self.bntFontTarget.setText(QtGui.QApplication.translate("frmPreference", "Font", None, QtGui.QApplication.UnicodeUTF8))
        self.Source_2.setText(QtGui.QApplication.translate("frmPreference", "Source", None, QtGui.QApplication.UnicodeUTF8))
        self.bntFontSource.setText(QtGui.QApplication.translate("frmPreference", "Font", None, QtGui.QApplication.UnicodeUTF8))
        self.lblsupportteam_2.setText(QtGui.QApplication.translate("frmPreference", "Comment", None, QtGui.QApplication.UnicodeUTF8))
        self.bntFontComment.setText(QtGui.QApplication.translate("frmPreference", "Font", None, QtGui.QApplication.UnicodeUTF8))
        self.label4_3.setText(QtGui.QApplication.translate("frmPreference", "Target", None, QtGui.QApplication.UnicodeUTF8))
        self.btnColorSource.setText(QtGui.QApplication.translate("frmPreference", "Color", None, QtGui.QApplication.UnicodeUTF8))
        self.btnColorTarget.setText(QtGui.QApplication.translate("frmPreference", "Color", None, QtGui.QApplication.UnicodeUTF8))
        self.btnColorComment.setText(QtGui.QApplication.translate("frmPreference", "Color", None, QtGui.QApplication.UnicodeUTF8))
        self.bntDefaultsFont.setText(QtGui.QApplication.translate("frmPreference", "Defaults Font", None, QtGui.QApplication.UnicodeUTF8))
        self.bntDefaultsColor.setText(QtGui.QApplication.translate("frmPreference", "Defaults Color", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("frmPreference", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("frmPreference", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    frmPreference = QtGui.QDialog()
    ui = Ui_frmPreference()
    ui.setupUi(frmPreference)
    frmPreference.show()
    sys.exit(app.exec_())
