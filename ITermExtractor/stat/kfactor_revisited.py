from ITermExtractor.Structures.WordStructures import Collocation, TaggedWord
from typing import List
from operator import itemgetter
from ITermExtractor.Morph import find_candidate_by_id
from itertools import groupby
import logging

KFACTOR = 0.7
THRESHOLD = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}


def is_beyond_threshold(phrase: Collocation) -> bool:
    result = phrase.freq >= THRESHOLD[phrase.wordcount]
    return result


def calculate(candidates: List[Collocation], dictionary: List[TaggedWord]) -> List[Collocation]:
    logger = logging.getLogger()
    result_list = []
    logger.info("Начало статистической проверки ")
    candidates = sorted(candidates, key=itemgetter('wordcount'), reverse=True)

    grouped_by_len = dict()
    candidate_lengths = []

    for key, value_sitter in groupby(candidates, key=itemgetter('wordcount')):
        grouped_by_len[key] = list(value_sitter)
        candidate_lengths.append(key)

    for index, c_group in grouped_by_len.items():
        for candidate in c_group:
            is_nested = len(candidate.llinked) > 0
            if not is_nested:
                if is_beyond_threshold(candidate):
                    result_list.append(candidate)
            else:
                longer_phrases = [find_candidate_by_id(candidates, link_id) for link_id in candidate.llinked]
                for longer_term in longer_phrases:
                    if longer_term.freq > KFACTOR * candidate.freq:
                        if is_beyond_threshold(candidate):
                            result_list.append(candidate)
                    else:
                        if is_beyond_threshold(longer_term) and longer_term not in candidates:
                            result_list.append(longer_term)
        logging.info("Кандидаты длиной {0} сл. обработаны".format(index))

    logger.info("Список терминов сформирован, элементов: {0}. Сортировка впереди".format(len(result_list)))
    result_list = sorted(result_list, key=itemgetter('freq'), reverse=True)
    logger.info("Список терминов сформирован, элементов: {0}".format(len(result_list)))
    return result_list
