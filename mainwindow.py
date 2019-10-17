#!/usr/bin/env python3

import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtCore import QTimer, QFile, QTextStream

from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from new import New

import linecodes

Ui_MainWindow, _ = uic.loadUiType("mainwindow.ui")

class MainWindow(QMainWindow, Ui_MainWindow):

    class DataSets:

        def __init__(self, sets):

            self.data = [([], []) for it in range(sets)]

        def set(self, x, y, n = 0):

            self.data[n] = x, y

        def get(self, n = 0):

            return self.data[n]

    def __init__(self, parent = None):

        QMainWindow.__init__(self, parent = parent)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.timer = QTimer(self)
        self.current_file = None
        self.is_modified = False
        self.updated = True
        self.line_coding = None
        self.initial_condition = None
        self.min_bits = 1
        self.offset = 0
        self.channels = 1

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        #self.toolbar = NavigationToolbar(self.canvas, self)
        self.mainLayout.addWidget(self.canvas)
        #self.mainLayout.addWidget(self.toolbar)
        self.clock_graph = None
        self.input_graph = None
        self.output_graph = None
        self.new_window = New(self)

        self.createConections()

        self.label_2.hide()
        self.horizontalScrollBar.hide()

        self.timer.setInterval(150)
        self.timer.start()

    def createConections(self):

        self.timer.timeout.connect(self.update)
        self.lineEdit.textChanged.connect(self.requestUpdate)
        self.actionNew.triggered.connect(self.new)
        self.actionOpen.triggered.connect(self.open)
        self.actionSave_As.triggered.connect(self.saveAs)
        self.actionSave.triggered.connect(self.save)
        self.actionShow_Input.triggered.connect(self.requestUpdate)
        self.actionShow_Clock.triggered.connect(self.requestUpdate)
        self.actionShow_Vertical_Grid.triggered.connect(self.requestUpdate)
        self.actionShow_Horizontal_Grid.triggered.connect(self.requestUpdate)
        self.actionShow_Top_Spine.triggered.connect(self.requestUpdate)
        self.actionShow_Right_Spine.triggered.connect(self.requestUpdate)
        self.checkBox.stateChanged.connect(self.requestUpdate)
        self.radioButton.clicked.connect(self.requestUpdate)
        self.radioButton_2.clicked.connect(self.requestUpdate)
        self.radioButton_3.clicked.connect(self.requestUpdate)
        self.horizontalScrollBar.valueChanged.connect(self.requestUpdate)

    def requestUpdate(self):

        self.updated = True

    def readInput(self):

        input = self.lineEdit.text()
        print(input)

        if not input:
            self.canvas.draw()
            #self.hexLabel.setText('-')
            #self.binLabel.setText('-')
            return None

        if self.radioButton_3.isChecked():

            binary = input

            if len(binary) > 2:
                if binary[0] == '0' and (binary[1] == 'b' or binary[1] == 'B'):
                    binary = binary[2:]

            hex_ = self._bin_to_hex(binary)

            if hex_ is None:
                self.canvas.draw()
                #self.hexLabel.setText('-')
                #self.binLabel.setText('Binário Invalido')
                return None

        else:

            if self.radioButton_2.isChecked():
                hex_ = input
            else:
                hex_ = self._word_to_hex(input)

            if len(hex_) > 2:
                if hex_[0] == '0' and (hex_[1] == 'x' or hex_[1] == 'X'):
                    hex_ = hex_[2:]

            binary = self._hex_to_binary(hex_)

            if binary is None:
                self.canvas.draw()
                #self.hexLabel.setText('Hexadecimal Invalido')
                #self.binLabel.setText('-')
                return None

        #self.hexLabel.setText('0x' + hex_)
        #self.binLabel.setText('0b' + binary)

        return binary

    def update(self):

        if not self.updated:
            return

        self.figure.clear()

        input = self.readInput()
        if input is None:
            self.canvas.draw()
            return
        print(input)

        input_data = MainWindow.DataSets(1)
        clock_data = MainWindow.DataSets(1)
        #
        output_data = MainWindow.DataSets(1)

        input = [int(i) for i in input]
        tmp = y = [input[0]] + input
        x = [i for i in range(len(tmp))]
        input_data.set(x,y)
        y = [i%2 for i in range(2*len(tmp)-1)]
        x = [i/2 for i in range(2*len(tmp)-1)]
        clock_data.set(x,y)
        output = False
        if self.line_coding is not None:
            y = self.line_coding(input,self.initial_condition)
            y = [y[0]] + y
            x = [i for i in range(len(y))]
            output_data.set(x,y)
            output = True

        n = 1
        n = n + int(self.actionShow_Input.isChecked())
        n = n + int(self.actionShow_Clock.isChecked())
        self.figure.subplots_adjust(hspace=0.8, left=0.05, right=0.95)

        if self.actionShow_Clock.isChecked():
            self.clock_graph = self.figure.add_subplot(n, 1, 1)
            self.updateData(self.clock_graph, clock_data)
            self.clock_graph.set_title("clock")

        if self.actionShow_Input.isChecked():
            self.input_graph = self.figure.add_subplot(n, 1, n - 1)
            self.updateData(self.input_graph, input_data)
            self.input_graph.set_title("input")

        if output is True:
            self.output_graph = self.figure.add_subplot(n, 1, n)
            self.updateData(self.output_graph, output_data)
            self.output_graph.set_title("output")
            self.canvas.draw()

        self.updated = False

    def updateData(self, graph, data):

        if graph is None:
            return

        x, y = data.get(0)
        if len(x) is 0:
            return
        graph.step(x,y)

        x, y = data.get(0)
        start = -x[-1]/20
        end = 21*x[-1]/20

        graph.yaxis.set_major_locator(MaxNLocator(integer=True))
        graph.xaxis.set_major_locator(MaxNLocator(integer=True))


        graph.xaxis.grid(self.actionShow_Vertical_Grid.isChecked())
        graph.yaxis.grid(self.actionShow_Horizontal_Grid.isChecked())

        graph.spines['right'].set_visible(self.actionShow_Right_Spine.isChecked())
        graph.spines['top'].set_visible(self.actionShow_Top_Spine.isChecked())
        #graph.xaxis.set_ticks_position('bottom')
        #graph.yaxis.set_ticks_position('left')

        if self.checkBox.isChecked() is True:
            value = (x[-1] - 19*(8)/20) * \
                self.horizontalScrollBar.value()/99
            start = value - (8)/20
            end = start + 21*(8)/20
            self.label_2.show()
            self.horizontalScrollBar.show()
        else:
            self.label_2.hide()
            self.horizontalScrollBar.hide()

        first = y[0]
        for val in y:
            if val != first:
                break
        else:
            if first == 0:
                graph.axis([start, end, -0.24, 1.24])
            else:
                graph.axis([start, end, min(0, first) - 0.2*abs(first) - 0.04,
                             max(0, first) + 0.2*abs(first) + 0.04])
            return
        diff = max(y) - min(y)
        graph.axis([start, end, min(y) - 0.2*diff - 0.04, max(y) + 0.2*diff + 0.04])
        return

    def codingInformation(self, linecode, initial_condition, min_bits, offset, channel):

        self.line_coding = linecode
        self.initial_condition = initial_condition
        self.min_bits = min_bits
        self.offset = offset
        self.channels = channel
        self.requestUpdate()

    def new(self):

        self.new_window.show()

    def open(self):

        if self.maybeSave():
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_name, _ = QFileDialog.getOpenFileName(self,
                                "QFileDialog.getOpenFileName()",
                                "",
                                "All Files (*);;Python Files (*.py)",
                                options = options)

            if file_name:
                self.loadFile(file_name)

    def maybeSave(self):

        if not self.is_modified:
            return True

        ret_val = QMessageBox.warning(self,
                        "Application",
                        "The file has been modified.\n"
                        "Do you want to save your changes?",
                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if ret_val is QMessageBox.Save:
            return self.save()
        elif ret_val is QMessageBox.Discard:
            return True
        else:
            return False

    def loadFile(self, file_name):

        file = QFile(file_name)
        if not file.open(QFile.ReadOnly):
            QMessageBox.warning(self,
                                "Error Opening File",
                                "Cannot open file '%s'" % file_name)

        input = QTextStream(file)

        self.currentFile(file_name)

    def save(self):

        if self.current_file is None:
            return self.saveAs()
        else:
            return self.saveFile(current_file)

    def saveAs(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)

        if file_name:
            self.saveFile(file_name)
            return True
        return False

    def saveFile(self, file_name):

        file = QFile(file_name)
        if not file.open(QFile.WriteOnly):
            QMessageBox.warning(self,
                                "Error Saving File",
                                "Cannot write file '%s'" % file_name)
            return False

        output = QTextStream(file)

        self.currentFile(file_name)
        return True

    def currentFile(self, file_name):

        self.current_file = file_name
        self.is_modified = False

    def about(self):

        QMessageBox.about(self, "About", "about")

    @staticmethod
    def _hex_to_binary(hex_):

        try:
            values = ""
            for hex_char in hex_:
                values += "{:0=4b}".format(int(hex_char, 16))

        except ValueError:
            return None

        return values

    @staticmethod
    def _bin_to_hex(binary):

        binary = '0'*(len(binary) % 4) + binary
        try:
            hex_ = ""
            for i in range(0, len(binary), 4):
                hex_ += '{:x}'.format(int(binary[i : i + 4], 2))

        except ValueError:
            return None

        return hex_

    @staticmethod
    def _word_to_hex(word):

        values = ''
        for letter in word:
            values += '{:2x}'.format(ord(letter))

        return values

def __runfile__():

    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())

if __name__ == '__main__':

    __runfile__()
