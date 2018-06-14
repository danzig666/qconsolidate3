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
import os
import re

from qgis.PyQt.QtCore import (
                              QDir,
                              QFile,
                              QFileInfo,
                              QSettings,
                              )
from qgis.PyQt.QtWidgets import (
                                 QCheckBox,
                                 QComboBox,
                                 QDialog,
                                 QDialogButtonBox,
                                 QFileDialog,
                                 QLabel,
                                 QLineEdit,
                                 QMessageBox,
                                 QPushButton,
                                 QHBoxLayout,
                                 QVBoxLayout,
                                 )

from qgis.core import QgsProject, QgsApplication, QgsTask
from qgis.utils import iface

from .consolidatethread import ConsolidateTask
from .utils import log_msg, tr


class QConsolidateDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.initGui()

        self.consolidateTask = None

        self.btnOk = self.buttonBox.button(QDialogButtonBox.Ok)
        self.btnOk.setEnabled(False)
        self.btnOk.clicked.connect(self.accept)
        self.btnCancel = self.buttonBox.button(QDialogButtonBox.Cancel)
        self.btnCancel.setEnabled(True)
        self.btnCancel.clicked.connect(self.reject)

        self.project_name_le.editingFinished.connect(
            self.on_project_name_editing_finished)
        self.leOutputDir.textChanged.connect(
            self.set_ok_button)

        project_name = self.get_project_name()
        if project_name:
            self.project_name_le.setText(project_name)

        self.btnOk.setEnabled(bool(self.project_name_le.text()) and
                              bool(self.leOutputDir.text()))

        self.btnBrowse.clicked.connect(self.setOutDirectory)

    def initGui(self):
        self.setWindowTitle('QConsolidate3')
        self.project_name_lbl = QLabel('Project name')
        self.project_name_le = QLineEdit()
        self.checkBoxZip = QCheckBox('Consolidate in a Zip file')
        self.cb = QComboBox()
        self.cb.addItems(["SHP", "GeoPackage"])

        self.label = QLabel("Output directory")
        self.leOutputDir = QLineEdit()

        s = QSettings()
        lastdir = s.value("qconsolidate3/lastdir", "")
        self.leOutputDir.setText(lastdir)

        self.btnBrowse = QPushButton("Browse...")
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)

        self.proj_name_hlayout = QHBoxLayout()
        self.proj_name_hlayout.addWidget(self.project_name_lbl)
        self.proj_name_hlayout.addWidget(self.project_name_le)
        self.v_layout.addLayout(self.proj_name_hlayout)

        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.label)
        self.h_layout.addWidget(self.leOutputDir)
        self.h_layout.addWidget(self.btnBrowse)
        self.v_layout.addLayout(self.h_layout)

        self.v_layout.addWidget(self.cb)
        self.v_layout.addWidget(self.checkBoxZip)
        self.v_layout.addWidget(self.buttonBox)

    def on_project_name_editing_finished(self):
        try:
            valid_filename = get_valid_filename(self.project_name_le.text())
        except UnicodeEncodeError:
            self.project_name_le.undo()
        else:
            self.project_name_le.setText(valid_filename)
        self.set_ok_button()

    def get_project_name(self):
        prjfi = QFileInfo(QgsProject.instance().fileName())
        return prjfi.baseName()

    def set_ok_button(self):
        self.btnOk.setEnabled(bool(self.project_name_le.text()) and
                              bool(self.leOutputDir.text()))

    def setOutDirectory(self):
        s = QSettings()
        lastdir = s.value("qconsolidate3/lastdir", ".")
        outDir = QFileDialog.getExistingDirectory(
            self, self.tr("Select output directory"), lastdir)
        if not outDir:
            return

        s.setValue("qconsolidate3/lastdir", outDir)
        self.leOutputDir.setText(outDir)

    def accept(self):
        self.btnOk.setEnabled(False)
        self.btnCancel.setEnabled(False)
        project_name = self.project_name_le.text()
        if project_name.endswith('.qgs'):
            project_name = project_name[:-4]
        if not project_name:
            msg = tr("Please specify the project name")
            log_msg(msg, level='C', message_bar=iface.messageBar())
            self.restoreGui()
            return

        outputDir = self.leOutputDir.text()
        if not outputDir:
            msg = tr("Please specify the output directory.")
            log_msg(msg, level='C', message_bar=iface.messageBar())
            self.restoreGui()
            return
        outputDir = os.path.join(outputDir,
                                 get_valid_filename(project_name))

        # create main directory if not exists
        d = QDir(outputDir)
        if not d.exists():
            if not d.mkpath("."):
                msg = tr("Can't create directory to store the project.")
                log_msg(msg, level='C', message_bar=iface.messageBar())
                self.restoreGui()
                return

        # create directory for layers if not exists
        if d.exists("layers"):
            res = QMessageBox.question(
                self, self.tr("Directory exists"),
                self.tr("Output directory already contains 'layers'"
                        " subdirectory. Maybe this directory was used to"
                        " consolidate another project. Continue?"),
                QMessageBox.Yes | QMessageBox.No)
            if res == QMessageBox.No:
                self.restoreGui()
                return
        else:
            if not d.mkdir("layers"):
                msg = tr("Can't create directory for layers.")
                log_msg(msg, level='C', message_bar=iface.messageBar())
                self.restoreGui()
                return

        # copy project file
        projectFile = QgsProject.instance().fileName()
        try:
            if projectFile:
                f = QFile(projectFile)
                newProjectFile = os.path.join(outputDir,
                                              '%s.qgs' % project_name)
                f.copy(newProjectFile)
            else:
                newProjectFile = os.path.join(
                    outputDir, '%s.qgs' % project_name)
                p = QgsProject.instance()
                p.write(newProjectFile)
        except Exception as exc:
            self.restoreGui()
            log_msg(str(exc), level='C',
                    message_bar=iface.messageBar(),
                    exception=exc)
            return

        # start consolidate task that does all real work
        self.consolidateTask = ConsolidateTask(
            'Consolidation', QgsTask.CanCancel, outputDir, newProjectFile,
            self.checkBoxZip.isChecked(), self.cb.currentText())
        self.consolidateTask.begun.connect(self.on_consolidation_begun)

        QgsApplication.taskManager().addTask(self.consolidateTask)
        super().accept()

    def on_consolidation_begun(self):
        log_msg("Consolidation started.", level='I', duration=4,
                message_bar=iface.messageBar())

    def restoreGui(self):
        self.btnCancel.setEnabled(True)
        self.set_ok_button()


# from https://github.com/django/django/blob/master/django/utils/text.py#L223
def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(s).strip().replace(' ', '_')  # FIXME: str
    return re.sub(r'(?u)[^-\w.]', '', s)
