# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_budovysearchform.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_BudovySearchForm(object):
    def setupUi(self, BudovySearchForm):
        BudovySearchForm.setObjectName("BudovySearchForm")
        BudovySearchForm.resize(248, 190)
        self.gridLayout_2 = QtWidgets.QGridLayout(BudovySearchForm)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(BudovySearchForm)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 3, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(BudovySearchForm)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(BudovySearchForm)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.cisloDomovniLineEdit = QtWidgets.QLineEdit(BudovySearchForm)
        self.cisloDomovniLineEdit.setObjectName("cisloDomovniLineEdit")
        self.gridLayout_2.addWidget(self.cisloDomovniLineEdit, 0, 1, 1, 1)
        self.naParceleLineEdit = QtWidgets.QLineEdit(BudovySearchForm)
        self.naParceleLineEdit.setObjectName("naParceleLineEdit")
        self.gridLayout_2.addWidget(self.naParceleLineEdit, 1, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(BudovySearchForm)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 4, 0, 1, 1)
        self.lvBudovyLineEdit = QtWidgets.QLineEdit(BudovySearchForm)
        self.lvBudovyLineEdit.setObjectName("lvBudovyLineEdit")
        self.gridLayout_2.addWidget(self.lvBudovyLineEdit, 3, 1, 1, 1)
        self.mZpVyuzitiCombo = QtWidgets.QComboBox(BudovySearchForm)
        self.mZpVyuzitiCombo.setObjectName("mZpVyuzitiCombo")
        self.gridLayout_2.addWidget(self.mZpVyuzitiCombo, 2, 1, 1, 1)

        self.retranslateUi(BudovySearchForm)
        QtCore.QMetaObject.connectSlotsByName(BudovySearchForm)

    def retranslateUi(self, BudovySearchForm):
        _translate = QtCore.QCoreApplication.translate
        BudovySearchForm.setWindowTitle(_translate("BudovySearchForm", "Form"))
        self.label.setText(_translate("BudovySearchForm", "LV:"))
        self.label_2.setText(_translate("BudovySearchForm", "Na parcele:"))
        self.label_3.setText(_translate("BudovySearchForm", "Č. domovní:"))
        self.label_4.setText(_translate("BudovySearchForm", "Zp. využití:"))
