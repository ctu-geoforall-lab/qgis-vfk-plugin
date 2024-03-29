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
# Import the PyQt, QGIS libraries and classes
import os
import time
import sys
from pathlib import Path
from collections import OrderedDict
from re import search

from qgis.PyQt.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QProgressDialog, QToolBar, QActionGroup, QDockWidget, QToolButton, QMenu, QHBoxLayout, QPushButton, QLineEdit
from qgis.PyQt.QtGui import QPalette, QDesktopServices
from qgis.PyQt.QtCore import QFileInfo, QDir, Qt, QObject, pyqtSignal, QThread, QSettings, QUuid, QSignalMapper
from qgis.PyQt.QtSql import QSqlDatabase
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

from osgeo import ogr, gdal

from .ui_MainApp import Ui_MainApp
from .searchFormController import *
from .openThread import ImportVfkThread, DownloadPosidentsThread
from .applyChanges import *

sys.path.insert(0, str(Path(__file__).parent)) # needed for pywsdp import

class VFKError(Exception):
    pass


class VFKWarning(Warning):
    pass


class MainApp(QDockWidget, QMainWindow, Ui_MainApp):
    # signals
    goBack = pyqtSignal()
    searchOpsubByName = pyqtSignal(str)
    enableSearch = pyqtSignal(bool)
    refreshLegend = pyqtSignal(QgsMapLayer)
    ogrDatasourceLoaded = pyqtSignal(bool)

    class VfkLayer(object):
        Par = 0
        Bud = 1

    def __init__(self, iface):
        QDockWidget.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface

        # variables
        self.__mLastVfkFile = []
        self.__mOgrDataSource = None
        self.__mDataSourceName = ''
        self.__inputFilePath = ['']
        self.__mLoadedLayers = {}
        self.__mDefaultPalette = self.vfkFileLineEdit.palette()

        # new lineEdits variables
        self.lineEditsCount = 1

        self.__browseButtons = OrderedDict()
        self.__vfkLineEdits = OrderedDict()

        # data will be load from source according to checked radiobox
        self.__source_for_data = 'file'

        # apply changes into main database
        self.__databases = {}
        # self.pb_applyChanges.setEnabled(False)
        self.changes_instance = ApplyChanges()

        # Connect ui with functions
        self.__createToolbarsAndConnect()

        # check GDAL version
        self.__gdal_version = int(gdal.VersionInfo())

        if self.__gdal_version < 2020000:
            self.actionZpracujZmeny.setEnabled(False)
            self.pb_nextFile.setEnabled(False)
            self.pb_nextFile.setToolTip(
                'Není možné načíst více souborů, verze GDAL je nižší než 2.2.0.')
            self.actionZpracujZmeny.setToolTip('Zpracování změn není povoleno, verze GDAL je nižší než 2.2.0.')
            self.groupBox.setEnabled(False)

        # settings
        self.loadVfkButton.setDisabled(True)

        self.searchFormMainControls = SearchFormController.MainControls()
        self.searchFormMainControls.formCombobox = self.searchCombo
        self.searchFormMainControls.searchForms = self.searchForms
        self.searchFormMainControls.searchButton = self.searchButton

        self.searchForms = SearchFormController.SearchForms()
        self.searchForms.vlastnici = self.vlastniciSearchForm
        self.searchForms.parcely = self.parcelySearchForm
        self.searchForms.budovy = self.budovySearchForm
        self.searchForms.jednotky = self.jednotkySearchForm

        # search form controller
        self.__mSearchController = SearchFormController(
            self.searchFormMainControls, self.searchForms, self)

        self.__mSearchController.actionTriggered.connect(self.vfkBrowser.processAction)
        self.enableSearch.connect(self.searchButton.setEnabled)

        self.vfkBrowser.showParcely.connect(self.showParInMap)
        self.vfkBrowser.showBudovy.connect(self.showBudInMap)

        # connect lineEdits and returnPressed action
        self.vfkFileLineEdit.returnPressed.connect(self.loadVfkButton_clicked)
        self.vlastniciSearchForm.ui.jmenoLineEdit.returnPressed.connect(self.__mSearchController.search)
        self.vlastniciSearchForm.ui.rcIcoLineEdit.returnPressed.connect(self.__mSearchController.search)
        self.vlastniciSearchForm.ui.lvVlastniciLineEdit.returnPressed.connect(self.__mSearchController.search)

        self.parcelySearchForm.ui.parCisloLineEdit.returnPressed.connect(self.__mSearchController.search)
        self.parcelySearchForm.ui.lvParcelyLineEdit.returnPressed.connect(self.__mSearchController.search)

        self.budovySearchForm.ui.cisloDomovniLineEdit.returnPressed.connect(self.__mSearchController.search)
        self.budovySearchForm.ui.naParceleLineEdit.returnPressed.connect(self.__mSearchController.search)
        self.budovySearchForm.ui.lvBudovyLineEdit.returnPressed.connect(self.__mSearchController.search)

        self.jednotkySearchForm.ui.mCisloJednotkyLineEdit.returnPressed.connect(self.__mSearchController.search)
        self.jednotkySearchForm.ui.mCisloDomovniLineEdit.returnPressed.connect(self.__mSearchController.search)
        self.jednotkySearchForm.ui.mNaParceleLineEdit.returnPressed.connect(self.__mSearchController.search)
        self.jednotkySearchForm.ui.mLvJednotkyLineEdit.returnPressed.connect(self.__mSearchController.search)

        self.vfkBrowser.showHelpPage()

        # settings
        self.settings = QSettings()

    def browseButton_clicked(self, browseButton_id=1):
        """
        :param browseButton_id: ID of clicked browse button.
        :return:
        """
        sender = '{}-lastUsedDir'.format(self.sender().objectName())
        lastUsedDir = self.settings.value(sender, '')

        if self.__source_for_data == 'file':
            ext = '*.vfk'
            if self.__gdal_version >= 2020000:
                ext += ' *.db'
            loaded_file, __ = QFileDialog.getOpenFileName(
                self, 'Načti soubor VFK', lastUsedDir,
                'Soubory podporované ovladačem VFK GDAL ({})'.format(ext)
            )

            if not loaded_file:
                return

            self.__inputFilePath[browseButton_id - 1] = loaded_file
            self.__vfkLineEdits['vfkLineEdit_'+str(browseButton_id)].setText(loaded_file)
            self.settings.setValue(sender, os.path.dirname(loaded_file))
        elif self.__source_for_data == 'directory':
            loaded_dir = QFileDialog.getExistingDirectory(
                self, "Vyberte adresář s daty VFK", lastUsedDir
            )
            if not loaded_dir:
                return

            self.__inputFilePath = [loaded_dir]
            self.vfkFileLineEdit.setText(self.__inputFilePath[0])
            self.settings.setValue(sender, loaded_dir)
        else:
            iface.messageBar().pushMessage(
                'ERROR', 'Invalid data source ({})'.format(self.__source_for_data), level=Qgis.Critical, duration=10
            )

        self.loadVfkButton.setEnabled(True)

    def browserGoBack(self):
        self.vfkBrowser.goBack()

    def browserGoForward(self):
        self.vfkBrowser.goForth()

    def selectParInMap(self):
        self.showInMap(self.vfkBrowser.currentParIds(), "PAR")

    def selectBudInMap(self):
        self.showInMap(self.vfkBrowser.currentBudIds(), "BUD")

    def latexExport(self):
        fileName, __ = QFileDialog.getSaveFileName(
            self, "Jméno exportovaného souboru", ".tex", "LaTeX (*.tex)")
        if fileName:
            export_succesfull = self.vfkBrowser.exportDocument(
                self.vfkBrowser.currentUrl(), fileName, self.vfkBrowser.ExportFormat.Latex)
            if export_succesfull:
                self.succesfullExport("LaTeX")

    def htmlExport(self):
        fileName, __ = QFileDialog.getSaveFileName(
            self, "Jméno exportovaného souboru", ".html", "HTML (*.html)")
        if fileName:
            export_succesfull = self.vfkBrowser.exportDocument(
                self.vfkBrowser.currentUrl(), fileName, self.vfkBrowser.ExportFormat.Html)
            if export_succesfull:
                self.succesfullExport("HTML")

    def downloadPosidents(self):
        if not self.wsdpUsername.text() or not self.wsdpPassword.text():
            iface.messageBar().pushMessage(
                "Stažení posidentů přerušeno", "Vyplňte přístupové údaje", level=Qgis.Critical, duration=10)
            return

        self.loadVfkLayersFromSelected()

        listTelId = []
        for layer in self.__mLoadedLayers:
            id = self.__mLoadedLayers[layer]
            vectorLayer = QgsProject.instance().mapLayer(id)
            features = vectorLayer.selectedFeatures()
            for f in features:
                listTelId.append(f["TEL_ID"])

        if not self.__mLoadedLayers or not listTelId:
            iface.messageBar().pushMessage(
                "Stažení posidentů přerušeno", "Není vybrána žádná parcela ani budova", level=Qgis.Warning, duration=10)
            return

        self.wsdpStatus.setText(
            "Stahuji posidenty pro vybrané parcely a budovy (počet: {})...".format(len(features)))
        
        self.downloadPosidentsThread = DownloadPosidentsThread(listTelId)
        self.downloadPosidentsThread.working.connect(self.runDownloadingPosidents)
        if not self.downloadPosidentsThread.isRunning():
            self.downloadPosidentsThread.start()

    def runDownloadingPosidents(self, listTelId):
        from pywsdp.modules import CtiOS
        from pywsdp.base.exceptions import WSDPError, WSDPRequestError

        ctios = CtiOS([
            self.wsdpUsername.text(),
            self.wsdpPassword.text(),
        ], trial=self.wsdpTrial.isChecked())
        self.wsdpProgressBar.setValue(0)

        #ids = ctiosInterface.set_ids_from_db(db_path, "SELECT vla.opsub_id from vla,par where par.ID in ("+listParID+") and vla.TEL_ID=par.TEL_ID")
        try:
            sql = "SELECT * FROM opsub WHERE ID IN (SELECT opsub_id FROM vla WHERE tel_id IN ({}))".format(','.join(map(str, listTelId)))
            parameters_ctiOS_db = ctios.nacti_identifikatory_z_db(
                gdal.GetConfigOption('OGR_VFK_DB_NAME'),
                sql
            )
        except WSDPError as e:
            QgsMessageLog.logMessage("DB:{} SQL: {}".format(gdal.GetConfigOption('OGR_VFK_DB_NAME'), sql),
                                     level=Qgis.Info)                           
            iface.messageBar().pushMessage(
                'ERROR',
                'Vstupní VFK data neobsahující pro vybrané prvky informace o posidentech. {}'.format(e),
                level=Qgis.Critical, duration=10)
            self.wsdpStatus.setText('Nelze získat posidenty')
            return

        try:
            response, response_errors = ctios.posli_pozadavek(parameters_ctiOS_db)
            self.wsdpStatus.setText(
                "Počet úspěšně zpracovaných posidentů: {}/{} {}".format(
                    len(response.keys()) - len(response_errors.keys()),
                    len(response.keys()),
                    '(více v zprávách výpisů)' if response_errors else ''))
            self.wsdpProgressBar.setValue(100)
            # QgsMessageLog.logMessage("Stažené informace o posidentech: {}".format(response), level=Qgis.Info)
            if response_errors:
                QgsMessageLog.logMessage("Chybné informace o posidentech: {}".format(response), level=Qgis.Warning)
        except WSDPRequestError as e:
            iface.messageBar().pushMessage(
                'ERROR',
                'Nelze odeslat WSDP požadavek. {}'.format(e),
                level=Qgis.Critical, duration=10)
            self.wsdpStatus.setText('Nelze získat posidenty')
            return

        try:
            ctios.uloz_vystup_aktualizuj_db(
                response
            )
        except WSDPError as e:
            iface.messageBar().pushMessage(
                'ERROR',
                'Nepodařilo se aktualizovat interní DB. {}'.format(e),
                level=Qgis.Critical, duration=10)
            self.wsdpStatus.setText('Nelze získat posidenty')

    def setWSDPTrial(self):
        if self.wsdpTrial.isChecked():
            username = "WSTEST"
            password = "WSHESLO"
        else:
            username = password = ""
            
        self.wsdpUsername.setText(username)
        self.wsdpPassword.setText(password)
        
    def setSelectionChangedConnected(self, connected):
        """

        :type connected: bool
        :return:
        """
        for layer in self.__mLoadedLayers:
            id = self.__mLoadedLayers[layer]
            vectorLayer = QgsProject.instance().mapLayer(id)

            if connected:
                vectorLayer.selectionChanged.connect(self.showInfoAboutSelection)
            else:
                vectorLayer.selectionChanged.disconnect(self.showInfoAboutSelection)

    def showInMap(self, ids, layerName):
        """

        :type ids: list
        :type layerName: str
        :return:
        """
        if layerName in self.__mLoadedLayers:
            id = self.__mLoadedLayers[layerName]
            vectorLayer = QgsProject.instance().mapLayer(id)
            searchString = "ID IN ({})".format(", ".join(ids))
            error = ''
            fIds = self.__search(vectorLayer, searchString, error)
            if error:
                iface.messageBar().pushMessage(
                    'ERROR', 'In showInMap: {}'.format(error), level=Qgis.Critical, duration=10
                )
                return
            else:
                vectorLayer.selectByIds(fIds)

    def __search(self, layer, searchString, error):
        """
        Search features by expression.

        :type layer: QgsVectorLayer
        :type searchString: str
        :type error: str
        :return: list of ids
        """
        # parse search string and build parsed tree
        search = QgsExpression(searchString)
        fIds = []

        searchContext = QgsExpressionContext()
        searchContext.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))

        if search.hasParserError():
            error += "Parsing error:" + search.parserErrorString()
            return fIds
        if not search.prepare(searchContext):
            error += "Evaluation error:" + search.evalErrorString()

        fit = QgsFeatureIterator(layer.getFeatures())
        f = QgsFeature()

        while fit.nextFeature(f):
            searchContext.setFeature(f)
            if search.evaluate(searchContext):
                fIds.append(f.id())
            # check if there were errors during evaluating
            if search.hasEvalError():
                iface.messageBar().pushMessage(
                    'ERROR', 'Evaluate error: {}'.format(error), level=Qgis.Critical, duration=10
                )
                break

        return fIds

    def loadVfkButton_clicked(self):
        """
        After click method starts loading all inserted files
        """
        # check the source of data
        if self.__source_for_data == 'directory':
            self.__inputFilePath = self.__findVFKFilesInDirectory(self.__inputFilePath[0])
            
        # check if first file is amendment
        amendment_file = self.__checkIfAmendmentFile(self.__inputFilePath[0])

        # prepare name for database
        # 1. single vfk file -> filename_stav.db
        # 2. multiple vfk files
        # 2a. all in one directory -> filename1_filename2_..._stav.db
        # 2b. different directories filename1.parent/filename1_filename2_..._stav.db
        # 3. one of input file is DB -> db_name
        db_name = []
        num_input_db = 0
        dir_path = None
        dir_path_defined = False
        for fn in self.__inputFilePath:
            # define dir_path
            if dir_path is None:
                dir_path = Path(fn).parent
            elif dir_path_defined is False and dir_path != Path(fn).parent:
                dir_path = Path(dir_path).parent
                dir_path_defined = True
            # define db_name
            if Path(fn).suffix == '.db':
                db_name = [Path(fn).name]
                num_input_db += 1
            if num_input_db > 1:
                iface.messageBar().pushMessage(
                    'ERROR', 'Only one input SQLite database can be defined', level=Qgis.Critical, duration=10
                )
                return
            if num_input_db < 1:
                fn_name = Path(fn).stem
                if fn_name not in db_name:
                    db_name.append(fn_name)

        db_name = '_'.join(db_name)
        if num_input_db < 1:
            if amendment_file:
                db_name += '_zmeny.db'
            else:
                db_name += '_stav.db'

        db_path = str(dir_path / db_name)
        gdal.SetConfigOption(
            'OGR_VFK_DB_NAME', db_path
        )
        self.__mDataSourceName = db_path

        QgsApplication.processEvents()

        self.importThread = ImportVfkThread(self.__inputFilePath)
        self.importThread.working.connect(self.runLoadingLayer)
        if not self.importThread.isRunning():
            self.importThread.start()

    def runLoadingLayer(self, fileName):
        """

        :return:
        """
        if fileName not in self.__mLastVfkFile:

            self.labelLoading.setText(
                'Načítám data do SQLite databáze (může nějaký čas trvat...)')

            try:
                self.loadVfkFile(fileName)
            except VFKError as e:
                QMessageBox.critical(
                    self, 'Chyba', '{}'.format(e), QMessageBox.Ok)
                self.enableSearch.emit(False)
                return

            self.__mLastVfkFile.append(fileName)
            self.importThread.nextLayer = False

            if fileName == self.__inputFilePath[-1]:
                self.loadingLayersFinished()

    def loadingLayersFinished(self):
        """

        :return:
        """
        try:
            self.__openDatabase(
                gdal.GetConfigOption('OGR_VFK_DB_NAME')
            )
        except VFKError as e:
            QMessageBox.critical(
                self, 'Chyba', '{}'.format(e), QMessageBox.Ok)
            self.enableSearch.emit(False)
            return

        self.vfkBrowser.setConnectionName(self.property("connectionName"))
        self.__mSearchController.setConnectionName(
            self.property("connectionName"))

        self.enableSearch.emit(True)
        self.__mLoadedLayers.clear()

        layerActive = None
        if self.parCheckBox.isChecked():
            layerActive = self.__loadVfkLayer('PAR')
        else:
            self.__unLoadVfkLayer('PAR')

        if self.budCheckBox.isChecked():
            layer = self.__loadVfkLayer('BUD')
            if layerActive is None:
                layerActive = layer
        else:
            self.__unLoadVfkLayer('BUD')

        if layerActive:
            iface.setActiveLayer(layerActive)

        self.labelLoading.setText(
            'Načítání souborů VFK do interní SQLite databáze bylo dokončeno.\n{}'.format(
            gdal.GetConfigOption('OGR_VFK_DB_NAME')))

    def vfkFileLineEdit_textChanged(self, arg1):
        """

        :type arg1: str
        :return:
        """
        info = QFileInfo(arg1)

        if info.isFile():
            self.loadVfkButton.setEnabled(True)
            self.vfkFileLineEdit.setPalette(self.__mDefaultPalette)
        else:
            self.loadVfkButton.setEnabled(False)
            pal = QPalette(self.vfkFileLineEdit.palette())
            pal.setColor(QPalette.text(), Qt.red)
            self.vfkFileLineEdit.setPalette(pal)

    def __loadVfkLayer(self, vfkLayerName):
        """

        :type vfkLayerName: str
        :return: QgsMapLayer
        """
        # QgsMessageLog.logMessage("VFK) Loading vfk layer {}".format(vfkLayerName))
        if vfkLayerName in self.__mLoadedLayers:
            # QgsMessageLog.logMessage(
            #     "(VFK) Vfk layer {} is already loaded".format(vfkLayerName)
            # )
            return QgsProject.instance().mapLayer(self.__mLoadedLayers[vfkLayerName])

        composedURI = self.__mDataSourceName + "|layername=" + vfkLayerName
        layer = QgsVectorLayer(composedURI, vfkLayerName, "ogr")
        if not layer.isValid():
            iface.messageBar().pushMessage(
                'ERROR', "Layer failed to load!", level=Qgis.Critical, duration=10
            )

        self.__mLoadedLayers[vfkLayerName] = layer.id()

        try:
            self.__setSymbology(layer)
        except VFKWarning as e:
            QMessageBox.information(self, 'Load Style', e, QMessageBox.Ok)

        QgsProject.instance().addMapLayer(layer, False)
        root = QgsProject.instance().layerTreeRoot()
        group_name = Path(layer.source().split('|')[0]).stem
        group = root.findGroup(group_name)
        if group is None:
            group = root.addGroup(group_name)
        group.addLayer(layer)

        return layer

    def loadVfkLayersFromSelected(self):
        dsn = None
        for layer in iface.layerTreeView().selectedLayers():
            if layer.storageType() != "SQLite":
                continue
            layer_name = layer.source().split('|')[1].lstrip('layername=')
            if layer_name not in ('BUD', 'PAR'):
                continue
            if dsn is not None and dsn != layer.source().split('|')[0]:
                iface.messageBar().pushMessage(
                    "Lze dotazovat pouze jeden datový zdroj",
                    "Ignoruji {} z důvodu jiného datového zdroje".format(layer.name()),
                    level=Qgis.Info, duration=10)
                continue

            dsn = layer.source().split('|')[0]
            if self.__mDataSourceName is not None and self.__mDataSourceName != dsn:                
                self.__mLoadedLayers[layer_name] = layer.id()

        if dsn is not None and self.__mDataSourceName == dsn:
            # no change, skip re-loading data source
            return
        else:
            self.__mDataSourceName = dsn
        
        if self.__mDataSourceName is None:
                iface.messageBar().pushMessage(
                    "Chyba",
                    "Nelze se dotazovat. Aktuálně vybraná vrstva není validní zdroj VFK.",
                    level=Qgis.Critical, duration=10)
                return

        if self.__mOgrDataSource:
            self.__mOgrDataSource.Destroy()
            self.__mOgrDataSource = None
        gdal.SetConfigOption('OGR_VFK_DB_NAME', self.__mDataSourceName)
        self.__mOgrDataSource = ogr.Open(self.__mDataSourceName, 0)

        self.__openDatabase(self.__mDataSourceName)
        self.vfkBrowser.setConnectionName(self.property("connectionName"))
        self.__mSearchController.setConnectionName(
            self.property("connectionName"))
        
    def __unLoadVfkLayer(self, vfkLayerName):
        """

        :type vfkLayerName: str
        :return:
        """
        # QgsMessageLog.logMessage("(VFK) Unloading vfk layer {}".format(vfkLayerName))

        if vfkLayerName not in self.__mLoadedLayers:
            # QgsMessageLog.logMessage(
            #     "(VFK) Vfk layer {} is already unloaded".format(vfkLayerName)
            # )
            return

        QgsProject.instance().removeMapLayer(
            self.__mLoadedLayers[vfkLayerName])
        del self.__mLoadedLayers[vfkLayerName]

    def __setSymbology(self, layer):
        """

        :type layer: QgsVectorLayer
        :return:
        """
        name = layer.name()
        symbologyFile = ''

        if name == 'PAR':
            symbologyFile = ':/parStyle.qml'
        elif name == 'BUD':
            symbologyFile = ':/budStyle.qml'

        errorMsg, resultFlag = layer.loadNamedStyle(symbologyFile)

        # layer.startEditing()
        # layer.addAttribute(QgsField("ListVlastnictvi",QVariant.Int))
        # layer.commitChanges()
        
        if not resultFlag:
            raise VFKWarning('Load style: {}'.format(errorMsg))

        layer.triggerRepaint()
        self.refreshLegend.emit(layer)

    def __openDatabase(self, dbPath):
        """

        :type dbPath: str
        :return:
        """
        # QgsMessageLog.logMessage("(VFK) Open DB: {}".format(dbPath))
        if not QSqlDatabase.isDriverAvailable('QSQLITE'):
            raise VFKError('Databázový ovladač QSQLITE není dostupný.')

        connectionName = QUuid.createUuid().toString()
        db = QSqlDatabase.addDatabase("QSQLITE", connectionName)
        db.setDatabaseName(dbPath)
        if not db.open():
            raise VFKError('Nepodařilo se otevřít databázi. ')

        self.setProperty("connectionName", connectionName)

    def loadVfkFile(self, fileName):
        """

        :type fileName: str
        :return:
        """
        label_text = '...' + Path(fileName).parent.name + '/' + Path(fileName).name

        # overwrite database
        if fileName == self.__inputFilePath[0]:
            if self.overwriteCheckBox.isChecked():
                # QgsMessageLog.logMessage('(VFK) Database will be overwritten')
                gdal.SetConfigOption('OGR_VFK_DB_OVERWRITE', 'YES')

        if self.__mOgrDataSource:
            self.__mOgrDataSource.Destroy()
            self.__mOgrDataSource = None

        QgsApplication.registerOgrDrivers()

        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(0)

        QgsApplication.processEvents()

        self.labelLoading.setText(
            'Načítám soubor {} (může nějaký čas trvat...)'.format(label_text))

        QgsApplication.processEvents()

        self.__mOgrDataSource = ogr.Open(
            fileName, 0)   # 0 - datasource is open in read-only mode

        if not self.__mOgrDataSource:
            raise VFKError(
                "Nelze otevřít VFK soubor '{}' jako platný OGR datasource.".format(fileName))

        layerCount = self.__mOgrDataSource.GetLayerCount()

        layers_names = []

        for i in range(layerCount):
            layers_names.append(
                self.__mOgrDataSource.GetLayer(i).GetLayerDefn().GetName())

        if ('PAR' not in layers_names or 'BUD' not in layers_names) and len(self.__vfkLineEdits) == 1:
            self.__dataWithoutParBud()
            self.labelLoading.setText(
                'Data nemohla být načtena. Vstupní soubor neobsahuje bloky PAR a BUD.')
            QgsApplication.processEvents()
            return

        # load all layers
        self.progressBar.setRange(0, layerCount - 1)
        for i in range(layerCount):
            self.progressBar.setValue(i)
            theLayerName = self.__mOgrDataSource.GetLayer(
                i).GetLayerDefn().GetName()
            self.labelLoading.setText(
                u"VFK data {}/{}: {}".format(i + 1, layerCount, theLayerName))
            QgsApplication.processEvents()
            self.__mOgrDataSource.GetLayer(i).GetFeatureCount(True)
            time.sleep(0.02)

        self.labelLoading.setText(
            'Soubor {} úspěšně načten.'.format(label_text))

        gdal.SetConfigOption('OGR_VFK_DB_OVERWRITE', 'NO')
        self.__mOgrDataSource.Destroy()
        self.__mOgrDataSource = None

    def __selectedIds(self, layer):
        """

        :type layer: QgsVectorLayer
        :return:
        """
        ids = []
        flist = layer.selectedFeatures()

        for it in flist:
            f = QgsFeature(it)
            ids.append(str(f.attribute("ID")))
        return ids

    def showInfoAboutSelection(self):
        layers = ["PAR", "BUD"]
        layerIds = {}
        for layer in layers:
            if layer in self.__mLoadedLayers:
                id = str(self.__mLoadedLayers[layer])
                vectorLayer = QgsProject.instance().mapLayer(id)
                layerIds[layer] = self.__selectedIds(vectorLayer)

        self.vfkBrowser.showInfoAboutSelection(
            layerIds["PAR"], layerIds["BUD"])

    def showParInMap(self, ids):
        """

        :type ids: list
        :return:
        """
        if self.actionShowInfoaboutSelection.isChecked():
            self.setSelectionChangedConnected(False)
            self.showInMap(ids, "PAR")
            self.setSelectionChangedConnected(True)
        else:
            self.showInMap(ids, "PAR")

    def showBudInMap(self, ids):
        """

        :type ids: list
        :return:
        """
        if self.actionShowInfoaboutSelection.isChecked():
            self.setSelectionChangedConnected(False)
            self.showInMap(ids, "BUD")
            self.setSelectionChangedConnected(True)
        else:
            self.showInMap(ids, "BUD")

    def showOnCuzk(self):
        x = self.vfkBrowser.currentDefinitionPoint().first.split(".")[0]
        y = self.vfkBrowser.currentDefinitionPoint().second.split(".")[0]

        url = "http://nahlizenidokn.cuzk.cz/MapaIdentifikace.aspx?&x=-{}&y=-{}".format(
            y, x)
        QDesktopServices.openUrl(QUrl(url, QUrl.TolerantMode))

    def switchToImport(self):
        self.actionImport.trigger()

    def switchToSearch(self, searchType):
        """
        :type searchType: int
        """
        self.actionVyhledavani.trigger()
        self.searchCombo.setCurrentIndex(searchType)
        self.searchFormMainControls.searchForms.setCurrentIndex(searchType)

    def switchToChanges(self):
        self.actionZpracujZmeny.trigger()

    def switchToDownloadPosidents(self):
        self.actionDownloadPosidents.trigger()
        
    def succesfullExport(self, export_format):
        """

        :type export_format: str
        :return:
        """
        QMessageBox.information(
            self, 'Export', u"Export do formátu {} proběhl úspěšně.".format(
                export_format),
                                QMessageBox.Ok)

    def __dataWithoutParBud(self):
        """

        :type export_format: str
        :return:
        """
        QMessageBox.warning(self, 'Upozornění', u"Zvolený VFK soubor neobsahuje vrstvy s geometrií (PAR, BUD), proto nemohou "
                            u"být pomocí VFK Pluginu načtena. Data je možné načíst v QGIS pomocí volby "
                            u"'Načíst vektorovou vrstvu.'", QMessageBox.Ok)

    def __addRowToGridLayout(self):
        numLineEdits = len(self.__vfkLineEdits)
        if numLineEdits >= 5:
            iface.messageBar().pushMessage(
                'Upozornění', "Byl dosažen maximální počet ({}) VFK souborů pro zpracování. "
                "Načítání dalších souborů není povoleno!".format(numLineEdits),
                level=Qgis.Warning, duration=10)
            return

        # update label
        self.label.setText('VFK soubory:')

        # new layout
        horizontalLayout = QHBoxLayout()

        # create new objects
        row = str(numLineEdits + 1)
        self.__browseButtons['browseButton_' + row] = QPushButton("Procházet")
        self.__vfkLineEdits['vfkLineEdit_' + row] = QLineEdit()

        horizontalLayout.addWidget(self.__vfkLineEdits['vfkLineEdit_' + row])
        horizontalLayout.addWidget(self.__browseButtons['browseButton_' + row])

        # number of lines in gridLayout
        rows_count = self.gridLayout_12.rowCount()  # count of rows in gridLayout

        # export objects from gridLayout
        item_label = self.gridLayout_12.itemAtPosition(rows_count - 3, 0)
        item_par = self.gridLayout_12.itemAtPosition(rows_count - 3, 1)
        item_bud = self.gridLayout_12.itemAtPosition(rows_count - 2, 1)
        item_settings = self.gridLayout_12.itemAtPosition(rows_count - 1, 0)
        item_rewrite_db = self.gridLayout_12.itemAtPosition(rows_count - 1, 1)

        # remove objects from gridLayout
        self.gridLayout_12.removeItem(
            self.gridLayout_12.itemAtPosition(rows_count - 3, 0))
        self.gridLayout_12.removeItem(
            self.gridLayout_12.itemAtPosition(rows_count - 3, 1))
        self.gridLayout_12.removeItem(
            self.gridLayout_12.itemAtPosition(rows_count - 2, 1))
        self.gridLayout_12.removeItem(
            self.gridLayout_12.itemAtPosition(rows_count - 1, 0))
        self.gridLayout_12.removeItem(
            self.gridLayout_12.itemAtPosition(rows_count - 1, 1))

        # re-build gridLayout
        self.gridLayout_12.addLayout(horizontalLayout, rows_count - 3, 1)
        self.gridLayout_12.addItem(item_label, rows_count - 2, 0)
        self.gridLayout_12.addItem(item_par, rows_count - 2, 1)
        self.gridLayout_12.addItem(item_bud, rows_count - 1, 1)
        self.gridLayout_12.addItem(item_settings, rows_count, 0)
        self.gridLayout_12.addItem(item_rewrite_db, rows_count, 1)

        self.__browseButtons['browseButton_' + row].clicked.connect(
            lambda: self.browseButton_clicked(int(row)))

        # add empty filePath
        self.__inputFilePath.append('')
                
    def browseDb_clicked(self, database_type):
        """
        Method run dialog for select database in widget with changes.
        According to pushButton name will fill in relevant lineEdit.
        :type database_type: str
        """
        title = 'Vyber databázi'
        settings = QSettings()
        lastUsedDir = str(settings.value('/UI/' + "lastVectorFileFilter" + "Dir", "."))

        if database_type == 'mainDb':
            self.__databases[database_type] = QFileDialog.getOpenFileName(self, title, lastUsedDir, 'Datábaze (*.db)')
            if not self.__databases[database_type]:
                return
            self.le_mainDb.setText(str(self.__databases[database_type]))

        elif database_type == 'amendmentDb':
            self.__databases[database_type] = QFileDialog.getOpenFileName(self, title, lastUsedDir, 'Datábaze (*.db)')
            if not self.__databases[database_type]:
                return
            self.le_amendmentDb.setText(str(self.__databases[database_type]))

        elif database_type == 'exportDb':
            title = 'Zadej jméno výstupní databáze'
            self.__databases[database_type] = QFileDialog.getSaveFileName(self, u"Jméno výstupní databáze",
                                                                          ".db", u"Databáze (*.db)")
            if not self.__databases[database_type]:
                return
            self.le_exportDb.setText(str(self.__databases[database_type]))

        if len(self.__databases) == 3:
            self.pb_applyChanges.setEnabled(True)

    def applyChanges(self):
        """
        Method
        :return:
        """
        self.changes_instance.run(self.__databases['mainDb'],
                                  self.__databases['amendmentDb'],
                                  self.__databases['exportDb'])

    def __updateProgressBarChanges(self, iteration, table_name):
        """
        :type iteration: int
        :type table_name: str
        """
        self.progressBar_changes.setValue(iteration)
        self.l_status.setText('Aplikuji změny na tabulku {}...'.format(table_name))
        QgsApplication.processEvents()

    def __setRangeProgressBarChanges(self, max_range):
        """
        :type max_range: int
        """
        self.progressBar_changes.setRange(0, max_range)
        self.progressBar_changes.setValue(0)

    def __changesApplied(self):
        """
        """
        time.sleep(1)
        self.l_status.setText('Změny byly úspěšně aplikovány.')
        QgsApplication.processEvents()

    def __changesPreprocessingDatabase(self):
        """
        """
        self.l_status.setText('Připravuji výstupní databázi...')
        QgsApplication.processEvents()

    def __checkIfAmendmentFile(self, file_name):
        """

        :param file_name: Name of the input file
        :type file_name: str
        :return: bool
        """
        if file_name.endswith(".vfk"):
            with open(file_name, 'rb') as f:
                for line in f:

                    line_splited = str(line).split(';')

                    if line_splited[0] == '&HZMENY':
                        if line_splited[1] == '1':
                            return True
                        else:
                            return False
        else:
            # TODO: dopsat kontrolu, zda se jedna o stavovou, nebo zmenovou databazi
            pass

    def radioButtonValue(self):
        """
        Check which radio button is checked
        """
        self.vfkFileLineEdit.setText('')
        self.__inputFilePath = ['']
        self.loadVfkButton.setEnabled(False)

        if self.rb_file.isChecked():
            self.__source_for_data = 'file'
            self.pb_nextFile.show()
            self.label.setText('VFK soubor:')
        elif self.rb_directory.isChecked():
            self.__source_for_data = 'directory'
            self.pb_nextFile.hide()
            self.label.setText('Adresář:')

            # delete
            if len(self.__browseButtons) > 1:
                for i, button in enumerate(self.__browseButtons):
                    if i > 0:
                        self.__browseButtons[button].hide()
                self.__browseButtons = OrderedDict([self.__browseButtons.popitem(last=False)])
                
            if len(self.__vfkLineEdits) > 1:
                for i, le in enumerate(self.__vfkLineEdits):
                    if i > 0:
                        self.__vfkLineEdits[le].hide()
                self.__vfkLineEdits = OrderedDict([self.__vfkLineEdits.popitem(last=False)])
                

    def __findVFKFilesInDirectory(self, dir_path):
        """
        Finds all files with extension '.vfk' in given directory including subdirectories
        :param dir_path: Path to directory.
        :type dir_path: str
        :return: List of VFK files
        """
        file_paths = []
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".vfk"):
                    file_paths.append(os.path.join(root, file))

        return file_paths


    def __createToolbarsAndConnect(self):

        actionGroup = QActionGroup(self)
        actionGroup.addAction(self.actionImport)
        actionGroup.addAction(self.actionDownloadPosidents)        
        actionGroup.addAction(self.actionVyhledavani)
        actionGroup.addAction(self.actionZpracujZmeny)

        # QSignalMapper
        self.signalMapper = QSignalMapper(self)

        self.actionImport.triggered.connect(self.signalMapper.map)
        self.actionDownloadPosidents.triggered.connect(self.signalMapper.map)        
        self.actionVyhledavani.triggered.connect(self.signalMapper.map)
        self.actionZpracujZmeny.triggered.connect(self.signalMapper.map)

        # setMapping on each button to the QStackedWidget index we'd like to
        # switch to
        self.signalMapper.setMapping(self.actionImport, 0)
        self.signalMapper.setMapping(self.actionZpracujZmeny, 1)
        self.signalMapper.setMapping(self.actionVyhledavani, 2)
        self.signalMapper.setMapping(self.actionDownloadPosidents, 3)
        
        # connect mapper to stackedWidget
        self.signalMapper.mapped.connect(self.stackedWidget.setCurrentIndex)
        

        self.vfkBrowser.switchToPanelImport.connect(self.switchToImport)
        self.vfkBrowser.switchToPanelSearch.connect(self.switchToSearch)
        self.vfkBrowser.switchToPanelChanges.connect(self.switchToChanges)
        self.vfkBrowser.switchToPanelChanges.connect(self.switchToDownloadPosidents)

        # Browser toolbar
        # ---------------
        self.__mBrowserToolbar = QToolBar(self)
        self.actionBack.triggered.connect(self.vfkBrowser.goBack)
        self.actionForward.triggered.connect(self.vfkBrowser.goForth)

        self.actionSelectBudInMap.triggered.connect(self.selectBudInMap)
        self.actionSelectParInMap.triggered.connect(self.selectParInMap)
        self.actionCuzkPage.triggered.connect(self.showOnCuzk)

        self.actionExportLatex.triggered.connect(self.latexExport)
        self.actionExportHtml.triggered.connect(self.htmlExport)

        self.actionShowInfoaboutSelection.toggled.connect(self.setSelectionChangedConnected)
        self.actionShowHelpPage.triggered.connect(self.vfkBrowser.showHelpPage)

        self.loadVfkButton.clicked.connect(self.loadVfkButton_clicked)

        self.__browseButtons['browseButton_1'] = self.browseButton
        self.__browseButtons['browseButton_1'].clicked.connect(
            lambda: self.browseButton_clicked(1))

        self.__vfkLineEdits['vfkLineEdit_1'] = self.vfkFileLineEdit

        bt = QToolButton(self.__mBrowserToolbar)
        bt.setPopupMode(QToolButton.InstantPopup)
        bt.setText("Export ")

        menu = QMenu(bt)
        menu.addAction(self.actionExportLatex)
        menu.addAction(self.actionExportHtml)
        bt.setMenu(menu)

        # add actions to toolbar icons
        self.__mBrowserToolbar.addAction(self.actionImport)
        self.__mBrowserToolbar.addAction(self.actionDownloadPosidents)       
        self.__mBrowserToolbar.addAction(self.actionVyhledavani)
        self.__mBrowserToolbar.addAction(self.actionZpracujZmeny)
        self.__mBrowserToolbar.addSeparator()
        self.__mBrowserToolbar.addAction(self.actionBack)
        self.__mBrowserToolbar.addAction(self.actionForward)
        self.__mBrowserToolbar.addAction(self.actionSelectParInMap)
        self.__mBrowserToolbar.addAction(self.actionSelectBudInMap)
        self.__mBrowserToolbar.addAction(self.actionCuzkPage)
        self.__mBrowserToolbar.addSeparator()
        self.__mBrowserToolbar.addAction(self.actionShowInfoaboutSelection)
        self.__mBrowserToolbar.addSeparator()
        self.__mBrowserToolbar.addWidget(bt)
        self.__mBrowserToolbar.addSeparator()
        self.__mBrowserToolbar.addAction(self.actionShowHelpPage)

        self.rightWidgetLayout.insertWidget(0, self.__mBrowserToolbar)

        # connect signals from vfkbrowser when changing history
        self.vfkBrowser.currentParIdsChanged.connect(self.actionSelectParInMap.setEnabled)
        self.vfkBrowser.currentBudIdsChanged.connect(self.actionSelectBudInMap.setEnabled)
        self.vfkBrowser.historyBefore.connect(self.actionBack.setEnabled)
        self.vfkBrowser.historyAfter.connect(self.actionForward.setEnabled)
        self.vfkBrowser.definitionPointAvailable.connect(self.actionCuzkPage.setEnabled)

        # add toolTips
        self.pb_nextFile.setToolTip('Přidej další soubor VFK')
        self.parCheckBox.setToolTip('Načti vrstvu parcel')
        self.budCheckBox.setToolTip('Načti vrstvu budov')

        # add new VFK file
        self.pb_nextFile.clicked.connect(self.__addRowToGridLayout)

        # widget apply changes
        self.pb_mainDb.clicked.connect(
            lambda: self.browseDb_clicked('mainDb'))
        self.pb_amendmentDb.clicked.connect(
            lambda: self.browseDb_clicked('amendmentDb'))
        self.pb_exportDb.clicked.connect(
            lambda: self.browseDb_clicked('exportDb'))

        self.pb_applyChanges.clicked.connect(self.applyChanges)
        self.pb_applyChanges.setEnabled(False)

        self.changes_instance.maxRangeProgressBar.connect(self.__setRangeProgressBarChanges)
        self.changes_instance.updateStatus.connect(self.__updateProgressBarChanges)
        self.changes_instance.finishedStatus.connect(self.__changesApplied)
        self.changes_instance.preprocessingDatabase.connect(self.__changesPreprocessingDatabase)

        # connect radio boxes
        self.rb_file.clicked.connect(self.radioButtonValue)
        self.rb_directory.clicked.connect(self.radioButtonValue)

        # posidents widget
        self.wsdpQueryButton.clicked.connect(self.downloadPosidents)
        self.wsdpTrial.stateChanged.connect(self.setWSDPTrial)
