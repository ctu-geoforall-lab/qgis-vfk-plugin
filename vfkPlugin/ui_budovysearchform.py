# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_budovysearchform.ui'
#
# Created: Fri Nov 20 17:50:07 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_BudovySearchForm(object):
    def setupUi(self, BudovySearchForm):
        BudovySearchForm.setObjectName(_fromUtf8("BudovySearchForm"))
        BudovySearchForm.resize(248, 190)
        self.gridLayout_2 = QtGui.QGridLayout(BudovySearchForm)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(BudovySearchForm)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 3, 0, 1, 1)
        self.label_2 = QtGui.QLabel(BudovySearchForm)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtGui.QLabel(BudovySearchForm)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.cisloDomovniLineEdit = QtGui.QLineEdit(BudovySearchForm)
        self.cisloDomovniLineEdit.setObjectName(_fromUtf8("cisloDomovniLineEdit"))
        self.gridLayout_2.addWidget(self.cisloDomovniLineEdit, 0, 1, 1, 1)
        self.naParceleLineEdit = QtGui.QLineEdit(BudovySearchForm)
        self.naParceleLineEdit.setObjectName(_fromUtf8("naParceleLineEdit"))
        self.gridLayout_2.addWidget(self.naParceleLineEdit, 1, 1, 1, 1)
        self.label_4 = QtGui.QLabel(BudovySearchForm)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 4, 0, 1, 1)
        self.lvBudovyLineEdit = QtGui.QLineEdit(BudovySearchForm)
        self.lvBudovyLineEdit.setObjectName(_fromUtf8("lvBudovyLineEdit"))
        self.gridLayout_2.addWidget(self.lvBudovyLineEdit, 3, 1, 1, 1)
        self.mZpVyuzitiCombo = QtGui.QComboBox(BudovySearchForm)
        self.mZpVyuzitiCombo.setObjectName(_fromUtf8("mZpVyuzitiCombo"))
        self.gridLayout_2.addWidget(self.mZpVyuzitiCombo, 2, 1, 1, 1)

        self.retranslateUi(BudovySearchForm)
        QtCore.QMetaObject.connectSlotsByName(BudovySearchForm)

    def retranslateUi(self, BudovySearchForm):
        BudovySearchForm.setWindowTitle(_translate("BudovySearchForm", "Form", None))
        self.label.setText(_translate("BudovySearchForm", "LV:", None))
        self.label_2.setText(_translate("BudovySearchForm", "Na parcele:", None))
        self.label_3.setText(_translate("BudovySearchForm", "Č. domovní:", None))
        self.label_4.setText(_translate("BudovySearchForm", "Zp. využití:", None))

