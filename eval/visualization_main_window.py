from PyQt5 import QtCore, QtGui, QtWidgets
from eval.eval_container import EvalContainer
from eval.vocabulary_lookup import *
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChart
# from eval.demo import Ui_MainWindow
from eval.plot_visualization import Ui_MainWindow


class Prog(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.container = EvalContainer()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_widgets()

    def setup_widgets(self):
        self.ui.list_dropdown_box.addItems(['короткий', 'средний', 'длинный'])
        self.ui.button_refresh.clicked.connect(self.create_plot)

    def create_plot(self):
        list_type_index = self.ui.list_dropdown_box.currentIndex()
        selected_methods = {
            'cvalue_1': self.ui.check_cvaln.isChecked(),
            'cvalue_2': self.ui.check_cvalan.isChecked(),
            'kfactor_1': self.ui.check_kfacn.isChecked(),
            'kfactor_2': self.ui.check_kfacan.isChecked(),
        }
        print('тип списка = {}'.format(list_type_index))
        self.container.run_comparison_evals(selected_methods, list_type_index, self.ui.statusbar)
        self.build_line_series(selected_methods, list_type_index, 500)

    def build_line_series(self, selected_methods: Dict[str, bool], list_type_index: int, length_limit: int):
        if selected_methods['cvalue_1']:
            print("Prvi koraki")
            p_cval_1 = self.container.get_points(self.container.cvalue_1, list_type_index, length_limit)
            chart = QChart()
            chart.legend().hide()
            # self.container.add_data()
            # window.add_data(xdata, np.sin(xdata), color=Qt.red Qt.blue)
            chart.addSeries(p_cval_1)
            chart.createDefaultAxes()
            self.chart_widget.setChart(chart)

            self.scrollAreaGraph.setChart(chart)
            self.scrollAreaGraph.setRenderHint(QPainter.Antialiasing)
            """QChart * chart = new QChart();
            chart->legend()->hide();
            chart->addSeries(series);
            chart->createDefaultAxes();
            chart->setTitle("Simple line chart example");
            """

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Prog()
    # ui = Ui_MainWindow()
    # ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
