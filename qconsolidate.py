# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2017-2018 GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.

# This plugin was forked from https://github.com/alexbruy/qconsolidate
# by Alexander Bruy (alexander.bruy@gmail.com),
# starting from commit 6f27b0b14b925a25c75ea79aea62a0e3d51e30e3.


from builtins import str
from builtins import object
import qgis  # NOQA

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import Qgis

from . import qconsolidatedialog
from . import aboutdialog
from .utils import log_msg, tr

from . import resources_rc  # NOQA


class QConsolidatePlugin(object):
    def __init__(self, iface):
        self.iface = iface

        self.qgsVersion = str(Qgis.QGIS_VERSION_INT)  # FIXME: unicode

    def initGui(self):
        if int(self.qgsVersion) < 20000:
            qgisVersion = (self.qgsVersion[0] + "."
                           + self.qgsVersion[2] + "."
                           + self.qgsVersion[3])
            msg = tr("QGIS %s detected.\n" % qgisVersion)
            msg += tr("This version of OQ-Consolidate requires at least"
                      " QGIS version 3.0.\nPlugin will not be enabled.")
            log_msg(msg, level='C', message_bar=self.iface.messageBar())
            return None

        self.actionRun = QAction(
            QIcon(":/icons/qconsolidate.png"),
            "OQ-Consolidate",
            self.iface.mainWindow())
        self.actionRun.setStatusTip(
            QCoreApplication.translate(
                "OQ-Consolidate",
                ("Consolidates all layers from current"
                 " QGIS project into one directory")))
        self.actionAbout = QAction(
            QIcon(":/icons/about.png"),
            "About OQ-Consolidate",
            self.iface.mainWindow())

        self.actionRun.triggered.connect(self.run)
        self.actionAbout.triggered.connect(self.about)

        self.iface.addPluginToMenu(
            QCoreApplication.translate(
                "OQ-Consolidate", "OQ-Consolidate"), self.actionRun)
        self.iface.addPluginToMenu(
            QCoreApplication.translate(
                "OQ-Consolidate", "OQ-Consolidate"), self.actionAbout)
        self.iface.addToolBarIcon(self.actionRun)

    def unload(self):
        self.iface.removePluginMenu(
            QCoreApplication.translate(
                "OQ-Consolidate", "OQ-Consolidate"), self.actionRun)
        self.iface.removePluginMenu(
            QCoreApplication.translate(
                "OQ-Consolidate", "OQ-Consolidate"), self.actionAbout)
        self.iface.removeToolBarIcon(self.actionRun)

    def run(self):
        self.dlg = qconsolidatedialog.QConsolidateDialog()
        self.dlg.show()

    def about(self):
        dlg = aboutdialog.AboutDialog()
        dlg.exec_()
