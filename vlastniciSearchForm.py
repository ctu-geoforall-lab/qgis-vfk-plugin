# -*- coding: utf-8 -*-

"""
/***************************************************************************
 vfkPluginDialog
                                 A QGIS plugin
 Plugin umoznujici praci s daty katastru nemovitosti
                             -------------------
        begin                : 2015-06-11
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Stepan Bambula
        email                : stepan.bambula@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from builtins import str

from qgis.PyQt import uic
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QWidget


class VlastniciSearchForm(QWidget):
    # signals
    searchEnabled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(VlastniciSearchForm, self).__init__(parent)
        ui_path = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(os.path.join(ui_path, "ui_vlastnicisearchform.ui"), self)

        # Set up the user interface from Designer.
        self.setupUi(self)

        self.ofoCheckBox.clicked.connect(self.__vlastniciSetRcIcoEnabled)
        self.opoCheckBox.clicked.connect(self.__vlastniciSetRcIcoEnabled)

        self.ofoCheckBox.clicked.connect(self.__vlastniciSearchEnabled)
        self.opoCheckBox.clicked.connect(self.__vlastniciSearchEnabled)
        self.sjmCheckBox.clicked.connect(self.__vlastniciSearchEnabled)

    def jmeno(self):
        return str(self.jmenoLineEdit.text().strip())

    def rcIco(self):
        return self.rcIcoLineEdit.text().strip()

    def isSjm(self):
        return self.sjmCheckBox.isChecked()

    def isOpo(self):
        return self.opoCheckBox.isChecked()

    def isOfo(self):
        return self.ofoCheckBox.isChecked()

    def lv(self):
        return self.lvVlastniciLineEdit.text().strip()

    def __vlastniciSearchEnabled(self):
        if self.ofoCheckBox.isChecked() or self.opoCheckBox.isChecked() or self.sjmCheckBox.isChecked():
            self.searchEnabled.emit(True)
        else:
            self.searchEnabled.emit(False)

    def __vlastniciSetRcIcoEnabled(self):
        if self.ofoCheckBox.isChecked() or self.opoCheckBox.isChecked():
            self.rcIcoLineEdit.setEnabled(True)
        else:
            self.rcIcoLineEdit.setEnabled(False)
