import ctypes
import sys
from pynput.mouse import Button, Controller
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QSettings, QEventLoop, QTimer

from global_hotkeys import *

from Ui_FastAutoClicker import Ui_FastAutoClicker


# for taskbar icon
myappid = u'FastAutoClicker'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
# i dont understand it


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.ui = Ui_FastAutoClicker()
        self.ui.setupUi(self)
        self.initUI()  # intilization function

    def initUI(self):
        self.ui.StartBtn.clicked.connect(self.StartBtnFun)
        self.ui.StopBtn.clicked.connect(self.StopBtnFun)
        self.ui.HotkeyBtn.clicked.connect(self.HotkeyBtnFun)
        self.RepeatCounter = 0
        # to make settings file
        self.Settings = QSettings("FastAutoClicker", "FastAutoClicker")
        self.SettingsConfig()  # to apply settings

    def DelayFun(self):
        self.Hours = self.ui.HoursSpinBox.value() * 3600000  # hours to milliseconds
        self.Minutes = self.ui.MinutesSpinBox.value() * 60000  # Minutes to milliseconds
        self.Seconds = self.ui.SecondsSpinBox.value() * 1000  # Seconds to milliseconds
        self.Milliseconds = self.ui.MilliSSpinBox.value()
        self.clickInterval = 10  # add 10 ms to Delay for prefomance
        self.Delay = self.Milliseconds + self.Seconds + \
            self.Minutes + self.Hours + self.clickInterval#Delay time sum

    def StartBtnFun(self):
        self.DelayFun()#gets the delay time
        self.mainfun()  # run the main function

    def StopBtnFun(self):
        self.RepeatCounter = 0  # reset Repat counter

    def mainfun(self):
        Mouse = Controller()
        MouseButton = self.ui.MouseComboBox.currentText().lower()#get mouse button
        button = getattr(Button, MouseButton)
        MouseClick = self.ui.ClickComboBox.currentIndex()+1#get single or double cilck
        while self.ui.StopBtn.isEnabled():
            loop = QEventLoop()  # sleep
            QTimer.singleShot(self.Delay, loop.quit)  # sleep
            loop.exec_()  # sleep

            Mouse.click(button, MouseClick)#the AutoClicker

            if self.ui.RepeatRadioButton.isChecked():  # to check if checked no need to initialize
                self.RepeatCounterFun()  # for RepeatCounter

    def RepeatCounterFun(self):  # Repeat Radio Button Checked function
        self.RepeatCounter += 1  # for each repeat
        if self.RepeatCounter == self.ui.RepeatSpinBox.value():  # To stop
            self.ui.StopBtn.click()  # To stop

    # hotkey detection code
    # change the text for the buttons and sends the hotkey value to listener
    def HotkeyBtnFun(self):
        if self.ui.shortcut_edit.keySequence().isEmpty():  # if keySequenceEdit is empty
            QMessageBox.warning(
                self, "Invalid Shortcut", "Please enter a valid shortcut.")  # error message
        else:  # if keySequenceEdit is not empty
            try:  # try expect for hotkey length and special characters
                self.HotkeySequence = self.ui.shortcut_edit.keySequence().toString().lower()
                self.hotkeyFun()#call the hotkey function to assign
                # change button text to add the hotkey
                self.ui.StartBtn.setText(
                    "Start  ({})".format(self.HotkeySequence.upper()))
                # change button text to add the hotkey
                self.ui.StopBtn.setText(
                    "Stop  ({})".format(self.HotkeySequence.upper()))
                
            # self.shortcut_edit.setEnabled(False)#diable the keySequenceEdit #no need
            except Exception:
                QMessageBox.warning(
                    self, "Invalid Shortcut", "Please enter a valid shortcut.")  # error message

    # for globla hotkey

    def hotkeyFun(self):  # assign the globla hotkey and start listening
        clear_hotkeys()#clear all hotkeys
        self.bindings = [[self.HotkeySequence, self.OnHotkeyClick, None, False]]#get hotkey from HotkeySequence
        register_hotkeys(self.bindings)#register hotkeys
        start_checking_hotkeys()#start listening
            

    # for globla hotkey
    def OnHotkeyClick(self):  # what the hotkey dose when pressed
        if self.ui.StartBtn.isEnabled():  # if app not running
            self.ui.StartBtn.click()  # Click the Start Btn
        elif self.ui.StopBtn.isEnabled():  # if app running
            self.ui.StopBtn.click()  # Click the Stop Btn

    def SettingsConfig(self):  # applies settings at startup
        # move the window position at startup
        try:  # for first start error
            self.move(self.Settings.value("WindowPosition"))
            # set MouseComboBox value at startup
            self.ui.MouseComboBox.setCurrentText(
                self.Settings.value("MouseComboBox"))
            # set ClickComboBox value at startup
            self.ui.ClickComboBox.setCurrentText(
                self.Settings.value("ClickComboBox"))
            # set RepeatSpinBox value at startup
            self.ui.RepeatSpinBox.setValue(
                self.Settings.value("RepeatSpinBox"))
            self.HotkeySequence = (self.Settings.value(
                "HotkeySequence"))  # get the hotkey sequence
            self.ui.shortcut_edit.setKeySequence(
                self.HotkeySequence)  # set Hotkey value at startup
            self.HotkeyBtnFun()  # press save button
        except Exception:
            pass

    def closeEvent(self, event):  # what happend when closing the app
        # save the position of the window
        self.Settings.setValue("WindowPosition", self.pos())
        # save MouseComboBox value
        self.Settings.setValue(
            "MouseComboBox", self.ui.MouseComboBox.currentText())
        # save ClickComboBox value
        self.Settings.setValue(
            "ClickComboBox", self.ui.ClickComboBox.currentText())
        # save RepeatSpinBox value
        self.Settings.setValue("RepeatSpinBox", self.ui.RepeatSpinBox.value())
        try:
            # save HotkeySequence value
            self.Settings.setValue("HotkeySequence", self.HotkeySequence)
        except Exception:
            pass
        self.ui.StopBtn.click()  # stops running in the background
        stop_checking_hotkeys() #Stops the hotkey listening
        event.accept()  # IDK
        super().closeEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
