import math
import logging
import multiprocessing
from collections import namedtuple
from typing import List, Dict
from operator import itemgetter
from ITermExtractor.Structures.WordStructures import Collocation
from itertools import groupby
from helpers import split_tasks
from ITermExtractor.Morph import find_candidate_by_id
from ITermExtractor.Tests.linguistic_filter import is_integral

params = namedtuple('params', ['name', 'cvalue'])
params.__doc__ = "Параметры терминологических подстрок"
params.name.__doc__ = "Слово/Фраза"
params.cvalue.__doc__ = "Величина cvalue"
# <editor-fold desc="# Threshold property setup">
THRESHOLD = 1


def set_threshold(value: float):
    global THRESHOLD
    if isinstance(value, float) or isinstance(value, int):
        THRESHOLD = value if value >= 0 else 0
# </editor-fold>


def calculate(candidates: List[Collocation], is_single_threaded: bool = False) -> List[params]:
    """
    Подсчитывает c-value для списка терминологических кандидатов
    :param is_single_threaded: флаг многопочности - True = выполнять в одном потоке, False - в нескольких
    :param candidates: список терминологических кандидатов  collocation_tuple('словосочетание', 'число слов', 'частота')
    :return: список терминов со значениями c-value
    """

    terms = []
    candidates = sorted(candidates, key=itemgetter('wordcount'), reverse=True)
    grouped_by_len = dict()
    candidate_lengths = []

    for key, value_sitter in groupby(candidates, key=itemgetter('wordcount')):
        grouped_by_len[key] = list(value_sitter)
        candidate_lengths.append(key)

    lengths_info = " ".join(["{1} фраз ({0} сл.)".format(k, len(v)) for k, v in grouped_by_len.items()])
    logging.info("Предварительные операции проведены, всего словосочетаний: {0}: {1}"
                 .format(len(candidates), lengths_info))

    for index, c_group in grouped_by_len.items():
        terms += parallel_conjugation(c_group, candidates, is_single_threaded)
        logging.info("Кандидаты длиной {0} сл. обработаны".format(index))

    logging.info("Подсчет cvalue закончен (терминов: {0}), сортировка и выход".format(len(terms)))
    terms = sorted(terms, key=itemgetter(1), reverse=True)
    return terms


def calculate_by_group(c_group: List[Collocation], candidates: List[Collocation]) -> List[params]:
    """
    Подсчитывает c-value в группе терминологических кандидатов
    :param c_group: малый перечень словосочетаний
    :param candidates: полный перечень словосочетаний
    :return: перечень слов/словосочетаний с метрикой 
    """
    terms = []
    for candidate in c_group:
        is_nested = len(candidate.llinked) > 0
        if not is_nested:
            cval = math.log(candidate.wordcount, 2) * candidate.freq
        else:
            longer_phrases = [find_candidate_by_id(candidates, link_id) for link_id in candidate.llinked]
            if None in longer_phrases:
                logging.error(
                    "В ссылках фразы \"{0}\" закралась ссылка (x{1}) "
                    "на несуществующий id".format(candidate.collocation, longer_phrases.count(None)))
                continue
            pta = len(longer_phrases)  # должно быть равно len(candidate.llinked)
            longer_phrase_freq = sum([phrase.freq for phrase in longer_phrases])
            cval = math.log(candidate.wordcount, 2) * (candidate.freq - 1 / pta * longer_phrase_freq)
        if cval > THRESHOLD:
            terms.append(params(name=candidate.collocation, cvalue=cval))
    return terms


def parallel_conjugation(c_group: List[Collocation], candidates: List[Collocation],
                         is_single_threaded: bool = False) -> List[params]:
    """
    Функция многопоточного подчета стат метрики
    :param c_group: группа кандидатов с одинаковым wordcount
    :param candidates: полный перечень всех кандидатов
    :param is_single_threaded: флаг - выполнять ли в одном потоке
    :return: перечень терминов
    """
    logging.info("Разделяем на потоки")
    spliced_group_list = split_tasks(c_group)
    # TODO идея для оптимизации: ограничивать значения candidates для каждой из мини-групп
    # оставить только те, что упоминаются в llinked
    args = list(zip(spliced_group_list, [candidates for i in range(len(candidates))]))
    result = []
    if not is_single_threaded:
        logging.debug("Разделили аргументы по задачам ({0})".format(len(args)))
        with multiprocessing.Pool(processes=len(args)) as pool:
            immediate_results = pool.starmap(calculate_by_group, args)
            for i in immediate_results:
                result += i
    else:
        for arg in args:
            result += calculate_by_group(arg[0], arg[1])
    logging.debug("Готовы результаты обработки")
    return result
