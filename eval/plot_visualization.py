# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plot_visualization.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.lbl_onoff_caption = QtWidgets.QLabel(self.centralwidget)
        self.lbl_onoff_caption.setObjectName("lbl_onoff_caption")
        self.gridLayout.addWidget(self.lbl_onoff_caption, 1, 0, 1, 1)
        self.lbl_list_caption = QtWidgets.QLabel(self.centralwidget)
        self.lbl_list_caption.setObjectName("lbl_list_caption")
        self.gridLayout.addWidget(self.lbl_list_caption, 0, 0, 1, 1)
        self.list_dropdown_box = QtWidgets.QComboBox(self.centralwidget)
        self.list_dropdown_box.setMaxVisibleItems(3)
        self.list_dropdown_box.setObjectName("list_dropdown_box")
        self.gridLayout.addWidget(self.list_dropdown_box, 0, 1, 1, 1)
        self.line_onoff_layout = QtWidgets.QGridLayout()
        self.line_onoff_layout.setObjectName("line_onoff_layout")
        self.check_cvaln = QtWidgets.QCheckBox(self.centralwidget)
        self.check_cvaln.setObjectName("check_cvaln")
        self.line_onoff_layout.addWidget(self.check_cvaln, 0, 0, 1, 1)
        self.check_cvalan = QtWidgets.QCheckBox(self.centralwidget)
        self.check_cvalan.setObjectName("check_cvalan")
        self.line_onoff_layout.addWidget(self.check_cvalan, 1, 0, 1, 1)
        self.check_kfacn = QtWidgets.QCheckBox(self.centralwidget)
        self.check_kfacn.setObjectName("check_kfacn")
        self.line_onoff_layout.addWidget(self.check_kfacn, 0, 1, 1, 1)
        self.check_kfacan = QtWidgets.QCheckBox(self.centralwidget)
        self.check_kfacan.setObjectName("check_kfacan")
        self.line_onoff_layout.addWidget(self.check_kfacan, 1, 1, 1, 1)
        self.gridLayout.addLayout(self.line_onoff_layout, 1, 1, 1, 1)
        self.button_refresh = QtWidgets.QPushButton(self.centralwidget)
        self.button_refresh.setObjectName("button_refresh")
        self.gridLayout.addWidget(self.button_refresh, 3, 0, 1, 1)
        self.graph_scroll_holder = QtWidgets.QScrollArea(self.centralwidget)
        self.graph_scroll_holder.setWidgetResizable(True)
        self.graph_scroll_holder.setObjectName("graph_scroll_holder")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 782, 393))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_3)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.chart_widget = QtChart.QChartView(self.scrollAreaWidgetContents_3)
        self.chart_widget.setObjectName("chart_widget")
        self.gridLayout_3.addWidget(self.chart_widget, 0, 0, 1, 1)
        self.graph_scroll_holder.setWidget(self.scrollAreaWidgetContents_3)
        self.gridLayout.addWidget(self.graph_scroll_holder, 4, 0, 1, 2)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 30))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.lbl_onoff_caption.setText(_translate("MainWindow", "Методы"))
        self.lbl_list_caption.setText(_translate("MainWindow", "Список"))
        self.check_cvaln.setText(_translate("MainWindow", "C-value N+"))
        self.check_cvalan.setText(_translate("MainWindow", "C-value A|N"))
        self.check_kfacn.setText(_translate("MainWindow", "kFactor N+"))
        self.check_kfacan.setText(_translate("MainWindow", "kFactor A|N"))
        self.button_refresh.setText(_translate("MainWindow", "Построить"))

from PyQt5 import QtChart

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

