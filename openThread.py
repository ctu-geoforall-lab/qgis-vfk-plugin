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

from qgis.PyQt.QtCore import QThread, pyqtSignal


class ImportVfkThread(QThread):
    working = pyqtSignal(str)
    nextLayer = True

    def __init__(self, vfk_files):
        """
        Class for using multi-thread import of layers
        :type vfk_files: list of VFK files to be imported
        """
        QThread.__init__(self)

        self.vfk_files = vfk_files

    def __del__(self):
        self.wait()

    def run(self):
        for vfkFile in self.vfk_files:
            self.working.emit(vfkFile)
            self.nextLayer = True

            while self.nextLayer:
                self.sleep(1)

class DownloadPosidentsThread(QThread):
    working = pyqtSignal(list)

    def __init__(self, listTelId):
        """
        Class for using multi-thread import of layers
        :type vfk_files: list of VFK files to be imported
        """
        QThread.__init__(self)

        self.listTelId = listTelId

    def __del__(self):
        self.wait()

    def run(self):
        self.working.emit(self.listTelId)
