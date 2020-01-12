#!/usr/bin/env python3

import sys
import json
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from diagram import Graph, Diagram
import linecode

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
Ui_MainWindow, _ = uic.loadUiType("mainwindow.ui")

class MainWindow(QMainWindow, Ui_MainWindow):

    CODELINE_INFO_DICT = {
        'Differential Manchester': (('Nivel Baixo', 'Nivel Alto'), (0, 1)),
        'AMI': (('Bit 1 Positivo', 'Bit 1 Negativo'), (-1, 1)),
        'MLT-3': (("Bit 1", "Bit 0 Crescendo", "Bit 0 Decrescendo", "Bit -1"),
                  (-1, 1)),
        '2B1Q': ((), (-3, 3))
    }

    def __init__(self, parent=None):
        # setting up window
        QMainWindow.__init__(self, parent=parent)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # initailzaing variables
        self._diagram_index = 0
        self._digrama_update = True
        self._diagram_vector = []
        self._input_vector = []
        self._request_update = False
        self._timer = QTimer(self)
        self.canvas = []
        # setting up tree view
        self.treeView.setModel(QStandardItemModel())
        self.treeView.setUniformRowHeights(True)
        self.treeView.header().hide()
        #
        self.addDiagram("Diagram 0")
        #
        self.formConversion.hide()
        self.formIndividual.hide()
        self.comboBoxLineCode.clear()
        for line_code in linecode.function_vector():
            self.comboBoxLineCode.addItem(line_code)
        #
        self.initConnections()
        #
        self.radioButtonSlot()
        #
        self._timer.setInterval(50)
        self._timer.start()
        self._request_update = True
        self._modifying = False

    def requestUpdate(self):
        self._request_update = True
        self._modifying = True

    def update(self):
        #
        if self._request_update is False:
            return

        if self._modifying is True:
            self._modifying = False
            return
        #
        data = self.readInput()
        self._diagram_vector[self._diagram_index].setDataInput(data)
        self._diagram_vector[self._diagram_index].updateFigure()
        #
        if self._digrama_update is True:
            for i in reversed(range(self.gridGraphics.count())):
                self.gridGraphics.removeWidget(self.gridGraphics.itemAt(i).widget())
            self.canvas[self._diagram_index] = FigureCanvas(
                self._diagram_vector[self._diagram_index].figure())
            self.gridGraphics.addWidget(self.canvas[self._diagram_index])
            self._digrama_update = False
        #
        self.canvas[self._diagram_index].draw()
        self._request_update = False

    def readInput(self):
        #
        text = self.lineEditInput.text()
        self._input_vector[self._diagram_index] = text
        data_bin = None
        data_hex = None
        data_txt = None
        #
        if text is None:
            self.lineEditBinary.setText('')
            self.lineEditHexadecimal.setText('')
            self.lineEditText.setText('')
            self._request_update = True
            return None

        if self.radioButtonBinary.isChecked():
            data_bin = text
            if len(data_bin) > 2:
                if data_bin[0] == '0' and (data_bin[1] == 'b' or data_bin[1] == 'B'):
                    data_bin = data_bin[2:]
            data_hex = self.binToHex(data_bin)
            data_txt = self.hexToTxt(data_hex)
        elif self.radioButtonHexadecimal.isChecked():
            data_hex = text
            if len(data_hex) > 2:
                if data_hex[0] == '0' and (data_hex[1] == 'x' or data_hex[1] == 'X'):
                    data_hex = data_hex[2:]
            data_bin = self.hexToBin(data_hex)
            data_txt = self.hexToTxt(data_hex)
        else:
            data_txt = text
            data_hex = self.txtToHex(data_txt)
            data_bin = self.hexToBin(data_hex)
        #
        if data_bin is None or data_hex is None or data_txt is None:
            self.lineEditBinary.setText('')
            self.lineEditHexadecimal.setText('')
            self.lineEditText.setText('')
            return
        self.lineEditBinary.setText(data_bin)
        self.lineEditHexadecimal.setText(data_hex)
        self.lineEditText.setText(data_txt)
        #
        return [int(i) for i in data_bin]

    def addGraph(self, line_code):
        #
        self._diagram_vector[self._diagram_index].addGraph(Graph(linecode.generate_nrz_unipolar))
        row = self.treeView.model().itemFromIndex(self.treeView.model().index(self._diagram_index,0))
        item = QStandardItem(self.comboBoxLineCode.itemText(self.comboBoxLineCode.currentIndex()))
        item.setEditable(False)
        row.appendRow(item)

    def removeGraph(self):
        pass

    def addDiagram(self, label):
        #
        self._diagram_vector.append(Diagram(label))
        self._diagram_index = len(self._diagram_vector)-1
        item = QStandardItem(label)
        item.setEditable(True)
        self.treeView.model().appendRow(item)
        self.canvas.append(FigureCanvas(self._diagram_vector[self._diagram_index].figure()))
        #
        self._input_vector.append("")
        self.lineEditInput.setText(self._input_vector[self._diagram_index])

    def removeDiagram(self):
        pass

    def initConnections(self):
        #
        self.treeView.clicked.connect(self.treeViewSlot)
        self.checkBoxInput.stateChanged.connect(self.checkBoxInputSlot)
        self.actionCreateDiagram.triggered.connect(self.actionCreateDiagramSlot)
        self.actionCreateGraph.triggered.connect(self.actionCreateGraphSlot)
        self.actionSave.triggered.connect(self.actionSaveSlot)
        self.lineEditInput.textChanged.connect(self.requestUpdate)
        self.radioButtonBinary.clicked.connect(self.radioButtonSlot)
        self.radioButtonHexadecimal.clicked.connect(self.radioButtonSlot)
        self.radioButtonText.clicked.connect(self.radioButtonSlot)
        self._timer.timeout.connect(self.update)
        self.comboBoxLineCode.currentIndexChanged.connect(self.comboBoxLineCodeSlot)
        self.comboBox.currentIndexChanged.connect(self.comboBoxInitialValueSlot)
        self.lineEditTitle.textChanged.connect(self.lineEditTitleSlot)
        self.lineEditXLabel.textChanged.connect(self.lineEditXLabelSlot)
        self.lineEditYLabel.textChanged.connect(self.lineEditYLabelSlot)
        self.spinBoxBit.valueChanged.connect(self.spinBoxBitSlot)

    def treeViewSlot(self, signal):
        #
        index = self.treeView.currentIndex()
        if self.treeView.model().itemFromIndex(index).parent() is None:
            self.formIndividual.hide()
            self.formPublic.show()
            self._diagram_index = index.row()
            self.lineEditInput.setText(self._input_vector[self._diagram_index])
            self._digrama_update = True
        else:
            self.formIndividual.show()
            self.formPublic.hide()
            item = self.treeView.model().itemFromIndex(index)
            if self.treeView.model().indexFromItem(item.parent()).row() != self._diagram_index:
                self._diagram_index = self.treeView.model().indexFromItem(item.parent()).row()
                self._digrama_update = True
            graph = self._diagram_vector[self._diagram_index].getGraph(index.row())
            index = self.comboBoxLineCode.findText(item.text())
            self.comboBoxLineCode.setCurrentIndex(index)
            self.lineEditTitle.setText(graph.getTitle())
            self.lineEditXLabel.setText(graph.getXLabel())
            self.lineEditYLabel.setText(graph.getYLabel())
            self.comboBox.setCurrentIndex(graph.getInitialCondition())
        self.requestUpdate()

    def checkBoxInputSlot(self):
        #
        if self.checkBoxInput.isChecked():
            self.formConversion.show()
        else:
            self.formConversion.hide()
        self.requestUpdate()

    def actionCreateDiagramSlot(self):
        #
        self.addDiagram("Diagram "+str(len(self._diagram_vector)))
        self._digrama_update = True
        self.requestUpdate()

    def actionCreateGraphSlot(self):
        #
        self.addGraph(None)
        self.requestUpdate()

    def radioButtonSlot(self):
        #
        if self.radioButtonBinary.isChecked():
            self.lineEditBinary.hide()
            self.labelBinary.hide()
            self.lineEditHexadecimal.show()
            self.labelHexadecimal.show()
            self.lineEditText.show()
            self.labelText.show()
        elif self.radioButtonHexadecimal.isChecked():
            self.lineEditBinary.show()
            self.labelBinary.show()
            self.lineEditHexadecimal.hide()
            self.labelHexadecimal.hide()
            self.lineEditText.show()
            self.labelText.show()
        else:
            self.lineEditBinary.show()
            self.labelBinary.show()
            self.lineEditHexadecimal.show()
            self.labelHexadecimal.show()
            self.lineEditText.hide()
            self.labelText.hide()
        self.requestUpdate()

    def comboBoxLineCodeSlot(self):
        #
        index = self.treeView.currentIndex().row()
        graph = self._diagram_vector[self._diagram_index].getGraph(index)
        functions = linecode.function_vector()
        text = self.comboBoxLineCode.itemText(self.comboBoxLineCode.currentIndex())
        self.treeView.model().itemFromIndex(self.treeView.currentIndex()).setText(text)
        graph.setLineCode(functions[text])

        info_t = MainWindow.CODELINE_INFO_DICT.get(
            self.comboBoxLineCode.itemText(self.comboBoxLineCode.currentIndex()))

        self.comboBox.clear()

        graph.setInitialCondition(self.comboBox.currentIndex())

        if info_t is None:
            graph.setYInterval(0, 1)
        else:
            graph.setYInterval(*info_t[1])

        if info_t is None or not info_t[0]:
            self.comboBox.setEnabled(False)
            self.labelInit.setEnabled(False)
        else:
            for cond in info_t[0]:
                self.comboBox.addItem(cond)
            self.comboBox.setEnabled(True)
            self.labelInit.setEnabled(True)

        self.requestUpdate()

    def lineEditTitleSlot(self):
        #
        index = self.treeView.currentIndex().row()
        graph = self._diagram_vector[self._diagram_index].getGraph(index)
        graph.setTitle(self.lineEditTitle.text())
        self.requestUpdate()

    def lineEditXLabelSlot(self):
        #
        index = self.treeView.currentIndex().row()
        graph = self._diagram_vector[self._diagram_index].getGraph(index)
        graph.setXLabel(self.lineEditXLabel.text())
        self.requestUpdate()

    def lineEditYLabelSlot(self):
        #
        index = self.treeView.currentIndex().row()
        graph = self._diagram_vector[self._diagram_index].getGraph(index)
        graph.setYLabel(self.lineEditYLabel.text())
        self.requestUpdate()

    def spinBoxBitSlot(self):
        #
        self._diagram_vector[self._diagram_index].setXticks(
            self.spinBoxBit.value())
        self.requestUpdate()

    def comboBoxInitialValueSlot(self):

        index = self.treeView.currentIndex().row()
        graph = self._diagram_vector[self._diagram_index].getGraph(index)

        graph.setInitialCondition(self.comboBox.currentIndex())

        self.requestUpdate()

    def saveToCSVFile(self, filename):

        index = self.treeView.currentIndex().row()
        graph = self._diagram_vector[self._diagram_index].getGraph(index)

        with open(filename, 'w') as file:
            file.write('x, in_y, out_y\n')
            for x, in_y, out_y in zip(graph.getData()[0], graph.getInputData(),
                                      graph.getData()[1]):
                file.write('{}, {}, {}\n'.format(x, in_y, out_y))

    def saveFigure(self, filename):

        self._diagram_vector[self._diagram_index].figure().savefig(filename)

    def actionSaveSlot(self):

        file_filter = ('CSV files (*.csv);; Image files(*.png *.jpg);; '
                       'PDF files (*.pdf);; JSON files(*.json)')
        fdialog = QFileDialog(None, 'Open File', '', file_filter)

        if fdialog.exec_():
            filename = fdialog.selectedFiles()[0]
        else:
            return

        if filename.endswith('.csv'):
            self.saveToCSVFile(filename)
        elif filename.endswith('.png') or filename.endswith('.jpg') or \
            filename.endswith('.pdf'):

            self.saveFigure(filename)
        elif filename.endswith('.json'):
            linecode_functions = linecode.function_vector()
            with open(filename, 'w') as file:
                diagrams = tuple(diagram.toDict() for diagram in
                                 self._diagram_vector)
                for diagram in diagrams:
                    for graph in diagram['graphs']:
                        graph_linecode_function = graph['linecode-function']
                        del graph['linecode-function']
                        for name, function in linecode_functions.items():
                            if function is graph_linecode_function:
                                break
                        else:
                            name = 'Unipolar NRZ-L'
                        graph['linecode'] = name

                json.dump({'diagrams': diagrams}, file)
        else:
            msg = QMessageBox(QMessageBox.Critical, 'Error',
                              'The format of this file is not supported')
            msg.exec_()

    @staticmethod
    def hexToBin(data_hex):
        #
        try:
            data_bin = ""
            for it in data_hex:
                    data_bin += "{:0=4b}".format(int(it, 16))
        except ValueError:
            return None
        return data_bin

    @staticmethod
    def binToHex(data_bin):
        #
        data_bin = '0'*(len(data_bin)%4)+data_bin
        try:
            data_hex = ""
            for it in range(0, len(data_bin), 4):
                data_hex += '{:x}'.format(int(data_bin[it : it+4], 2))
        except ValueError:
            return None
        return data_hex

    @staticmethod
    def txtToHex(data_txt):
        #
        data_hex = ''
        for it in data_txt:
            data_hex += '{:2x}'.format(ord(it))
        return data_hex

    @staticmethod
    def hexToTxt(data_hex):
        #
        if data_hex is None:
            return None
        if len(data_hex) % 2 == 1:
            data_hex += '0'
        data_txt = ''
        try:
            for it in range(len(data_hex)//2):
                data_txt += chr(int(data_hex[2*it:2*it+2], 16))
        except Exception:
            return None
        return data_txt

def __runfile__():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    __runfile__()
