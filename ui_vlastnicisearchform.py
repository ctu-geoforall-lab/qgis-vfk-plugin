# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_vlastnicisearchform.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_VlastniciSearchForm(object):
    def setupUi(self, VlastniciSearchForm):
        VlastniciSearchForm.setObjectName("VlastniciSearchForm")
        VlastniciSearchForm.resize(238, 208)
        self.gridLayout = QtWidgets.QGridLayout(VlastniciSearchForm)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(VlastniciSearchForm)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.jmenoLineEdit = QtWidgets.QLineEdit(VlastniciSearchForm)
        self.jmenoLineEdit.setObjectName("jmenoLineEdit")
        self.gridLayout.addWidget(self.jmenoLineEdit, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(VlastniciSearchForm)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.ofoCheckBox = QtWidgets.QCheckBox(VlastniciSearchForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ofoCheckBox.sizePolicy().hasHeightForWidth())
        self.ofoCheckBox.setSizePolicy(sizePolicy)
        self.ofoCheckBox.setChecked(True)
        self.ofoCheckBox.setObjectName("ofoCheckBox")
        self.gridLayout.addWidget(self.ofoCheckBox, 1, 1, 1, 1)
        self.opoCheckBox = QtWidgets.QCheckBox(VlastniciSearchForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.opoCheckBox.sizePolicy().hasHeightForWidth())
        self.opoCheckBox.setSizePolicy(sizePolicy)
        self.opoCheckBox.setChecked(True)
        self.opoCheckBox.setObjectName("opoCheckBox")
        self.gridLayout.addWidget(self.opoCheckBox, 2, 1, 1, 1)
        self.sjmCheckBox = QtWidgets.QCheckBox(VlastniciSearchForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sjmCheckBox.sizePolicy().hasHeightForWidth())
        self.sjmCheckBox.setSizePolicy(sizePolicy)
        self.sjmCheckBox.setChecked(True)
        self.sjmCheckBox.setObjectName("sjmCheckBox")
        self.gridLayout.addWidget(self.sjmCheckBox, 3, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(VlastniciSearchForm)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.rcIcoLineEdit = QtWidgets.QLineEdit(VlastniciSearchForm)
        self.rcIcoLineEdit.setObjectName("rcIcoLineEdit")
        self.gridLayout.addWidget(self.rcIcoLineEdit, 4, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(VlastniciSearchForm)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)
        self.lvVlastniciLineEdit = QtWidgets.QLineEdit(VlastniciSearchForm)
        self.lvVlastniciLineEdit.setObjectName("lvVlastniciLineEdit")
        self.gridLayout.addWidget(self.lvVlastniciLineEdit, 5, 1, 1, 1)

        self.retranslateUi(VlastniciSearchForm)
        QtCore.QMetaObject.connectSlotsByName(VlastniciSearchForm)

    def retranslateUi(self, VlastniciSearchForm):
        _translate = QtCore.QCoreApplication.translate
        VlastniciSearchForm.setWindowTitle(_translate("VlastniciSearchForm", "Form"))
        self.label.setText(_translate("VlastniciSearchForm", "Jméno:"))
        self.label_4.setText(_translate("VlastniciSearchForm", "Typ osoby:"))
        self.ofoCheckBox.setText(_translate("VlastniciSearchForm", "OFO"))
        self.opoCheckBox.setText(_translate("VlastniciSearchForm", "OPO"))
        self.sjmCheckBox.setText(_translate("VlastniciSearchForm", "SJM"))
        self.label_2.setText(_translate("VlastniciSearchForm", "RČ/IČO:"))
        self.label_3.setText(_translate("VlastniciSearchForm", "LV:"))