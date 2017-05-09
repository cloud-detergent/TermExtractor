import math
from collections import namedtuple
from typing import List
from operator import itemgetter
import logging
from ITermExtractor.Structures.WordStructures import Collocation
from ITermExtractor.Structures.WordStructures import TaggedWord
from itertools import groupby
from ITermExtractor.Tests.linguistic_filter import is_integral

params = namedtuple('params', ['name', 'cvalue'])
params.__doc__ = "Параметры терминологических подстрок"
params.name.__doc__ = "Слово/Фраза"
params.cvalue.__doc__ = "Величина cvalue"
THRESHOLD = 1


class LinguisticContainer(object):
    __dictionary__ = []

    def __init__(self, dictionary: List[TaggedWord]):
        self.__dictionary__ = dictionary

    def get_dictionary(self):
        return self.__dictionary__


def calculate(candidates: List[Collocation]) -> List[params]:
    """
    Подсчитывает c-value для списка терминологических кандидатов
    :param c_group: список терминологических кандидатов  collocation_tuple('словосочетание', 'число слов', 'частота')
    :param max_len: максимальное значение количества слов в списке
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
        for candidate in c_group:
            is_nested = len(candidate.llinked) > 0
            if not is_nested:
                cval = math.log(candidate.wordcount, 2) * candidate.freq
            else:
                longer_phrases = [find_candidate_by_id(candidates, link_id) for link_id in candidate.llinked]
                if None in longer_phrases:
                    logging.error("В ссылках фразы \"{0}\" закралась ссылка (x{1}) на несуществующий id".format(candidate.collocation, longer_phrases.count(None)))
                    continue
                pta = len(longer_phrases)  # должно быть равно len(candidate.llinked)
                longer_phrase_freq = sum([phrase.freq for phrase in longer_phrases])
                cval = math.log(candidate.wordcount, 2) * (candidate.freq - 1 / pta * longer_phrase_freq)
            if cval > THRESHOLD:
                terms.append(params(name=candidate.collocation, cvalue=cval))
        logging.info("Кандидаты длиной {0} сл. обработаны".format(index))

    logging.info("Подсчет cvalue закончен (терминов: {0}), сортировка и выход".format(len(terms)))
    terms = sorted(terms, key=itemgetter(1), reverse=True)
    return terms


def find_candidate_by_id(collocation_list: List[Collocation], cid: int):
    results = [collocation for collocation in collocation_list if collocation.id == cid]
    result = results[0] if len(results) > 0 else None
    if result is None:
        collocation_dict = dict([(r.id, r) for r in collocation_list])
        collocation_with_links = list(filter(lambda x: len(x.llinked) > 0, collocation_list))
        link_integrity_checks = [all(link in collocation_dict for link in p.llinked) for p in collocation_with_links]
        flag = all(link_integrity_checks)
        logging.debug("----> Фраза по id (#{0}) не найдена, все ли в порядке со ссылками в списке: {1}, а хоть что-то: {2}".format(cid, flag, True in link_integrity_checks))
    return result
