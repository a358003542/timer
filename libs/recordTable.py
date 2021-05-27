#!/usr/bin/env python
# -*-coding:utf-8-*-
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QDialog, QVBoxLayout, QTableWidget, \
    QTableWidgetItem


class RecordTable(QDialog):
    def __init__(self, parent=None, record=None):
        super().__init__()
        self.parent = parent
        if record is None:
            record = []
        self.setupUi(record)

    def setupUi(self, running_record):
        self.resize(670, 670)
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.table = QTableWidget(self)
        mainLayout.addWidget(self.table)

        row_count = len(running_record)
        if row_count < 3:
            row_count = 3
        self.table.setRowCount(row_count)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ['task_name', 'start_time', 'last_time', 'end_time', 'status'])

        head_font = QFont('微软雅黑', 11)
        head_font.setBold(True)
        self.table.horizontalHeader().setFont(head_font)
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 160)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 160)
        self.table.setColumnWidth(4, 90)

        for index, item in enumerate(running_record[::-1]):
            task_name = item.get('task_name', '')
            last_time = item.get('last_time', '')
            status = item.get('status', '')
            start_time = item.get('start_time', '')
            end_time = item.get('end_time', '')

            self.table.setItem(index, 0, QTableWidgetItem(task_name))
            self.table.setItem(index, 1, QTableWidgetItem(start_time))
            self.table.setItem(index, 2, QTableWidgetItem(last_time))
            self.table.setItem(index, 3, QTableWidgetItem(end_time))
            self.table.setItem(index, 4, QTableWidgetItem(status))