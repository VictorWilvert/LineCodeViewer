#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

class Graph:

    def __init__(self, line_code, initial_condition = 0):
        self._line_code = line_code
        self._initial_codition = initial_condition
        self._title = ""
        self._x_label = ""
        self._y_label = ""
        self._data = ([], [])
        self._yinterval = (0, 1)

    def setLineCode(self, line_code):
        self._line_code = line_code

    def getLineCode(self):
        return self._line_code

    def setYInterval(self, min_, max_):
        self._yinterval = (min_, max_)

    def getYInterval(self):
        return self._yinterval

    def setInitialCondition(self, initial_condition):
        self._initial_codition = initial_condition

    def getInitialCondition(self):
        return self._initial_codition

    def setTitle(self, title):
        self._title = title

    def getTitle(self):
        return self._title

    def setXLabel(self, x_label):
        self._x_label = x_label

    def getXLabel(self):
        return self._x_label

    def setYLabel(self, y_label):
        self._y_label = y_label

    def getYLabel(self):
        return self._y_label

    def setData(self, data_input):
        if len(data_input) is 0:
            return
        y = self._line_code(data_input, self._initial_codition)
        y = [y[0]] + y
        x = [i for i in range(len(y))]
        self._data = (x, y)

    def getData(self):
        return self._data

class Diagram:

    def __init__(self, label):
        self._label = label
        self._figure = plt.figure()
        self._graph_vector = []
        self._data_input = None
        self._xticks = 2

    def setLabel(self, label):
        self._label = label

    def getLabel(self):
        return self._label

    def addGraph(self, graph):
        self._graph_vector.append(graph)

    def numberOfGraphs(self):
        return len(self._graph_vector)

    def removeGraph(self, index):
        self._graph_vector.erase(index)

    def getGraph(self, index):
        return self._graph_vector[index]

    def setDataInput(self, data_input):
        self._data_input = data_input

    def setXticks(self, value):
        self._xticks = value

    def figure(self):
        return self._figure

    def updateFigure(self):
        if self.numberOfGraphs() is 0:
            return
        self._figure.clear()
        if self._data_input is None or len(self._data_input) is 0:
            return
        # update the figure with new data
        self._figure.subplots_adjust(hspace=0.8, left=0.05, right=0.95)
        for i in range(len(self._graph_vector)):
            self._graph_vector[i].setData(self._data_input)
            graph = self._figure.add_subplot(self.numberOfGraphs(), 1, i+1)
            graph.set_title(self._graph_vector[i].getTitle())
            graph.set_xlabel(self._graph_vector[i].getXLabel())
            graph.set_ylabel(self._graph_vector[i].getYLabel())
            x, y = self._graph_vector[i].getData()
            graph.step(x,y)
            start = -x[-1]/20
            end = 21*x[-1]/20
            graph.yaxis.set_major_locator(MaxNLocator(integer=True))
            graph.xaxis.set_major_locator(MaxNLocator(integer=True))
            #graph.xaxis.set_xticks(np.arange(0,len(x)+1,self._xticks))
            graph.xaxis.grid(True)
            graph.yaxis.grid(True)
            """
            if self.partialVizualizationCheckBox.isChecked() is True:
                value = (x_values[-1] - 19*self.VizualizationSpinBox.value()/20) * \
                    self.horizontalSlider.value()/99
                start = value - self.VizualizationSpinBox.value()/20
                end = start + 21*self.VizualizationSpinBox.value()/20
            """

            y_interval = self._graph_vector[i].getYInterval()
            diff = y_interval[1] - y_interval[0]
            graph.axis([start, end, y_interval[0] - 0.2*diff - 0.04,
                        y_interval[1] + 0.2*diff + 0.04])
