#!/usr/bin/env python3

import time
import sys

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QApplication, QMessageBox, \
    QMenu
from PySide2.QtCore import QTimer, Slot, Signal, QTranslator, QThread, \
    QLocale

from libs.gfun import beep
from libs.json_helper import get_json_value, set_json_value
from libs.datetime_helper import normal_format_now
from libs.id_helper import random_md5
from libs.mainWidget import MainWidget
from libs.pyside2_helper import Loginfo, SystemTrayIcon

from libs.recordTable import RecordTable

VERSION = '1.3.0'

LOG_INTERVAL = 10  # s
RECORD_SAVE_NUM = 1000  # 保存的运行记录
AUTOSAVE_INTERVAL = 60  # s


class Timer(QMainWindow):
    timeout = Signal()

    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.lang = QLocale.system().name()

        self.sound_thread = None
        self.shutdown_job = False
        self.running_log = []
        self.running_task_info = []  # 更完备的任务信息数据
        self.current_count_task_name = ''
        self.current_countdown_task_name = ''

        self.time = 0
        self.timeInterval = 1000  # = 1s

        self.timerUp = QTimer()
        self.timerUp.setInterval(self.timeInterval)
        self.timerUp.timeout.connect(self.updateUptime)

        self.timerDown = QTimer()
        self.timerDown.setInterval(self.timeInterval)
        self.timerDown.timeout.connect(self.updateDowntime)

        self.timerAutoSave = QTimer()
        self.timerAutoSave.setInterval(AUTOSAVE_INTERVAL * 1000)
        self.timerAutoSave.timeout.connect(self.auto_save_running_log)
        self.timerAutoSave.start()

        self.initUi()

        self.timeout.connect(self.beep)

    @Slot()
    def start_count(self):
        if not self.current_count_task_name:
            self.current_count_task_name = f'count_{random_md5(6)}'
            self.add_log(f'start task {self.current_count_task_name}')

            self.upsert_task_info({
                'task_name': self.current_count_task_name,
                'start_time': normal_format_now()
            })

        self.timerUp.start()

    @Slot()
    def start_countdown(self):
        if not self.current_countdown_task_name:
            self.current_countdown_task_name = f'countdown_{random_md5(6)}'

            self.add_log(f'start task {self.current_countdown_task_name}')

            self.upsert_task_info({
                'task_name': self.current_countdown_task_name,
                'start_time': normal_format_now()
            })
        self.timerDown.start()

    def updateUptime(self):
        self.time += 1
        self.set_timer(self.time)

        if self.time % LOG_INTERVAL == 0:
            self.add_log(
                f'{self.current_count_task_name} running... all seem good. '
                f'current time is: {self.format_time_sec(self.time)}'
            )

            self.upsert_task_info({
                'task_name': self.current_count_task_name,
                'current_time': self.format_time_sec(self.time)
            })

    def updateDowntime(self):
        self.time = self.time - 1
        self.set_timer(self.time)

        if self.time % LOG_INTERVAL == 0:
            self.add_log(
                f'{self.current_countdown_task_name} running... all seem good. '
                f'current time is: {self.format_time_sec(self.time)}'
            )

            self.upsert_task_info({
                'task_name': self.current_countdown_task_name,
                'current_time': self.format_time_sec(self.time)
            })

        if self.time <= 0:
            self.add_log(f'{self.current_countdown_task_name} completed.')

            self.upsert_task_info({
                'task_name': self.current_countdown_task_name,
                'status': 'completed',
                'end_time': normal_format_now()
            })

            # 倒计时信号触发后倒计时就应该停止
            self.timerDown.stop()
            self.timeout.emit()

    @Slot()
    def beep(self):
        # make a sound
        self.sound_thread = MakeSoundThread(self)
        self.sound_thread.start()

    @Slot()
    def handle_act_shutdown(self):
        import os
        os.system("shutdown -s -t 60")
        self.shutdown_job = True

    def set_timer(self, time_sec):
        self.time = time_sec
        text_time = self.format_time_sec(self.time)
        self.mywidget.timeViewer.display(text_time)

    def handle_count_reset(self):
        self.time = 0
        self.set_timer(self.time)

        self.timerUp.stop()

        self.current_count_task_name = ''

    def handle_countdown_reset(self):
        self.time = 0
        self.set_timer(self.time)
        self.mywidget.reset_countdown_edit()

        self.timerDown.stop()

        if self.sound_thread:
            self.sound_thread.requestInterruption()
            self.sound_thread = None

        if self.shutdown_job:
            import os
            os.system("shutdown -a")
            self.shutdown_job = False

        self.current_countdown_task_name = ''

    def show_running_log(self):
        loginfo = Loginfo(self, log_info=self.running_log)
        loginfo.exec()

    def show_running_record(self):
        running_record = get_json_value('timer.json', 'running_record')
        recordTable = RecordTable(self, record=running_record)
        recordTable.exec()

    def set_act_beep(self):
        self.timeout.disconnect()
        self.timeout.connect(self.beep)

    def set_act_shutdown(self):
        reply = QMessageBox.question(self, '信息',
                                     self.tr(
                                         'countdown action is shutdown the system, are you sure?'),
                                     QMessageBox.Yes,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.timeout.disconnect()
            self.timeout.connect(self.handle_act_shutdown)
        else:
            pass

    def initUi(self):
        self.setFixedSize(300, 450)
        self.center()
        self.setWindowTitle('timer')
        self.setWindowIcon(QIcon(':/images/myapp.png'))

        menu_control = self.menuBar().addMenu(self.tr('Contorl'))
        act_countDownBeep = menu_control.addAction(
            self.tr('set countdown action is make a beep sound(default)'))
        act_countDownShutdown = menu_control.addAction(
            self.tr('set countdown action is shutdown the system'))
        act_countDownBeep.triggered.connect(self.set_act_beep)
        act_countDownShutdown.triggered.connect(self.set_act_shutdown)
        menu_control.addSeparator()

        act_quit = menu_control.addAction(self.tr('quit'))
        act_quit.triggered.connect(self.menu_exit)

        menu_language = self.menuBar().addMenu(self.tr('Language'))
        act_chinese = menu_language.addAction('中文')
        act_chinese.triggered.connect(self.change_lang_chinese)
        act_english = menu_language.addAction('english')
        act_english.triggered.connect(self.change_lang_english)

        menu_help = self.menuBar().addMenu(self.tr('Help'))
        act_show_running_log = menu_help.addAction(self.tr('running log'))
        act_show_running_record = menu_help.addAction(
            self.tr("running record"))
        act_show_running_log.triggered.connect(self.show_running_log)
        act_show_running_record.triggered.connect(self.show_running_record)

        menu_help.addSeparator()
        act_about = menu_help.addAction(self.tr('about this program'))
        act_about.triggered.connect(self.about)
        act_aboutqt = menu_help.addAction('aboutqt')
        act_aboutqt.triggered.connect(QApplication.instance().aboutQt)

        self.mywidget = MainWidget(self)
        self.setCentralWidget(self.mywidget)

        self.mysystemTrayIcon = SystemTrayIcon(self, icon=":/images/myapp.png")
        menu1 = QMenu(self)
        menu_systemTrayIcon_open = menu1.addAction(self.tr('open'))
        menu_systemTrayIcon_open.triggered.connect(self.reopen)
        menu1.addSeparator()
        menu_systemTrayIcon_exit = menu1.addAction(self.tr("exit"))
        menu_systemTrayIcon_exit.triggered.connect(self.menu_exit)
        self.mysystemTrayIcon.setContextMenu(menu1)
        self.mysystemTrayIcon.show()

        # 状态栏
        self.statusBar().showMessage(self.tr('program is ready...'))
        self.statusBar().setSizeGripEnabled(False)

        self.show()

    def add_log(self, info):
        self.running_log.append(f'{normal_format_now()}: {info}')

    @Slot()
    def auto_save_running_log(self):
        """
        自动保存运行日志
        :return:
        """
        running_record = get_json_value('timer.json', 'running_record')
        if not running_record:
            running_record = []

        all_record = running_record.copy()

        for item_index, item in enumerate(self.running_task_info):
            self.upsert_task_info(item, target=all_record)

        if len(all_record) > RECORD_SAVE_NUM:
            all_record = all_record[-RECORD_SAVE_NUM:]

        set_json_value('timer.json', 'running_record', all_record)

    def upsert_task_info(self, task_info, target=None):
        if target is None:
            target = self.running_task_info
        task_name = task_info['task_name']
        for index, task_info_item in enumerate(target):
            if task_name == task_info_item['task_name']:
                target[index] = {**task_info_item, **task_info}
                break
        else:
            target.append(task_info)

    def format_time_sec(self, time_sec):
        """
        input time in second output time like that format 00:00:00

        :param time_sec:
        :return:
        """
        time_data = time.gmtime(time_sec)
        hour = time_data.tm_hour
        minute = time_data.tm_min
        second = time_data.tm_sec

        text_time = f'{hour:0>2}:{minute:0>2}:{second:0>2}'
        return text_time

    def menu_exit(self):
        reply = QMessageBox.question(self, '信息',
                                     self.tr('are you sure to quit?'),
                                     QMessageBox.Yes,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.add_log('program quit normally...')
            self.app.exit()
        else:
            # 如果主窗口不显示qt事件循环会终止
            self.showMinimized()

    def reopen(self):
        self.show()

    def retranslateUi(self):
        self.mywidget.buttonStart.setText(self.tr("start"))
        self.mywidget.buttonPause.setText(self.tr("pause"))
        self.mywidget.buttonReset.setText(self.tr("reset"))
        self.mywidget.buttonCountDown.setText(self.tr("countdown"))
        self.mywidget.buttonCountDownPause.setText(self.tr('countdown pause'))

    def change_lang_chinese(self):
        self.app.removeTranslator(default_translator)
        translator = QTranslator()
        translator.load(':/translations/timer_zh_CN')
        self.app.installTranslator(translator)
        self.retranslateUi()
        self.lang = 'zh_CN'

    def change_lang_english(self):
        self.app.removeTranslator(default_translator)
        translator = QTranslator()
        translator.load('')
        self.app.installTranslator(translator)
        self.retranslateUi()
        self.lang = 'en'

    def closeEvent(self, event):
        if self.mysystemTrayIcon.isVisible():
            QMessageBox.information(self, '信息', self.tr(
                'program is still running background.'))
            self.hide()
            event.ignore()

    def about(self):
        QMessageBox.about(self, self.tr("about this software"), f"""
        a simple timer program {VERSION}
        start 启动计时器
        pause 暂停计时器
        reset 重设计时器
        ---------------------
        countdown 启动倒计时
        countdown pause 倒计时暂停
        countdown stop  倒计时停止(停止报警)""")

    # center method
    def center(self):
        screen = self.app.screens()[0]
        screen_size = screen.size()
        size = self.geometry()
        self.move((screen_size.width() - size.width()) / 2, \
                  (screen_size.height() - size.height()) / 2)


class MakeSoundThread(QThread):
    def run(self):
        while True:
            beep(500, 3)

            self.sleep(10)

            if self.isInterruptionRequested():
                return


if __name__ == '__main__':
    import timer_rc

    app = QApplication(sys.argv)

    # 先自动加载最佳语言方案
    default_translator = QTranslator()
    default_translator.load(f':/translations/timer_{QLocale.system().name()}')
    app.installTranslator(default_translator)

    timer = Timer(app)

    timer.show()
    sys.exit(app.exec_())
