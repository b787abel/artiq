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
from sipyco.pc_rpc import Client


logger = logging.getLogger(__name__)


class Model(DictSyncModel):
    def __init__(self, init):
        DictSyncModel.__init__(self,
            ["series", "number_left", 'priority'],
            init)

    def sort_key(self, k, v):
        # order by priority, and then by due date and RID
        return (-v["priority"] or 0, k)

    def convert(self, k, v, column):
        if column == 0:
            return v["series"]
        elif column == 1:
            return v["number_left"]
        elif column == 2: 
            return v["priority"]
        else:
            raise ValueError
            
    def clear_all(self):
        self.backing_store.clear()
    
    
    def flags(self, index):
        flags = super().flags(index)
        if index.column() == 2:  # Make the third column editable
            flags |= QtCore.Qt.ItemIsEditable
        return flags
    
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            keys = list(self.backing_store.keys())
            key = keys[index.row()]
            old_row = self.backing_store[key]
            column = index.column()
            print('setData ','key', key, 'column', column)
            print('before update', self.backing_store)
            if column == 2:
                old_row = self.backing_store[key]
                old_row["priority"] = int(value)
                series = old_row["series"]
                self.__delitem__(key)
                self.__setitem__(key, old_row)
            print('after update', self.backing_store)
            schedule = Client("::1", 3251, "master_schedule")
            schedule.change_series_priority(series, int(value))
            schedule.close_rpc()
            return True
        return False

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
        
        # Connect signals for editing start and stop
        self.table.clicked.connect(self.stop_timer_on_edit)
        self.table.setItemDelegate(ItemDelegate(self))
        
        #self.table.dataChanged.connect(self.start_timer)
        
        
    def stop_timer_on_edit(self):
        print('click detected!!!')
        # Stop the timer when editing starts
        print('state', self.table.state())
        #if self.table.state() == QtWidgets.QAbstractItemView.EditingState:
        self.timer.stop()
        print('timer stopped')

    def start_timer(self):
        print('timer started')
        # Restart the timer when editing is finished
        #if self.table.state() != QtWidgets.QAbstractItemView.EditingState:
        self.timer.start(1000)
        
    def on_timeout(self):
        # This method will be called every second
        value = {"series": self.counter, "number_left": self.counter}
        
        schedule = Client("::1", 3251, "master_schedule")
        
        #Get status and series IDs 
        status = schedule.get_status()
        series_dict = {'all_series': [], 
               'number_left': [],
               'priority': []}

        keys = status.keys()
        for key in keys: 
            exp = status[key]
            series = exp['expid']['arguments']['series']
            priority = exp['priority']
            if series not in series_dict['all_series']: 
                series_dict['all_series'].append(series)
                series_dict['number_left'].append(1)
                series_dict['priority'].append(priority)
            else: 
                ind = series_dict['all_series'].index(series)
                series_dict['number_left'][ind]+=1 
                if priority > series_dict['priority'][ind]: 
                    series_dict['priority'][ind] = priority
                    
        # Fill up the table             
        print('callback ', self.table_model.backing_store)
        for i in range(len(series_dict['all_series'])):  
            value = {"series": series_dict['all_series'][i],
                     "number_left": series_dict['number_left'][i],
                     "priority": series_dict['priority'][i]
                     }
            try: 
                self.table_model.__setitem__(value['series'], value)
            except: 
                print('callback cannot set')
        #Go through table and remove unnecessary rows 
        active_series = series_dict['all_series']
        displayed_series = list(self.table_model.backing_store.keys())
        for i in range(len(displayed_series)):
            if displayed_series[i] not in active_series: 
                self.table_model.__delitem__(displayed_series[i])
            
        schedule.close_rpc()

    def set_model(self, model):
        self.table_model = model
        self.table.setModel(self.table_model)


    def save_state(self):
        return bytes(self.table.horizontalHeader().saveState())

    def restore_state(self, state):
        self.table.horizontalHeader().restoreState(QtCore.QByteArray(state))

class ItemDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)
        self.dock_widget = parent

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if index.column() == 2:
            editor.installEventFilter(self)
        return editor

    def eventFilter(self, editor, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                self.commitData.emit(editor)
                self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.NoHint)
                self.dock_widget.start_timer()  # Restart the timer
                return True
        return super(ItemDelegate, self).eventFilter(editor, event)

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        editor.setText(str(value))

    def setModelData(self, editor, model, index):
        value = int(editor.text())
        model.setData(index, value, QtCore.Qt.EditRole)