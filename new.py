#!/usr/bin/env python3

import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication

import linecodes

Ui_New, _ = uic.loadUiType("new.ui")

class LineCodeProperties:

    def __init__(self, code_function, min_bits, initial_condition, channels):
        self._code_function = code_function
        self._min_bits = min_bits
        self._init_cond = initial_condition
        self._channels = channels

    @property
    def code_function(self):
        return self._code_function

    @property
    def min_bits(self):
        return self._min_bits

    @property
    def initial_condition(self):
        return self._init_cond

    @property
    def channels(self):
        return self._channels

class New(QDialog, Ui_New):

    def __init__(self, parent=None):

        QDialog.__init__(self, parent = parent)
        Ui_New.__init__(self)
        self.setupUi(self)
        self.p_wind = parent

        self.comboBox_2.clear()
        L = LineCodeProperties
        self.linecodes = {"Select" : L((),0,(),0),
                        "Unipolar NRZ" : L(linecodes.generate_nrz_unipolar,1,(),1),
                        "Polar NRZ-L" : L(linecodes.generate_nrz_polar_l,1,(),1),
                        "Polar NRZ-I" : L(linecodes.generate_nrz_polar_i,1,("Low Level","High Level"),1),
                        "RZ Polar" : L(linecodes.generate_rz,1,(),1),
                        "Manchester" : L(linecodes.generate_manchester,1,(),1),
                        "Diferential Manchester" : L(linecodes.generate_machester_differential,1,("Low Level","High Level"),1),
                        "AMI" : L(linecodes.generate_ami,1,("Low Level","High Level"),1),
                        "Peseudoternary" : L(linecodes.generate_pseudoternary,1,("Low Level","High Level"),1),
                        "2B1Q" : L(linecodes.generate_2b1q,1,(),1),
                        "MLT-3" : L(linecodes.generate_mlt3,1,("Bit 1","Bit 0+", "Bit 0-", "Bit -1"),1)}
        for code in self.linecodes:
            self.comboBox_2.addItem(code)
        self.comboBox.clear()
        self.comboBox.addItem("")
        self.comboBox.setEnabled(False)
        self.spinBox.clear()
        self.spinBox.setEnabled(False)

        self.coding = None
        self.initial_condition = None
        self.offset = 0
        self.min_bits = 0
        self.channels = 0

        self.comboBox_2.currentIndexChanged.connect(self.update)
        self.buttonBox.accepted.connect(self.ok)
        self.buttonBox.rejected.connect(self.close)

    def update(self):

        prop = self.linecodes[self.comboBox_2.itemText(self.comboBox_2.currentIndex())]
        options = prop.initial_condition
        self.comboBox.clear()
        if not options:
            self.comboBox.setEnabled(False)
        else:
            self.comboBox.setEnabled(True)
            for string in options:
                self.comboBox.addItem(string)

        self.spinBox.clear()
        if self.comboBox_2.currentIndex() is 0:
            self.spinBox.setEnabled(False)
        else:
            self.spinBox.setEnabled(True)
            self.spinBox.setValue(0)

    def ok(self):

        if self.comboBox_2.currentIndex() is 0:

            return
        prop = self.linecodes[self.comboBox_2.itemText(self.comboBox_2.currentIndex())]
        self.coding = prop.code_function
        self.initial_condition = self.comboBox.currentIndex()
        self.offset = self.spinBox.value()
        self.min_bits = prop.min_bits
        self.channels = prop.channels
        self.p_wind.codingInformation(self.coding,self.initial_condition,self.min_bits,self.offset,self.channels)
        self.close()

def __runfile__():

    app = QApplication(sys.argv)

    main = New()
    main.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    __runfile__()
