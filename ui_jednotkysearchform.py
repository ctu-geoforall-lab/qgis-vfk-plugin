# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_jednotkysearchform.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_JednotkySearchForm(object):
    def setupUi(self, JednotkySearchForm):
        JednotkySearchForm.setObjectName("JednotkySearchForm")
        JednotkySearchForm.resize(248, 181)
        self.gridLayout = QtWidgets.QGridLayout(JednotkySearchForm)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(JednotkySearchForm)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(JednotkySearchForm)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(JednotkySearchForm)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(JednotkySearchForm)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(JednotkySearchForm)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.mCisloJednotkyLineEdit = QtWidgets.QLineEdit(JednotkySearchForm)
        self.mCisloJednotkyLineEdit.setObjectName("mCisloJednotkyLineEdit")
        self.gridLayout.addWidget(self.mCisloJednotkyLineEdit, 0, 1, 1, 1)
        self.mCisloDomovniLineEdit = QtWidgets.QLineEdit(JednotkySearchForm)
        self.mCisloDomovniLineEdit.setObjectName("mCisloDomovniLineEdit")
        self.gridLayout.addWidget(self.mCisloDomovniLineEdit, 1, 1, 1, 1)
        self.mNaParceleLineEdit = QtWidgets.QLineEdit(JednotkySearchForm)
        self.mNaParceleLineEdit.setObjectName("mNaParceleLineEdit")
        self.gridLayout.addWidget(self.mNaParceleLineEdit, 2, 1, 1, 1)
        self.mLvJednotkyLineEdit = QtWidgets.QLineEdit(JednotkySearchForm)
        self.mLvJednotkyLineEdit.setObjectName("mLvJednotkyLineEdit")
        self.gridLayout.addWidget(self.mLvJednotkyLineEdit, 4, 1, 1, 1)
        self.mZpVyuzitiCombo = QtWidgets.QComboBox(JednotkySearchForm)
        self.mZpVyuzitiCombo.setObjectName("mZpVyuzitiCombo")
        self.gridLayout.addWidget(self.mZpVyuzitiCombo, 3, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 1)

        self.retranslateUi(JednotkySearchForm)
        QtCore.QMetaObject.connectSlotsByName(JednotkySearchForm)

    def retranslateUi(self, JednotkySearchForm):
        _translate = QtCore.QCoreApplication.translate
        JednotkySearchForm.setWindowTitle(_translate("JednotkySearchForm", "Form"))
        self.label.setText(_translate("JednotkySearchForm", "Č. jednotky:"))
        self.label_2.setText(_translate("JednotkySearchForm", "Č. domovní:"))
        self.label_3.setText(_translate("JednotkySearchForm", "Na parcele:"))
        self.label_4.setText(_translate("JednotkySearchForm", "Zp. využití:"))
        self.label_5.setText(_translate("JednotkySearchForm", "LV:"))