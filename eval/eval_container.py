from eval.vocabulary_lookup import *
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPolygonF
from PyQt5.QtChart import QLineSeries
from PyQt5 import QtWidgets
import os
import random
import numpy as np


class EvalContainer(object):
    def __init__(self):
        self.cvalue_1 = [None, None, None]
        self.cvalue_2 = [None, None, None]
        self.kfactor_1 = [None, None, None]
        self.kfactor_2 = [None, None, None]
        self.prepared_sample = comparison_sample_preparation(load_vocabulary())
        print('Voc Loaded')

    def run_comparison_evals(self, selected_methods: Dict[str, bool], list_type_index: int, status_bar: QtWidgets.QStatusBar):
        file_1 = os.path.join('..', 'result', 'cvalue_noun_plus.txt')
        file_2 = os.path.join('..', 'result', 'cvalue_adj_noun.txt')
        file_3 = os.path.join('..', 'result', 'kfactor_noun_plus.txt')
        file_4 = os.path.join('..', 'result', 'kfactor_adj_noun.txt')

        run_d = {
            'c1': selected_methods['cvalue_1'] and self.cvalue_1[list_type_index] is None,
            'c2': selected_methods['cvalue_2'] and self.cvalue_2[list_type_index] is None,
            'k1': selected_methods['kfactor_1'] and self.kfactor_1[list_type_index] is None,
            'k2': selected_methods['kfactor_2'] and self.kfactor_2[list_type_index] is None
        }

        if not any(run_d.values()):
            status_bar.showMessage('Необходимые данные уже получены, рисуем график')
            return

        # <editor-fold desc="Выбор списков для получения">
        cvalue_1i = {0: list(), 1: list(), 2: list()}  # short/middle/long lists
        cvalue_2i = {0: list(), 1: list(), 2: list()}
        kfactor_1i = {0: list(), 1: list(), 2: list()}
        kfactor_2i = {0: list(), 1: list(), 2: list()}
        if run_d['c1']:
            cvalue_1i[2] = comparison_terms_preparation(open_text_stat(file_1))
        if run_d['c2']:
            cvalue_2i[2] = comparison_terms_preparation(open_text_stat(file_2))
        if run_d['k1']:
            kfactor_1i[2] = comparison_terms_preparation(open_text_stat(file_3))
        if run_d['k2']:
            kfactor_2i[2] = comparison_terms_preparation(open_text_stat(file_4))
        # </editor-fold>

        status_bar.showMessage('Открыты результирующие файлы с терминами')

        random.seed()
        cvalue_1i[0] = [t for i, t in enumerate(cvalue_1i[2]) if i < 100]
        cvalue_2i[0] = [t for i, t in enumerate(cvalue_2i[2]) if i < 100]
        kfactor_1i[0] = select_random_excerpt(kfactor_1i[2], {1: 20, 2: 20, 3: 20, 4: 20, 5: 20})
        kfactor_2i[0] = select_random_excerpt(kfactor_2i[2], {1: 20, 2: 20, 3: 20, 4: 20, 5: 20})
        status_bar.showMessage('Сформированы короткие списки')

        cvalue_1i[1] = [t for t in cvalue_1i[2] if t[2] > 1]
        cvalue_2i[1] = [t for t in cvalue_2i[2] if t[2] > 1]
        kfactor_1i[1] = [t for t in kfactor_1i[2] if t[2] > 1]
        kfactor_2i[1] = [t for t in kfactor_2i[2] if t[2] > 1]
        status_bar.showMessage('Сформированы средние списки')

        text_type_desc = 'короткий' if list_type_index == 0 else 'средний' if list_type_index == 1 else 'длинный'

        if run_d['c1']:
            self.cvalue_1[list_type_index] = calc_full_fuzzy_array(cvalue_1i[list_type_index], self.prepared_sample)
            status_bar.showMessage('Обработан {} список cvalue noun+'.format(text_type_desc))
        if run_d['c2']:
            self.cvalue_2[list_type_index] = calc_full_fuzzy_array(cvalue_2i[list_type_index], self.prepared_sample)
            status_bar.showMessage('Обработан {} список cvalue adj|noun'.format(text_type_desc))
        if run_d['k1']:
            self.kfactor_1[list_type_index] = calc_full_fuzzy_array(kfactor_1i[list_type_index], self.prepared_sample)
            status_bar.showMessage('Обработан {} список kfactor noun+'.format(text_type_desc))
        if run_d['k2']:
            self.kfactor_2[list_type_index] = calc_full_fuzzy_array(kfactor_2i[list_type_index], self.prepared_sample)
            status_bar.showMessage('Обработан {} список kfactor noun+'.format(text_type_desc))
        status_bar.showMessage('Обработка закончена')

    @staticmethod
    def get_points(input_list: List[float], list_type_index: int, length_limit: int=-1) -> QLineSeries:
        """
        Формирует множество точек для графика по данным о списке совпадений терминов
        :param input_list: входной список результатов по одному методу
        :param list_type_index: номер типа списка (короткий/средний/длинный)
        :param length_limit: ограничение по длине результирующего множества
        :return: множество точек List[QPointF]
        """
        length_limit = len(input_list) if length_limit == -1 else length_limit
        result = [QPointF(n, sim) for n, sim in enumerate(input_list) if n <= length_limit]
        conv_result = QLineSeries()
        for r in result:
            conv_result.append(r)
        return conv_result

    @staticmethod
    def series_to_polyline(xdata, ydata):
        """
        Convert series data to QPolygon(F) polyline
        :param xdata:
        :param ydata:
        :return:
        """
        size = len(xdata)
        polyline = QPolygonF(size)
        pointer = polyline.data()
        dtype, tinfo = np.float, np.finfo  # integers: = np.int, np.iinfo
        pointer.setsize(2 * polyline.size() * tinfo(dtype).dtype.itemsize)
        memory = np.frombuffer(pointer, dtype)
        memory[:(size - 1) * 2 + 1:2] = xdata
        memory[1:(size - 1) * 2 + 2:2] = ydata
        return polyline

    def add_data(self, xdata, ydata, color=None) -> QLineSeries:
        curve = QLineSeries()
        pen = curve.pen()
        if color is not None:
            pen.setColor(color)
        pen.setWidthF(.1)
        curve.setPen(pen)
        curve.setUseOpenGL(True)
        curve.append(EvalContainer.series_to_polyline(xdata, ydata))
        self.chart.addSeries(curve)
        self.chart.createDefaultAxes()
