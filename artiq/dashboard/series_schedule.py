#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 15:51:50 2024

@author: abelberegi
"""

import asyncio
import time
from functools import partial
import logging

from PyQt5 import QtCore, QtWidgets, QtGui

from artiq.gui.models import DictSyncModel
from artiq.tools import elide


logger = logging.getLogger(__name__)


class Model(DictSyncModel):
    def __init__(self, init):
        DictSyncModel.__init__(self,
            ["series", "number_left"],
            init)

    def sort_key(self, k, v):
        # order by priority, and then by due date and RID
        return (-v["series"], v["number_left"] or 0, k)

    def convert(self, k, v, column):
        if column == 0:
            return k
        elif column == 1:
            return v["series"]
        elif column == 2:
            return v["number_left"]
        else:
            raise ValueError
            
    def set_row(self, key, value):
        self.backing_store[key] = value
        self.invalidate()
            
    


class SeriesScheduleDock(QtWidgets.QDockWidget):
    def __init__(self, schedule_ctl, schedule_sub):
        QtWidgets.QDockWidget.__init__(self, "Series Schedule")
        self.setObjectName("Series Schedule")
        self.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable |
                         QtWidgets.QDockWidget.DockWidgetFloatable)

        self.schedule_ctl = schedule_ctl

        self.table = QtWidgets.QTableView()
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self.table.verticalHeader().hide()
        self.setWidget(self.table)

        self.table.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        self.table_model = Model(dict())
        self.table.setModel(self.table_model)
        schedule_sub.add_setmodel_callback(self.set_model)

        cw = QtGui.QFontMetrics(self.font()).averageCharWidth()
        h = self.table.horizontalHeader()
        h.resizeSection(0, 7*cw)
        h.resizeSection(1, 12*cw)
        
        
        # Initialize counter
        self.counter = 0
        
        # Set up a QTimer to call the update method every second
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start(1000)  # 1000 milliseconds = 1 second
        
    def on_timeout(self):
        # This method will be called every second
        self.counter += 1
        key = self.counter
        value = {"series": self.counter, "number_left": self.counter}
        print('table',self.table_model)
        #print('table',dir(self.table_model))
        self.table_model.__setitem__(key, value)
        logger.info(f"Added row {self.counter}")

    def set_model(self, model):
        self.table_model = model
        self.table.setModel(self.table_model)


    def save_state(self):
        return bytes(self.table.horizontalHeader().saveState())

    def restore_state(self, state):
        self.table.horizontalHeader().restoreState(QtCore.QByteArray(state))
