# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_jednotkysearchform.ui'
#
# Created: Fri Nov 20 17:50:26 2015
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

class Ui_JednotkySearchForm(object):
    def setupUi(self, JednotkySearchForm):
        JednotkySearchForm.setObjectName(_fromUtf8("JednotkySearchForm"))
        JednotkySearchForm.resize(248, 181)
        self.gridLayout = QtGui.QGridLayout(JednotkySearchForm)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(JednotkySearchForm)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(JednotkySearchForm)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtGui.QLabel(JednotkySearchForm)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_4 = QtGui.QLabel(JednotkySearchForm)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_5 = QtGui.QLabel(JednotkySearchForm)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.mCisloJednotkyLineEdit = QtGui.QLineEdit(JednotkySearchForm)
        self.mCisloJednotkyLineEdit.setObjectName(_fromUtf8("mCisloJednotkyLineEdit"))
        self.gridLayout.addWidget(self.mCisloJednotkyLineEdit, 0, 1, 1, 1)
        self.mCisloDomovniLineEdit = QtGui.QLineEdit(JednotkySearchForm)
        self.mCisloDomovniLineEdit.setObjectName(_fromUtf8("mCisloDomovniLineEdit"))
        self.gridLayout.addWidget(self.mCisloDomovniLineEdit, 1, 1, 1, 1)
        self.mNaParceleLineEdit = QtGui.QLineEdit(JednotkySearchForm)
        self.mNaParceleLineEdit.setObjectName(_fromUtf8("mNaParceleLineEdit"))
        self.gridLayout.addWidget(self.mNaParceleLineEdit, 2, 1, 1, 1)
        self.mLvJednotkyLineEdit = QtGui.QLineEdit(JednotkySearchForm)
        self.mLvJednotkyLineEdit.setObjectName(_fromUtf8("mLvJednotkyLineEdit"))
        self.gridLayout.addWidget(self.mLvJednotkyLineEdit, 4, 1, 1, 1)
        self.mZpVyuzitiCombo = QtGui.QComboBox(JednotkySearchForm)
        self.mZpVyuzitiCombo.setObjectName(_fromUtf8("mZpVyuzitiCombo"))
        self.gridLayout.addWidget(self.mZpVyuzitiCombo, 3, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 1)

        self.retranslateUi(JednotkySearchForm)
        QtCore.QMetaObject.connectSlotsByName(JednotkySearchForm)

    def retranslateUi(self, JednotkySearchForm):
        JednotkySearchForm.setWindowTitle(_translate("JednotkySearchForm", "Form", None))
        self.label.setText(_translate("JednotkySearchForm", "Č. jednotky:", None))
        self.label_2.setText(_translate("JednotkySearchForm", "Č. domovní:", None))
        self.label_3.setText(_translate("JednotkySearchForm", "Na parcele:", None))
        self.label_4.setText(_translate("JednotkySearchForm", "Zp. využití:", None))
        self.label_5.setText(_translate("JednotkySearchForm", "LV:", None))

