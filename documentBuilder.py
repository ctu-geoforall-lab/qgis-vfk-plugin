from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object
# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject

from qgis.utils import iface

from .vfkDocument import *
from .vfkTableModel import *
from .htmlDocument import *
from .domains import *

class Coordinates(object):

    def __init__(self):
        self.first = ''
        self.second = ''


class DocumentBuilder(object):

    def __init__(self, connectionName=''):
        """
        :type connectionName: str
        """
        # variables
        self.__mCurrentPageParIds = []
        self.__mCurrentPageBudIds = []
        self.__mCurrentDefinitionPoint = Coordinates()
        self.__mDocument = None

        # constructor depended decision
        if connectionName:
            self.__mHasConnection = True
            self.__mConnectionName = connectionName
            self.__mDveRadyCislovani = False
            self.__mStringBezZapisu = "Bez zápisu."
            self.initKatUzemi()
        else:
            self.__mHasConnection = False

    def currentParIds(self):
        return self.__mCurrentPageParIds

    def currentBudIds(self):
        return self.__mCurrentPageBudIds

    def currentDefinitionPoint(self):
        return self.__mCurrentDefinitionPoint

    def buildHtml(self, document, taskMap):
        """

        :type document: VfkDocument
        :type taskMap: dict
        """
        self.__mCurrentPageParIds = []
        self.__mCurrentPageBudIds = []
        self.__mCurrentDefinitionPoint.first = ''
        self.__mCurrentDefinitionPoint.second = ''

        self.__mDocument = document
        self.__mDocument.header()

        if taskMap["page"] == "help":
            self.pageHelp()

        if self.__mHasConnection:
            if taskMap["page"] == "tel":
                self.pageTeleso(taskMap["id"])
            elif taskMap["page"] == "par":
                self.pageParcela(taskMap["id"])
            elif taskMap["page"] == "bud":
                self.pageBudova(taskMap["id"])
            elif taskMap["page"] == "jed":
                self.pageJednotka(taskMap["id"])
            elif taskMap["page"] == "opsub":
                self.pageOpravnenySubjekt(taskMap["id"])
            elif taskMap["page"] == "seznam":
                if taskMap["type"] == "id":
                    if "parcely" in taskMap:
                        self.pageSeznamParcel(taskMap["parcely"].split(","))
                    if "budovy" in taskMap:
                        self.pageSeznamBudov(taskMap["budovy"].split(","))
                elif taskMap["type"] == "string":
                    if "opsub" in taskMap:
                        self.pageSeznamOsob(taskMap['opsub'].split(","))
            elif taskMap["page"] == "search":
                if taskMap["type"] == "vlastnici":
                    self.pageSearchVlastnici(
                        taskMap["jmeno"], taskMap["rcIco"],
                                             taskMap["sjm"], taskMap["opo"],
                                             taskMap["ofo"], taskMap["lv"])
                elif taskMap["type"] == "parcely":
                    self.pageSearchParcely(
                        taskMap["parcelniCislo"], taskMap["typ"], taskMap["druh"], taskMap["lv"])
                elif taskMap["type"] == "budovy":
                    self.pageSearchBudovy(
                        taskMap["domovniCislo"], taskMap[
                            "naParcele"], taskMap["zpusobVyuziti"],
                                          taskMap["lv"])
                elif taskMap["type"] == "jednotky":
                    self.pageSearchJednotky(
                        taskMap["cisloJednotky"], taskMap[
                            "domovniCislo"], taskMap["naParcele"],
                                            taskMap["zpusobVyuziti"], taskMap["lv"])
        self.__mDocument.footer()
        return

    def initKatUzemi(self):
        model = VfkTableModel(self.__mConnectionName)

        if model.dveRadyCislovani():
            self.__mDveRadyCislovani = True

    def pageTelesa(self):
        model = VfkTableModel(self.__mConnectionName)

        ok = model.telesa()
        if not ok:
            return

        for i in range(model.rowCount()):
            tel_id = model.value(i, "tel_id")
            cislo_tel = model.value(i, "tel_cislo_tel")
            link = self.__mDocument.link(
                "showText?page=tel&id={}".format(tel_id), cislo_tel + "<br/>")
            self.__mDocument.text(link)

    def pageTeleso(self, id):
        """

        :type id: str
        :return:
        """
        parIds = []
        budIds = []
        jedIds = []
        opsubIds = []

        self.partTelesoHlavicka(id)
        # self.partTelesoVlastnici(id, opsubIds, True)
        self.partTelesoNemovitosti(id, parIds, budIds, jedIds)

        self.partTelesoB1(parIds, budIds, jedIds, opsubIds, True)
        self.partTelesoC(parIds, budIds, jedIds, opsubIds, True)
        self.partTelesoD(parIds, budIds, jedIds, opsubIds, True)
        self.partTelesoE(parIds, budIds, jedIds)
        self.partTelesoF(parIds, True)

    def partTelesoHlavicka(self, id):
        """

        :type id: str
        :return:
        """
        hlavickaModel = VfkTableModel(self.__mConnectionName)

        ok = hlavickaModel.telesoHlavicka(id)
        if not ok:
            return

        self.__mDocument.heading1("List vlastnictví")
        content = [TPair(
            "List vlastnictví:", self.makeLVCislo(hlavickaModel, 0)),
            TPair(
            "Kat. území:", self.makeKatastrUzemi(hlavickaModel, 0)),
                   TPair("Obec:", self.makeObec(hlavickaModel, 0)),
                   TPair(
                       "Okres:", "{} {}".format(hlavickaModel.value(0, "okresy_nazev"),
                                                  hlavickaModel.value(0, "okresy_nuts4")))]

        self.__mDocument.keyValueTable(content)

        if hlavickaModel.dveRadyCislovani():
            self.__mDocument.paragraph(
                "V kat. území jsou pozemky vedeny ve dvou číselných řadách.")
        else:
            self.__mDocument.paragraph(
                "V kat. území jsou pozemky vedeny v jedné číselné řadě.")

    def partTelesoNemovitosti(self, id, parIds, budIds, jedIds):
        """

        :type id: str
        :type parIds: list
        :type budIds: list
        :type jedIds: list
        """
        self.__mDocument.heading2("B – Nemovitosti")
        self.partTelesoParcely(id, parIds)
        self.partTelesoBudovy(id, budIds)
        self.partTelesoJednotky(id, jedIds)

        self.__mCurrentPageParIds = parIds
        self.__mCurrentPageBudIds = budIds

    def partVlastnikNemovitosti(self, opsubId):
        """

        :type opsubId: str
        """
        self.__mDocument.heading2("Nemovitosti vlastníka")
        self.partVlastnikParcely(opsubId)
        self.partVlastnikBudovy(opsubId)
        self.partVlastnikJednotky(opsubId)

    def partTelesoParcely(self, opsubId, parIds):
        """

        :type opsubId: str
        :type parIds: list
        """
        model = VfkTableModel(self.__mConnectionName)

        ok = model.telesoParcely(opsubId, False)
        if not ok or model.rowCount() == 0:
            return

        self.tableParcely(model, parIds, False)

    def partVlastnikParcely(self, id):
        """

        :type id: str
        """
        model = VfkTableModel(self.__mConnectionName)

        ok = model.vlastnikParcely(id, False)
        if not ok or model.rowCount() == 0:
            return

        parIds = []
        self.tableParcely(model, parIds, True)
        self.__mCurrentPageParIds = parIds

    def tableParcely(self, model, parIds, LVColumn):
        """

        :type model: VfkTableModel
        :type parIds: list
        :type LVColumn: bool
        """
        self.__mDocument.heading3("Pozemky")
        self.__mDocument.beginTable()
        header = [
            "Parcela", "Výměra [m{}]".format(
                self.__mDocument.superScript(
                    "2")), "Druh pozemk", "Způsob využití",
                  "Způsob ochrany"]
        if LVColumn:
            header.append("LV")

        self.__mDocument.tableHeader(header)

        for i in range(model.rowCount()):
            row = [self.makeParcelniCislo(
                model, i), model.value(i, "par_vymera_parcely"),
                model.value(i, "drupoz_nazev"), model.value(i, "zpvypo_nazev")]

            parcelaId = model.value(i, "par_id")
            ochranaModel = VfkTableModel(self.__mConnectionName)

            ok = ochranaModel.nemovitostOchrana(
                parcelaId, VfkTableModel.Nemovitost.NParcela)
            if not ok:
                break

            ochranaNazev = []
            for j in range(ochranaModel.rowCount()):
                ochranaNazev.append(ochranaModel.value(j, "zpochn_nazev"))

            row.append(", ".join(ochranaNazev))

            if LVColumn:
                row.append(self.makeLVCislo(model, i))

            self.__mDocument.tableRow(row)
            parIds.append(parcelaId)
        self.__mDocument.endTable()

    def partTelesoBudovy(self, opsubId, budIds):
        """

        :type opsubId: str
        :type budIds: list
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)

        ok = model.telesoBudovy(opsubId, False)
        if not ok or model.rowCount() == 0:
            return

        self.tableBudovy(model, budIds, False)

    def partVlastnikBudovy(self, id):
        """

        :type id: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)

        ok = model.vlastnikBudovy(id, False)
        if not ok or model.rowCount() == 0:
            return

        budIds = []
        self.tableBudovy(model, budIds, True)
        self.__mCurrentPageBudIds.append(budIds)

    def tableBudovy(self, model, budIds, LVColumn):
        """

        :param model: VfkTableModel
        :param budIds: list
        :param LVColumn: bool
        :return:
        """
        self.__mDocument.heading3("Stavby")
        self.__mDocument.beginTable()
        header = ["Typ stavby", "Část obce", "Č. budovy",
                  "Způsob využití", "Způsob ochrany", "Na parcele"]

        if LVColumn:
            header.append("LV")

        self.__mDocument.tableHeader(header)

        for i in range(model.rowCount()):
            row = []

            if Domains.anoNe(model.value(i, "typbud_zadani_cd")) is False:
                row.append(
                    self.__mDocument.link(
                        "showText?page=bud&id={}".format(
                            model.value(i, "bud_id")),
                                                 model.value(i, "typbud_zkratka")))
                row.append(model.value(i, "casobc_nazev"))
                row.append('')
            else:
                row.append('')
                row.append(model.value(i, "casobc_nazev"))
                row.append(
                    self.__mDocument.link(
                        "showText?page=bud&id={}".format(
                            model.value(i, "bud_id")),
                                                 "{} {}".format(model.value(i, "typbud_zkratka"),
                                                                 model.value(i, "bud_cislo_domovni"))))
            row.append(model.value(i, "zpvybu_nazev"))

            budId = model.value(i, "bud_id")
            ochranaModel = VfkTableModel(self.__mConnectionName)

            ok = ochranaModel.nemovitostOchrana(
                budId, VfkTableModel.Nemovitost.NBudova)
            if not ok:
                break

            ochranaNazev = []
            for j in range(ochranaModel.rowCount()):
                ochranaNazev.append(ochranaModel.value(j, "zpochn_nazev"))

            row.append(", ".join(ochranaNazev))
            row.append(self.makeParcelniCislo(model, i))

            if LVColumn:
                row.append(self.makeLVCislo(model, i))

            self.__mDocument.tableRow(row)
            budIds.append(budId)
        self.__mDocument.endTable()

    def partTelesoJednotky(self, id, jedIds):
        """

        :type id: str
        :type jedIds: list
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)

        ok = model.telesoJednotky(id, False)
        if ok is False or model.rowCount() == 0:
            return

        self.tableJednotky(model, jedIds, False)

    def partVlastnikJednotky(self, opsubId):
        """

        :type opsubId: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)

        ok = model.vlastnikJednotky(opsubId, False)
        if not ok or model.rowCount() == 0:
            return

        jedIds = []
        self.tableJednotky(model, jedIds, True)

    def tableJednotky(self, model, jedIds, LVColumn):
        """

        :type model: VfkTableModel
        :type jedIds: list
        :type LVColumn: bool
        :return:
        """
        self.__mDocument.heading3("Jednotky")
        self.__mDocument.beginTable()
        header = ["Č.p./Č.jednotky ", "Způsob využití", "Způsob ochrany",
                  "Podíl na společných{}částech domu a pozemk".format(self.__mDocument.newLine())]

        if LVColumn:
            header.append("LV")

        self.__mDocument.tableHeader(header)

        for i in range(model.rowCount()):
            row = []

            jedId = model.value(i, "jed_id")
            row.append(self.makeJednotka(model, i))
            row.append(model.value(i, "zpvyje_nazev"))
            ochranaModel = VfkTableModel(self.__mConnectionName)

            ok = ochranaModel.nemovitostOchrana(
                jedId, VfkTableModel.Nemovitost.NJednotka)
            if not ok:
                break

            ochranaNazev = []
            for j in range(ochranaModel.rowCount()):
                ochranaNazev.append(ochranaModel.value(j, "zpochn_nazev"))

            row.append(", ".join(ochranaNazev))

            podilCit = model.value(i, "jed_podil_citatel")
            podilJmen = model.value(i, "jed_podil_jmenovatel")
            podil = ''

            if podilCit and podilJmen and podilJmen != "1":
                podil += "{}/{}".format(podilCit, podilJmen)

            row.append(podil)

            if LVColumn:
                row.append(self.makeLVCislo(model, i))

            self.__mDocument.tableRow(row)
            self.partTelesoJednotkaDetail(model.value(i, "bud_id"))

            jedIds.append(jedId)
        self.__mDocument.endTable()

    def partTelesoJednotkaDetail(self, budId):
        """

        :type budId: str
        :return:
        """
        budInfo = ''
        parInfo = ''

        budModel = VfkTableModel(self.__mConnectionName)
        ok = budModel.budova(budId, False)
        if not ok or budModel.rowCount() == 0:
            return

        budInfo += "Budova" + " "
        casobc = budModel.value(0, "casobc_nazev")
        budInfo += '' if casobc else casobc + ", "

        budova = ''
        budova += budModel.value(0, "typbud_zkratka")
        if Domains.anoNe(budModel.value(0, "typbud_zadani_cd")):
            budova += " " + budModel.value(0, "bud_cislo_domovni")
        budInfo += self.__mDocument.link(
            "showText?page=bud&id={}".format(budId), budova)

        lv = budModel.value(0, "tel_cislo_tel")
        lvId = budModel.value(0, "tel_id")
        if lv:
            budInfo += self.__mDocument.link(
                "showText?page=tel&id={}".format(lvId), "LV {}".format(lv))

        zpvybu = budModel.value(0, "zpvybu_nazev")
        budInfo += ", {}".format(zpvybu) if zpvybu else ''

        budInfo + ", na parcele {}".format(
            self.makeParcelniCislo(budModel, 0))

        self.__mDocument.tableRowOneColumnSpan(budInfo)

        parcelaId = budModel.value(0, "par_id")
        parModel = VfkTableModel(self.__mConnectionName)
        ok = parModel.parcela(parcelaId, False)
        if not ok:
            return

        parInfo += "Parcela {}".format(self.makeParcelniCislo(parModel, 0))
        lv = parModel.value(0, "tel_cislo_tel")
        lvId = parModel.value(0, "tel_id")
        if lv:
            parInfo += self.__mDocument.link(
                "showText?page=tel&id={}".format(lvId), "LV {}".format(lv))

        zpvypo = parModel.value(0, "zpvypo_nazev")
        parInfo += '' if not zpvypo else ", {}".format(zpvypo)
        parInfo += ", {} m{}".format(
            parModel.value(0, "par_vymera_parcely"), self.__mDocument.superScript("2"))

        self.__mDocument.tableRowOneColumnSpan(parInfo)

    def partTelesoB1(self, parIds, budIds, jedIds, opsubIds, forLV):
        """

        :type parIds: list
        :type budIds: list
        :type jedIds: list
        :type opsubIds: list
        :type forLV: bool
        """

        header = ["Typ vztah", "Oprávnění pro", "Povinnost k"]

        if forLV:
            self.__mDocument.heading2("B1 – Jiná práva")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partTelesoJinaPrava(parIds, VfkTableModel.OpravnenyPovinny.OPParcela) or \
                    self.partTelesoJinaPrava(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partTelesoJinaPrava(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka) or \
                    self.partTelesoJinaPrava(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)
        else:
            self.__mDocument.heading2("Jiná práva")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partNemovitostJinaPrava(parIds, VfkTableModel.OpravnenyPovinny.OPParcela) or \
                    self.partNemovitostJinaPrava(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partNemovitostJinaPrava(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka) or \
                    self.partNemovitostJinaPrava(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)

    def partTelesoC(self, parIds, budIds, jedIds, opsubIds, forLV):
        """

        :type parIds: list
        :type budIds: list
        :type jedIds: list
        :type opsubIds: list
        :type forLV: bool
        """
        header = ["Typ vztah", "Oprávnění pro", "Povinnost k"]

        if forLV:
            self.__mDocument.heading2("C – Omezení vlastnického práva")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partTelesoOmezeniPrava(parIds, VfkTableModel.OpravnenyPovinny.OPParcela) or \
                    self.partTelesoOmezeniPrava(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partTelesoOmezeniPrava(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka) or \
                    self.partTelesoOmezeniPrava(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)
        else:
            self.__mDocument.heading2("Omezení vlastnického práva")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partNemovitostOmezeniPrava(parIds, VfkTableModel.OpravnenyPovinny.OPParcela) or \
                    self.partNemovitostOmezeniPrava(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partNemovitostOmezeniPrava(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka) or \
                    self.partNemovitostOmezeniPrava(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)

    def partTelesoD(self, parIds, budIds, jedIds, opsubIds, forLV):
        """

        :type parIds: list
        :type budIds: list
        :type jedIds: list
        :type opsubIds: list
        :type forLV: bool
        """
        header = ["Typ vztah", "Vztah pro", "Vztah k"]

        if forLV:
            self.__mDocument.heading2("D – Jiné zápisy")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partTelesoJineZapisy(parIds, VfkTableModel.OpravnenyPovinny.OPParcela) or \
                    self.partTelesoJineZapisy(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partTelesoJineZapisy(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka) or \
                    self.partTelesoJineZapisy(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)
        else:
            self.__mDocument.heading2("Jiné zápisy")
            self.__mDocument.beginTable()
            self.__mDocument.tableHeader(header)

            if self.partNemovitostJineZapisy(parIds, VfkTableModel.OpravnenyPovinny.OPParcela) or \
                    self.partNemovitostJineZapisy(budIds, VfkTableModel.OpravnenyPovinny.OPBudova) or \
                    self.partNemovitostJineZapisy(jedIds, VfkTableModel.OpravnenyPovinny.OPJednotka) or \
                    self.partNemovitostJineZapisy(opsubIds, VfkTableModel.OpravnenyPovinny.OPOsoba):
                self.__mDocument.endTable()
            else:
                self.__mDocument.discardLastBeginTable()
                self.__mDocument.text(self.__mStringBezZapisu)

    def partTelesoE(self, parIds, budIds, jedIds):
        """

        :type parIds: list
        :type budIds: list
        :type jedIds: list
        """
        self.__mDocument.heading2(
            "E – Nabývací tituly a jiné podklady k zápis")

        model = VfkTableModel(self.__mConnectionName)
        ok = model.nabyvaciListiny(parIds, budIds, jedIds)
        if not ok:
            return

        if model.rowCount() == 0:
            self.__mDocument.text(self.__mStringBezZapisu)
        else:
            lastListinaId = ''
            self.__mDocument.beginItemize()
            for i in range(model.rowCount()):
                currentListinaId = model.value(i, "rl_listin_id")
                if currentListinaId == lastListinaId:
                    self.__mDocument.item(
                        self.makeShortDescription(
                            model.value(i, "rl_opsub_id"),
                                                                    VfkTableModel.OpravnenyPovinny.OPOsoba))
                else:
                    if lastListinaId:
                        self.__mDocument.endItemize()
                        self.__mDocument.endItem()
                    lastListinaId = currentListinaId
                    self.__mDocument.beginItem()
                    self.__mDocument.text(self.makeListina(model, i))
                    self.__mDocument.beginItemize()
                    self.__mDocument.item(
                        self.makeShortDescription(
                            model.value(i, "rl_opsub_id"),
                                                                    VfkTableModel.OpravnenyPovinny.OPOsoba))

            if lastListinaId:
                self.__mDocument.endItemize()
                self.__mDocument.endItem()

            self.__mDocument.endItemize()

    def partTelesoF(self, parIds, forLV):
        """

        :type parIds: list
        :type forLV: bool
        """
        if forLV:
            self.__mDocument.heading2(
                "F – Vztah bonitovaných půdně ekologických jednotek (BPEJ) k parcelám")
        else:
            self.__mDocument.heading2("BPEJ")

        header = ["Parcela", "BPEJ", "Výměra [m{}]".format(
            self.__mDocument.superScript("2"))]
        self.__mDocument.beginTable()
        self.__mDocument.tableHeader(header)

        isRecord = False
        for id in parIds:
            row = []
            model = VfkTableModel(self.__mConnectionName)
            ok = model.parcelaBpej(id)
            if not ok:
                break

            if model.rowCount() == 0:
                continue

            isRecord = True
            row.append(self.makeParcelniCislo(model, 0))
            row.append(model.value(0, "bdp_bpej_kod"))
            row.append(model.value(0, "bdp_vymera"))

            self.__mDocument.tableRow(row)

        if isRecord:
            self.__mDocument.endTable()
        else:
            self.__mDocument.discardLastBeginTable()
            self.__mDocument.text(self.__mStringBezZapisu)

    def partNemovitostJinaPrava(self, ids, opravneny):
        """

        :type ids: list
        :type opravneny: VfkTableModel.OpravnenyPovinny
        :return:
        """
        return self.partTelesoB1CDSubjekt(ids, opravneny, VfkTableModel.Pravo.Opravneni, False, False)

    def partTelesoJinaPrava(self, ids, opravneny):
        """

        :type ids: list
        :type opravneny: VfkTableModel.OpravnenyPovinny
        :return:
        """
        return self.partTelesoB1CDSubjekt(ids, opravneny, VfkTableModel.Pravo.Opravneni, False, True)

    def partNemovitostOmezeniPrava(self, ids, povinny):
        """

        :type ids: list
        :type povinny: VfkTableModel.OpravnenyPovinny
        :return:
        """
        return self.partTelesoB1CDSubjekt(ids, povinny, VfkTableModel.Pravo.Povinnost, False, False)

    def partTelesoOmezeniPrava(self, ids, povinny):
        """

        :type ids: list
        :type povinny: VfkTableModel.OpravnenyPovinny
        :return:
        """
        return self.partTelesoB1CDSubjekt(ids, povinny, VfkTableModel.Pravo.Povinnost, False, True)

    def partNemovitostJineZapisy(self, ids, povinny):
        """

        :type ids: list
        :type povinny: VfkTableModel.OpravnenyPovinny
        :return: bool
        """
        test1 = self.partTelesoB1CDSubjekt(
            ids, povinny, VfkTableModel.Pravo.Opravneni, True, False)
        test2 = self.partTelesoB1CDSubjekt(
            ids, povinny, VfkTableModel.Pravo.Povinnost, True, False)
        return test1 or test2

    def partTelesoJineZapisy(self, ids, povinny):
        """

        :type ids: list
        :type povinny: VfkTableModel.OpravnenyPovinny
        :return: bool
        """
        test1 = self.partTelesoB1CDSubjekt(
            ids, povinny, VfkTableModel.Pravo.Opravneni, True, True)
        test2 = self.partTelesoB1CDSubjekt(
            ids, povinny, VfkTableModel.Pravo.Povinnost, True, True)
        return test1 or test2

    def partTelesoB1CDSubjekt(self, ids, pravniSubjekt, pravo, sekceD, showListiny):
        """

        :type ids: list
        :type pravniSubjekt: VfkTableModel.OpravnenyPovinny
        :type pravo: VfkTableModel.Pravo
        :type sekceD: bool
        :type showListiny: bool
        :return: bool
        """
        isRecord = False
        povinni = ["jpv_par_id_k", "jpv_bud_id_k",
                   "jpv_jed_id_k", "jpv_opsub_id_k"]
        opravneni = ["jpv_par_id_pro", "jpv_bud_id_pro",
                     "jpv_jed_id_pro", "jpv_opsub_id_pro"]

        for id in ids:
            model = VfkTableModel(self.__mConnectionName)
            where = "typrav.sekce {}= 'D'".format('' if sekceD else '!')
            ok = model.nemovitostJpv(id, pravniSubjekt, pravo, where)
            if not ok or model.rowCount() == 0:
                continue

            isRecord = True
            for i in range(model.rowCount()):
                row = []
                typPrava = model.value(i, "typrav_nazev")
                row.append(typPrava)

                opravneniList = []
                for column1 in opravneni:
                    if model.value(i, column1):
                        opravneny = VfkTableModel().tableName2OpravnenyPovinny(
                            column1)
                        opravnenyId = model.value(i, column1)
                        opravneniList.append(
                            self.makeShortDescription(opravnenyId, opravneny))

                row.append(str(self.__mDocument.newLine()).join(opravneniList))

                povinniList = []
                for column2 in povinni:
                    if model.value(i, column2):
                        povinny = VfkTableModel().tableName2OpravnenyPovinny(
                            column2)
                        povinnyId = model.value(i, column2)
                        povinniList.append(
                            self.makeShortDescription(povinnyId, povinny))

                row.append(str(self.__mDocument.newLine()).join(povinniList))

                self.__mDocument.tableRow(row)

                if showListiny:
                    self.partTelesoListiny(model.value(i, "jpv_id"))

        return isRecord

    def partTelesoListiny(self, jpvId):
        """

        :type jpvId: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.jpvListiny(jpvId)
        if not ok:
            return

        for i in range(model.rowCount()):
            self.__mDocument.tableRowOneColumnSpan(self.makeListina(model, i))

    def pageParcela(self, id):
        """

        :type id: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.parcela(id, True)
        if not ok:
            return

        self.__mCurrentPageParIds.append(id)
        self.saveDefinitionPoint(id, VfkTableModel.Nemovitost.NParcela)

        content = [TPair("Parcelní číslo:", self.makeParcelniCislo(model, 0))]

        telesoModel = VfkTableModel(self.__mConnectionName)
        telesoModel.nemovitostTeleso(id, VfkTableModel.Nemovitost.NParcela)
        content.append(
            TPair("List vlastnictví:", self.makeLVCislo(telesoModel, 0)))
        content.append(
            TPair("Výměra [m{}]:".format(self.__mDocument.superScript("2")),
                  model.value(0, "par_vymera_parcely")))
        content.append(
            TPair("Určení výměry:", model.value(0, "zpurvy_nazev")))

        if model.value(0, "par_cena_nemovitosti"):
            content.append(
                TPair("Cena nemovitosti:", model.value(0, "par_cena_nemovitosti")))

        content.append(TPair("Typ parcely:", model.value(0, "par_par_type")))
        content.append(
            TPair("Mapový list:", model.value(0, "maplis_oznaceni_mapoveho_list")))
        content.append(
            TPair("Katastrální území:", self.makeKatastrUzemi(model, 0)))
        content.append(
            TPair("Druh pozemku:", model.value(0, "drupoz_nazev")))

        if model.value(0, "zpvypo_nazev"):
            content.append(
                TPair("Způsob využití pozemku:", model.value(0, "zpvypo_nazev")))

        if Domains.anoNe(model.value(0, "drupoz_stavebni_parcela")):
            content.append(
                TPair("Stavba na parcele:", self.makeDomovniCislo(model, 0)))
            self.__mCurrentPageBudIds.append(model.value(0, "bud_id"))

        self.__mDocument.heading1("Informace o parcele")
        self.__mDocument.keyValueTable(content)

        # neighbours
        sousedniModel = VfkTableModel(self.__mConnectionName)
        sousedniModel.sousedniParcely(id)
        ids = []
        for i in range(0, sousedniModel.rowCount()):
            ids.append(sousedniModel.value(i, "hp_par_id_1"))
            ids.append(sousedniModel.value(i, "hp_par_id_2"))

        ids = list(set(ids))
        ids.remove(id)

        link = self.__mDocument.link(
            "showText?page=seznam&type=id&parcely={}".format(",".join(ids)),
                                     "Sousední parcely")

        self.__mDocument.paragraph(link)
        opsubIds = []
        # self.partTelesoVlastnici(
        #     telesoModel.value(0, "tel_id"), opsubIds, False)
        self.partNemovitostOchrana(id, VfkTableModel.Nemovitost.NParcela)

        parIds = [id]
        tempList = []
        self.partTelesoB1(parIds, tempList, tempList, tempList, False)
        self.partTelesoC(parIds, tempList, tempList, tempList, False)
        self.partTelesoD(parIds, tempList, tempList, tempList, False)
        self.partTelesoF(parIds, False)

    def partTelesoVlastnici(self, id, opsubIds, forLV):
        """

        :type id: str
        :type opsubIds: list
        :type forLV: bool
        :return:
        """
        # vlastniciModel = VfkTableModel(self.__mConnectionName)
        # ok = vlastniciModel.telesoVlastnici(id)
        # if not ok:
            # return
        if forLV:
            self.__mDocument.heading2("A – Vlastníci, jiní oprávnění")
        else:
            self.__mDocument.heading2("Vlastníci, jiní oprávnění")
        
        self.mDocument.text("Informace o vlastníkovi není dostupná.")
    #     orderedPrava = []
    #     for i in range(vlastniciModel.rowCount()):
    #         orderedPrava.append(vlastniciModel.value(i, "typrav_nazev"))

    #     orderedPrava = list(set(orderedPrava))

    #     # tables =  {[[]]}
    #     tables = {}
    #     header = ["Jméno", "Adresa", "Identifikátor", "Podíl"]

    #     for i, item in enumerate(orderedPrava):
    #         table = [header]
    #         tables[orderedPrava[i]] = table

    #     for i in range(vlastniciModel.rowCount()):
    #         typravNazev = vlastniciModel.value(i, "typrav_nazev")
    #         opsubId = vlastniciModel.value(i, "vla_opsub_id")
    #         vlaPodilCitatel = vlastniciModel.value(i, "vla_podil_citatel")
    #         vlaPodilJmenovatel = vlastniciModel.value(
    #             i, "vla_podil_jmenovatel")
    #         podil = ''

    #         if vlaPodilCitatel and vlaPodilJmenovatel and vlaPodilJmenovatel != '1':
    #             podil += "{}/{}".format(vlaPodilCitatel, vlaPodilJmenovatel)

    #         vlastnikModel = VfkTableModel(self.__mConnectionName)
    #         ok = vlastnikModel.vlastnik(opsubId, True)
    #         if not ok:
    #             return

    #         opsub_type = vlastnikModel.value(0, "opsub_opsub_type")
    #         nazev = self.makeJmeno(vlastnikModel, 0)

    #         if opsub_type != "BSM":
    #             content = []
    #             adresa = self.makeAdresa(vlastnikModel, 0)
    #             identifikator = self.makeIdentifikator(vlastnikModel, 0)
    #             content.append(nazev)
    #             content.append(adresa)
    #             content.append(identifikator)
    #             content.append(podil)
    #             tables[typravNazev].append(content)
    #         else:
    #             nazev += " ({})".format(
    #                 vlastnikModel.value(0, "charos_zkratka"))
    #             rowContent = [nazev, '', '', podil]
    #             tables[typravNazev].append(rowContent)

    #             manzeleId = [vlastnikModel.value(
    #                 0, "opsub_id_je_1_partner_bsm"),
    #                 vlastnikModel.value(0, "opsub_id_je_2_partner_bsm")]

    #             sjmModel = VfkTableModel(self.__mConnectionName)
    #             for j in range(len(manzeleId)):
    #                 ok = sjmModel.vlastnik(manzeleId[j])
    #                 if not ok:
    #                     break

    #                 identifikatorSJM = sjmModel.value(0, "opsub_rodne_cislo")
    #                 rowContent = [self.makeJmeno(sjmModel, 0), self.makeAdresa(
    #                     sjmModel, 0), identifikatorSJM, '']
    #                 tables[typravNazev].append(rowContent)

    #         opsubIds.append(opsubId)
    #     for i in range(len(orderedPrava)):
    #         self.__mDocument.heading3(orderedPrava[i])
    #         self.__mDocument.table(tables[orderedPrava[i]], True)

    def partNemovitostOchrana(self, id, nemovitost):
        """

        :type id: str
        :type nemovitost: VfkTableModel.Nemovitost
        :return:
        """
        ochrana = VfkTableModel(self.__mConnectionName)
        ok = ochrana.nemovitostOchrana(id, nemovitost)
        if not ok:
            return

        self.__mDocument.heading2("Způsob ochrany nemovitosti")

        if ochrana.rowCount() == 0:
            self.__mDocument.text("Není evidován žádný způsob ochrany.")
        else:
            self.__mDocument.beginTable()
            header = ["Název"]

            for i in range(ochrana.rowCount()):
                content = [ochrana.value(i, "zpochn_nazev")]
                self.__mDocument.tableRow(content)

            self.__mDocument.endTable()

    def pageBudova(self, id):
        """

        :type id: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.budova(id, True)
        if not ok:
            return

        self.__mCurrentPageBudIds.append(id)
        self.saveDefinitionPoint(id, VfkTableModel.Nemovitost.NBudova)

        content = []

        if Domains.anoNe(model.value(0, "typbud_zadani_cd")):
            content.append(TPair("Stavba:", self.makeDomovniCislo(model, 0)))
            content.append(TPair("Část obce:", self.makeCastObce(model, 0)))

        content.append(TPair("Na parcele:", self.makeParcelniCislo(model, 0)))
        self.__mCurrentPageParIds.append(model.value(0, "par_id"))

        telesoModel = VfkTableModel(self.__mConnectionName)
        telesoModel.nemovitostTeleso(id, VfkTableModel.Nemovitost.NBudova)
        content.append(
            TPair("List vlastnictví:", self.makeLVCislo(telesoModel, 0)))

        cena = model.value(0, "bud_cena_nemovitosti")
        if cena:
            content.append(TPair("Cena nemovitosti:", cena))
        content.append(TPair("Typ stavby:", model.value(0, "typbud_nazev")))
        content.append(
            TPair("Způsob využití:", model.value(0, "zpvybu_nazev")))

        jednotkyModel = VfkTableModel(self.__mConnectionName)
        jednotkyModel.budovaJednotky(id)
        if jednotkyModel.rowCount() > 0:
            jednotky = []
            for i in range(jednotkyModel.rowCount()):
                jednotky.append(self.makeJednotka(jednotkyModel, i))

            content.append(TPair("Jednotky v budově:", ", ".join(jednotky)))

        content.append(
            TPair("Katastrální území:", self.makeKatastrUzemi(model, 0)))

        self.__mDocument.heading1("Informace o stavbě")
        self.__mDocument.keyValueTable(content)

        opsubIds = []
        # self.partTelesoVlastnici(
        #     telesoModel.value(0, "tel_id"), opsubIds, False)
        self.partNemovitostOchrana(id, VfkTableModel.Nemovitost.NBudova)

        budIds = [id]
        self.partTelesoB1([], budIds, [], [], False)
        self.partTelesoC([], budIds, [], [], False)
        self.partTelesoD([], budIds, [], [], False)

    def pageJednotka(self, id):
        """

        :type id: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.jednotka(id, True)
        if not ok:
            return

        content = [TPair("Číslo jednotky:", self.makeJednotka(model, 0)),
                   TPair("V budově:", self.makeDomovniCislo(model, 0)),
                   TPair("Na parcele:", self.makeParcelniCislo(model, 0))]

        self.__mCurrentPageParIds.append(model.value(0, "par_id"))
        self.__mCurrentPageBudIds.append(model.value(0, "bud_id"))

        telesoModel = VfkTableModel(self.__mConnectionName)
        telesoModel.nemovitostTeleso(id, VfkTableModel.Nemovitost.NJednotka)
        content.append(
            TPair("List vlastnictví:", self.makeLVCislo(telesoModel, 0)))

        cena = model.value(0, "jed_cena_nemovitosti")
        if cena:
            content.append(TPair("Cena nemovitosti:", cena))

        content.append(
            TPair("Typ jednotky:", model.value(0, "typjed_nazev")))
        content.append(
            TPair("Způsob využití:", model.value(0, "zpvyje_nazev")))
        content.append(TPair("Podíl jednotky na společných částech domu:", "{}/{}"
                             .format(model.value(0, "jed_podil_citatel"), model.value(0, "jed_podil_jmenovatel"))))
        content.append(
            TPair("Katastrální území:", self.makeKatastrUzemi(model, 0)))

        self.__mDocument.heading1("Informace o jednotce")
        self.__mDocument.keyValueTable(content)

        opsubIds = []
        # self.partTelesoVlastnici(
        #     telesoModel.value(0, "tel_id"), opsubIds, False)
        self.partNemovitostOchrana(id, VfkTableModel.Nemovitost.NJednotka)

        jedIds = [id]
        self.partTelesoB1([], [], jedIds, [], False)
        self.partTelesoC([], [], jedIds, [], False)
        self.partTelesoD([], [], jedIds, [], False)

    def pageOpravnenySubjekt(self, id):
        """

        :type id: str
        :return:
        """
        opsubModel = VfkTableModel(self.__mConnectionName)
        ok = opsubModel.opravnenySubjekt(id, True)
        if not ok:
            return

        content = []
        name = self.makeJmeno(opsubModel, 0)

        if opsubModel.value(0, "opsub_opsub_type") == "OPO":
            content.append(TPair("Název:", name))
            content.append(TPair("Adresa:", self.makeAdresa(opsubModel, 0)))
            content.append(
                TPair("IČO:", self.makeIdentifikator(opsubModel, 0)))
        elif opsubModel.value(0, "opsub_opsub_type") == "OFO":
            content.append(TPair("Jméno:", name))
            content.append(TPair("Adresa:", self.makeAdresa(opsubModel, 0)))
            content.append(
                TPair("Rodné číslo:", self.makeIdentifikator(opsubModel, 0)))
        else:
            content.append(TPair("Jméno:", name))

            for i in range(1, 3):
                manzelId = opsubModel.value(
                    0, "opsub_id_je_{}_partner_bsm".format(i))
                desc = self.makeShortDescription(
                    manzelId, VfkTableModel.OpravnenyPovinny.OPOsoba)
                content.append(TPair('', desc))

        content.append(TPair("Typ:", opsubModel.value(0, "charos_nazev")))

        nemovitostiModel = VfkTableModel(self.__mConnectionName)
        nemovitostiModel.vlastnikNemovitosti(id)

        telesaDesc = []
        nemovitostDesc = []
        idColumns = ["par_id", "bud_id", "jed_id"]

        for i in range(nemovitostiModel.rowCount()):
            telesaDesc.append(self.makeLVCislo(nemovitostiModel, i))

            for column in idColumns:
                nemovitostDesc.append(
                    self.makeLongDescription(nemovitostiModel.value(i, column),
                                             VfkTableModel().tableName2OpravnenyPovinny(column)))

        telesaDesc = list(set(telesaDesc))
        if telesaDesc:
            content.append(
                TPair("Listy vlastnictví:", ", ".join(telesaDesc)))
        self.__mDocument.heading1("Informace o oprávněné osobě")
        self.__mDocument.keyValueTable(content)

        self.partVlastnikNemovitosti(id)

        opsubIds = [id]
        self.partTelesoB1([], [], [], opsubIds, False)
        self.partTelesoC([], [], [], opsubIds, False)
        self.partTelesoD([], [], [], opsubIds, False)

    def pageSeznamParcel(self, ids):
        """

        :type ids: list
        """
        self.__mDocument.heading2("Seznam parcel")
        self.__mDocument.beginItemize()

        self.__mCurrentPageParIds = ids

        for id in ids:
            model = VfkTableModel(self.__mConnectionName)
            ok = model.parcela(id, False)
            if not ok:
                continue

            self.__mDocument.item(self.makeLongDescription(
                id, VfkTableModel.OpravnenyPovinny.OPParcela))

        self.__mDocument.endItemize()

    def pageSeznamOsob(self, ids):
        """

        :type ids: list
        """
        self.__mDocument.heading2("Seznam osob")
        self.__mDocument.beginItemize()

        self.__mCurrentPageParIds = ids

        count = 0
        for id in ids:
            model = VfkTableModel(self.__mConnectionName)
            ok = model.opravnenySubjekt(id, True)
            if not ok:
                continue

            if self.makeJmeno(model, 0, hyperlink=False):
                self.__mDocument.item(self.makeLongDescription(
                    id, VfkTableModel.OpravnenyPovinny.OPOsoba))
                count += 1

        self.__mDocument.endItemize()

        if count == 0:
            self.__mDocument.text(
                "Seznam osob získejte v záložce \"Stáhnout posidenty pro vybrané budovy a parcely\".")

    def pageSeznamBudov(self, ids):
        """

        :type ids: list
        """
        self.__mDocument.heading2("Seznam budov")
        self.__mDocument.beginItemize()
        self.__mCurrentPageBudIds = ids

        for id in ids:
            self.__mDocument.item(self.makeLongDescription(
                id, VfkTableModel.OpravnenyPovinny.OPBudova))

        self.__mDocument.endItemize()

    def pageSeznamJednotek(self, ids):
        """

        :type ids: list
        """
        self.__mDocument.heading2("Seznam jednotek")
        self.__mDocument.beginItemize()
        self.__mCurrentPageBudIds = ids

        for id in ids:
            self.__mDocument.item(self.makeLongDescription(
                id, VfkTableModel.OpravnenyPovinny.OPJednotka))

        self.__mDocument.endItemize()

    def pageSearchVlastnici(self, jmeno, identifikator, sjm, opo, ofo, lv):
        """

        :type jmeno: str
        :type identifikator: str
        :type sjm: bool
        :type opo: bool
        :type ofo: bool
        :type lv: bool
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.searchOpsub(jmeno, identifikator, sjm, opo, ofo, lv)
        if not ok:
            return

        ids = []
        for i in range(model.rowCount()):
            ids.append(model.value(i, 'opsub_id'))

        self.pageSeznamOsob(ids)

    def pageSearchParcely(self, parcelniCislo, typIndex, druhKod, lv):
        """

        :type parcelniCislo: str
        :type typIndex: str
        :type druhKod: str
        :type lv: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.searchPar(parcelniCislo, typIndex, druhKod, lv)
        if not ok:
            return

        ids = []
        for i in range(model.rowCount()):
            ids.append(model.value(i, "par_id"))

        self.pageSeznamParcel(ids)

    def pageSearchBudovy(self, domovniCislo, naParcele, zpusobVyuziti, lv):
        """

        :type domovniCislo: str
        :type naParcele: str
        :type zpusobVyuziti: str
        :type lv: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.searchBud(domovniCislo, naParcele, zpusobVyuziti, lv)
        if not ok:
            return

        ids = []
        for i in range(model.rowCount()):
            ids.append(model.value(i, "bud_id"))

        self.pageSeznamBudov(ids)

    def pageSearchJednotky(self, cisloJednotky, domovniCislo, naParcele, zpusobVyuziti, lv):
        """

        :type cisloJednotky: str
        :type domovniCislo: str
        :type naParcele: str
        :type zpusobVyuziti: str
        :type lv: str
        :return:
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.searchJed(
            cisloJednotky, domovniCislo, naParcele, zpusobVyuziti, lv)
        if not ok:
            iface.messageBar().pushWarning('ERROR',
                "Nemohu najit dane jednotky, nekde se stala nejaka chyba"
            )
            return

        ids = []
        for i in range(model.rowCount()):
            ids.append(model.value(i, "jed_id"))

        self.pageSeznamJednotek(ids)

    def pageHelp(self):
        self.__mDocument.heading1("VFK plugin")
        self.__mDocument.paragraph(
            "VFK plugin slouží pro usnadnění práce s českými katastrálními daty ve formátu VFK.")
        self.__mDocument.heading2("Kde začít?")

        link = self.__mDocument.link(
            "switchPanel?panel=import", "Importujte")
        text = "{} data ve formátu VFK, nebo již připravenou databázi SQLite s daty katastru nemovitostí. " \
               "Během importu se vytváří databáze, tato operace může chvíli trvat. ".format(
            link)
        text += "Následně lze vyhledávat:"
        self.__mDocument.paragraph(text)

        self.__mDocument.beginItemize()      
        link = self.__mDocument.link(
            "switchPanel?panel=search&type=0", "oprávněné osoby")
        text = "{} (tato možnost je momentálně nedostupná)".format(link)
        self.__mDocument.item(text)
        link = self.__mDocument.link(
            "switchPanel?panel=search&type=1", "parcely")
        self.__mDocument.item(link)
        link = self.__mDocument.link(
            "switchPanel?panel=search&type=2", "budovy")
        self.__mDocument.item(link)
        link = self.__mDocument.link(
            "switchPanel?panel=search&type=3", "jednotky")
        self.__mDocument.item(link)
        self.__mDocument.endItemize()

        text = "Vyhledávat lze na základě různých kritérií. " \
            "Není-li kritérium zadáno, vyhledány jsou všechny nemovitosti či osoby obsažené v databázi. " \
            "Výsledky hledání jsou pak vždy zobrazeny v tomto okně."
        self.__mDocument.paragraph(text)

        text = "Výsledky hledání obsahují odkazy na další informace, " \
            "kliknutím na odkaz si tyto informace zobrazíte, " \
            "stejně jako je tomu u webového prohlížeče. " \
            "Pro procházení historie použijte tlačítka Zpět a Vpřed v panelu nástrojů nad tímto oknem."
        self.__mDocument.paragraph(text)

        self.__mDocument.heading2("Aplikace změn")

        link = self.__mDocument.link(
            "switchPanel?panel=changes", "aplikaci změn")

        text = "Změny je možné aplikovat v panelu pro {}. Pro aplikování změn na stavová data je potřeba zadat " \
               "cestu k databázi se stavovými daty, k databázi se změnovými daty a nakonec cestu/jméno " \
               "pro výstupní databázi.".format(link)
        self.__mDocument.paragraph(text)

    def makeShortDescription(self, id, nemovitost):
        """

        :type id: str
        :type nemovitost: VfkTableModel.OpravnenyPovinny
        :return: str
        """
        text = ''
        if not id:
            return text

        model = VfkTableModel(self.__mConnectionName)
        if nemovitost == VfkTableModel.OpravnenyPovinny.OPParcela:
            model.parcela(id, False)
            text = "Parcela: "
            text += self.makeParcelniCislo(model, 0)
        elif nemovitost == VfkTableModel.OpravnenyPovinny.OPBudova:
            model.budova(id, False)
            text = "Budova: {}".format(self.makeDomovniCislo(model, 0))
        elif nemovitost == VfkTableModel.OpravnenyPovinny.OPJednotka:
            model.jednotka(id, False)
            text = "Jednotka: {}".format(self.makeJednotka(model, 0))
        elif nemovitost == VfkTableModel.OpravnenyPovinny.OPOsoba:
            model.opravnenySubjekt(id, True)
            if model.value(0, "opsub_opsub_type") == "BSM":
                text = "{}".format(self.makeJmeno(model, 0))
            else:
                text = "{}, {}, RČ/IČO: {}".format(self.makeJmeno(model, 0), self.makeAdresa(model, 0),
                                                    self.makeIdentifikator(model, 0))
        else:
            pass

        return text

    def makeLongDescription(self, id, nemovitost):
        """

        :type id: str
        :type nemovitost: VfkTableModel.OpravnenyPovinny
        :return: str
        """
        text = ''
        if not id:
            return text

        model = VfkTableModel(self.__mConnectionName)

        if nemovitost == VfkTableModel.OpravnenyPovinny.OPParcela:
            model.parcela(id, False)
            text = "Parcela "
            text += self.makeParcelniCislo(model, 0)
            text += ", LV {}".format(self.makeLVCislo(model, 0))
        elif nemovitost == VfkTableModel.OpravnenyPovinny.OPBudova:
            model.budova(id, False)
            text = "Budova: {}".format(self.makeDomovniCislo(model, 0))
            text += " na parcele {}".format(self.makeParcelniCislo(model, 0))
            text += ", LV {}".format(self.makeLVCislo(model, 0))
        elif nemovitost == VfkTableModel.OpravnenyPovinny.OPJednotka:
            model.jednotka(id, True)
            text = "Jednotka: ".format(self.makeJednotka(model, 0))
            text += " v budově  {}".format(self.makeDomovniCislo(model, 0))
            text += " na parcele {}".format(self.makeParcelniCislo(model, 0))
            text += ", LV {}".format(self.makeLVCislo(model, 0))
        elif nemovitost == VfkTableModel.OpravnenyPovinny.OPOsoba:
            text += self.makeShortDescription(id, nemovitost)
        else:
            pass

        return text

    def makeAdresa(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        cislo_domovni = model.value(row, "opsub_cislo_domovni")
        cislo_orientacni = model.value(row, "opsub_cislo_orientacni")
        ulice = model.value(row, "opsub_nazev_ulice")
        cast_obce = model.value(row, "opsub_cast_obce")
        obec = model.value(row, "opsub_obec")
        mestska_cast = model.value(row, "opsub_mestska_cast")
        psc = model.value(row, "opsub_psc")

        cislo = cislo_domovni
        if cislo_orientacni:
            cislo += "/" + cislo_orientacni

        adresa = []
        if not ulice:
            adresa.append(obec)
            if cislo:
                adresa.append(cislo)
            if cast_obce:
                adresa.append(cast_obce)
        else:
            adresa.append(ulice)
            if cislo:
                adresa.append(cislo)
            if not cast_obce:
                if mestska_cast:
                    adresa.append(mestska_cast)
                else:
                    adresa.append(cast_obce)
            adresa.append(obec)

        if psc:
            adresa.append(psc)
        return ", ".join(adresa)

    def makeJmeno(self, model, row, hyperlink=True):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        jmeno = ''
        if model.value(row, "opsub_opsub_type") == "OFO":
            jmeno += model.value(row, "opsub_titul_pred_jmenem") + " "
            jmeno += model.value(row, "opsub_prijmeni") + " "
            jmeno += model.value(row, "opsub_jmeno") + " "
            jmeno += model.value(row, "opsub_titul_za_jmenem")
        else:
            jmeno += model.value(row, "opsub_nazev")
        jmeno = jmeno.strip()

        if hyperlink:
            return self.__mDocument.link("showText?page=opsub&id={}".format(model.value(row, "opsub_id")), jmeno)
        return jmeno

    def makeIdentifikator(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        type = model.value(row, "opsub_opsub_type")
        identifikator = ''
        if type == "OPO":
            identifikator = model.value(row, "opsub_ico")
        elif type == "OFO":
            identifikator = model.value(row, "opsub_rodne_cislo")

        return identifikator

    def makeParcelniCislo(self, model, row):
        """

        :param model: VfkTableModel
        :param row: int
        :return: str
        """
        cislo = ''
        cislo += model.value(row, "par_kmenove_cislo_par")
        poddeleni = model.value(row, "par_poddeleni_cisla_par")
        if poddeleni:
            cislo += "/" + poddeleni

        st = ''
        if not model.value(row, "drupoz_stavebni_parcela"):
            iface.messageBar().pushWarning('ERROR',
                "Neni k dispozici tabulka drupoz_stavebni_parcela"
            )
        if self.__mDveRadyCislovani and Domains.anoNe(model.value(row, "drupoz_stavebni_parcela")):
            st = "st."

        link = self.__mDocument.link(
            "showText?page=par&id={}".format(model.value(row, "par_id")), cislo)
        return "{} {}".format(st, link)

    def makeDomovniCislo(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        return self.__mDocument.link(
            "showText?page=bud&id={}".format(model.value(row, "bud_id")),
                                     "{} {}".format(model.value(row, "typbud_zkratka"),
                                                     model.value(row, "bud_cislo_domovni")))

    def makeJednotka(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        return self.__mDocument.link(
            "showText?page=jed&id={}".format(model.value(row, "jed_id")),
                                     "{}/{}".format(model.value(row, "bud_cislo_domovni"),
                                                     model.value(row, "jed_cislo_jednotky")))

    def makeListina(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        return "Listina: {} {}".format(model.value(row, "typlis_nazev"), model.value(row, "dul_nazev"))

    def makeLVCislo(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        return self.__mDocument.link(
            "showText?page=tel&id={}".format(model.value(row, "tel_id")),
                                     model.value(row, "tel_cislo_tel"))

    def makeKatastrUzemi(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        return "{} {}".format(model.value(row, "katuze_nazev"), model.value(row, "par_katuze_kod"))

    def makeCastObce(self, model, row):
        """

        :type model: VfkTableModel
        :type row: int
        :return: str
        """
        return "{} {}".format(model.value(row, "casobc_nazev"), model.value(row, "casobc_kod"))

    def makeObec(self, model, row):
        """

        :param model: VfkTableModel
        :param row: int
        :return: str
        """
        return "{} {}".format(model.value(row, "obce_nazev"), model.value(row, "obce_kod"))

    def saveDefinitionPoint(self, id, nemovitost):
        """

        :param id: str
        :param nemovitost: VfkTableModel.Nemovitost
        """
        model = VfkTableModel(self.__mConnectionName)
        ok = model.definicniBod(id, nemovitost)
        if not ok:
            return
        self.__mCurrentDefinitionPoint.first = model.value(
            0, "obdebo_souradnice_x")
        self.__mCurrentDefinitionPoint.second = model.value(
            0, "obdebo_souradnice_y")
