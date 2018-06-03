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


import traceback
import sys
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtCore import QSettings
from qgis.core import Qgis, QgsMessageLog


def log_msg(message, tag='OQ-Consolidate', level='I', message_bar=None,
            duration=None, exception=None):
    """
    Add a message to the QGIS message log. If a messageBar is provided,
    the same message will be displayed also in the messageBar. In the latter
    case, warnings and critical messages will have no timeout, whereas
    info messages will have a duration of 5 seconds.

    :param message: the message
    :param tag: the log topic
    :param level:
        the importance level
        'I' -> Qgis.Info,
        'W' -> Qgis.Warning,
        'C' -> Qgis.Critical,
        'S' -> Qgis.Success,
    :param message_bar: a `QgsMessageBar` instance
    :param duration: how long (in seconds) the message will be displayed (use 0
        to keep the message visible indefinitely, or None to use
        the default duration of the chosen level
    :param exception: an optional exception, from which the traceback will be
        extracted and written only in the log
    """
    levels = {
              'I': Qgis.Info,
              'W': Qgis.Warning,
              'C': Qgis.Critical,
              'S': Qgis.Success,
              }
    if level not in levels:
        raise ValueError('Level must be one of %s' % levels.keys())
    tb_text = ''
    if exception is not None:
        tb_lines = traceback.format_exception(
            exception.__class__, exception, exception.__traceback__)
        tb_text = '\n' + ''.join(tb_lines)

    # if we are running nosetests, exit on critical errors
    if 'nose' in sys.modules and level == 'C':
        raise RuntimeError(message)
    else:
        log_verbosity = QSettings().value('oqconsolidate/log_verbosity', 'W')
        if (level == 'C'
                or level == 'W' and log_verbosity in ('S', 'I', 'W')
                or level in ('I', 'S') and log_verbosity in ('I', 'S')):
            QgsMessageLog.logMessage(
                tr(message) + tb_text, tr(tag), levels[level])
        if message_bar is not None:
            if level == 'I':
                title = 'Info'
                duration = duration if duration is not None else 8
            elif level == 'W':
                title = 'Warning'
                duration = duration if duration is not None else 0
            elif level == 'C':
                title = 'Error'
                duration = duration if duration is not None else 0
            elif level == 'S':
                title = 'Success'
                duration = duration if duration is not None else 8
            max_msg_len = 200
            if len(message) > max_msg_len:
                message = ("%s[...] (Please open the Log Messages Panel to"
                           " read the full message)" % message[:max_msg_len])
            message_bar.pushMessage(tr(title),
                                    tr(message),
                                    levels[level],
                                    duration)


def tr(message):
    """
    Leverage QApplication.translate to translate a message

    :param message: the message to be translated
    :returns: the return value of
              `QApplication.translate('OQ-Consolidate', message)`
    """
    return QApplication.translate('OQ-Consolidate', message)
