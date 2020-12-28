#!/usr/bin/env python
# -*-coding:utf-8-*-

from PySide2.QtCore import Slot
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLCDNumber, QPushButton, \
    QHBoxLayout, QComboBox


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__()
        self.parent = parent

        self.countdown_edit_font = QFont('微软雅黑', 15)

        self.initUI()

        self.buttonStart.clicked.connect(self.parent.start_count)
        self.buttonPause.clicked.connect(self.parent.timerUp.stop)
        self.buttonReset.clicked.connect(self.parent.handle_count_reset)
        self.buttonCountDown.clicked.connect(self.parent.start_countdown)
        self.buttonCountDownPause.clicked.connect(self.parent.timerDown.stop)
        self.buttonCountDownReset.clicked.connect(
            self.parent.handle_countdown_reset)

        self.countdown_edit_hour.currentIndexChanged.connect(
            self.countdown_edit_changed)
        self.countdown_edit_minute.currentIndexChanged.connect(
            self.countdown_edit_changed)
        self.countdown_edit_second.currentIndexChanged.connect(
            self.countdown_edit_changed)

    @Slot()
    def countdown_edit_changed(self, index):
        hour = self.countdown_edit_hour.currentIndex()
        minute = self.countdown_edit_minute.currentIndex()
        second = self.countdown_edit_second.currentIndex()

        time_sec = hour * 60 * 60 + minute * 60 + second

        self.parent.set_timer(time_sec)

    def reset_countdown_edit(self):
        self.countdown_edit_hour.setCurrentIndex(0)
        self.countdown_edit_minute.setCurrentIndex(0)
        self.countdown_edit_second.setCurrentIndex(0)

    def initUI(self):
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.timeViewer = QLCDNumber()
        self.timeViewer.setFixedHeight(45)
        self.timeViewer.setDigitCount(8)  # 00:00:00
        mainLayout.addWidget(self.timeViewer)

        self.buttonStart = QPushButton(self.tr("start"))
        self.buttonStart.setMinimumHeight(35)
        mainLayout.addWidget(self.buttonStart)

        self.buttonPause = QPushButton(self.tr("pause"))
        self.buttonPause.setMinimumHeight(35)
        mainLayout.addWidget(self.buttonPause)

        self.buttonReset = QPushButton(self.tr("reset"))
        self.buttonReset.setMinimumHeight(35)
        mainLayout.addWidget(self.buttonReset)

        mainLayout.addSpacing(10)

        countdown_edit_hlayout = QHBoxLayout()
        self.countdown_edit_hour = QComboBox()
        self.countdown_edit_hour.setMinimumHeight(35)
        self.countdown_edit_hour.setFont(self.countdown_edit_font)
        self.countdown_edit_hour.addItems([f'{i}' for i in range(0, 24)])

        self.countdown_edit_minute = QComboBox()
        self.countdown_edit_minute.setMinimumHeight(35)
        self.countdown_edit_minute.setFont(self.countdown_edit_font)
        self.countdown_edit_minute.addItems([f'{i}' for i in range(0, 60)])

        self.countdown_edit_second = QComboBox()
        self.countdown_edit_second.setMinimumHeight(35)
        self.countdown_edit_second.setFont(self.countdown_edit_font)
        self.countdown_edit_second.addItems([f'{i}' for i in range(0, 60)])

        countdown_edit_hlayout.addWidget(self.countdown_edit_hour)

        countdown_edit_hlayout.addWidget(self.countdown_edit_minute)

        countdown_edit_hlayout.addWidget(self.countdown_edit_second)

        mainLayout.addLayout(countdown_edit_hlayout)

        self.buttonCountDown = QPushButton(self.tr("countdown"))
        self.buttonCountDown.setMinimumHeight(35)
        self.buttonCountDownPause = QPushButton(self.tr("countdown pause"))
        self.buttonCountDownPause.setMinimumHeight(35)
        self.buttonCountDownReset = QPushButton(self.tr("countdown reset"))
        self.buttonCountDownReset.setMinimumHeight(35)

        mainLayout.addWidget(self.buttonCountDown)
        mainLayout.addWidget(self.buttonCountDownPause)
        mainLayout.addWidget(self.buttonCountDownReset)
