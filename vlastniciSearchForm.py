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

from PyQt4.QtGui import *
from PyQt4.QtCore import pyqtSignal, SIGNAL

from ui_vlastnicisearchform import *


class VlastniciSearchForm(QWidget):
    # signals
    searchEnabled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(VlastniciSearchForm, self).__init__(parent)

        # Set up the user interface from Designer.
        self.ui = Ui_VlastniciSearchForm()
        self.ui.setupUi(self)

        self.connect(self.ui.ofoCheckBox, SIGNAL(
            "clicked()"), self.__vlastniciSetRcIcoEnabled)
        self.connect(self.ui.opoCheckBox, SIGNAL(
            "clicked()"), self.__vlastniciSetRcIcoEnabled)

        self.connect(self.ui.ofoCheckBox, SIGNAL(
            "clicked()"), self.__vlastniciSearchEnabled)
        self.connect(self.ui.opoCheckBox, SIGNAL(
            "clicked()"), self.__vlastniciSearchEnabled)
        self.connect(self.ui.sjmCheckBox, SIGNAL(
            "clicked()"), self.__vlastniciSearchEnabled)

    def jmeno(self):
        return unicode(self.ui.jmenoLineEdit.text().strip())

    def rcIco(self):
        return self.ui.rcIcoLineEdit.text().strip()

    def isSjm(self):
        return self.ui.sjmCheckBox.isChecked()

    def isOpo(self):
        return self.ui.opoCheckBox.isChecked()

    def isOfo(self):
        return self.ui.ofoCheckBox.isChecked()

    def lv(self):
        return self.ui.lvVlastniciLineEdit.text().strip()

    def __vlastniciSearchEnabled(self):
        if self.ui.ofoCheckBox.isChecked() or self.ui.opoCheckBox.isChecked() or self.ui.sjmCheckBox.isChecked():
            self.emit(SIGNAL("searchEnabled"), True)
        else:
            self.emit(SIGNAL("searchEnabled"), False)

    def __vlastniciSetRcIcoEnabled(self):
        if self.ui.ofoCheckBox.isChecked() or self.ui.opoCheckBox.isChecked():
            self.ui.rcIcoLineEdit.setEnabled(True)
        else:
            self.ui.rcIcoLineEdit.setEnabled(False)
