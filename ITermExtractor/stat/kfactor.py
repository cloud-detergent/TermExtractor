from ITermExtractor.Structures.WordStructures import collocation, TaggedWord
from typing import List
from operator import itemgetter
from ITermExtractor.Morph import make_substrs, is_identical_collocation_q, get_longer_terms, assign_tags
from ITermExtractor.stoplist import StopList
import logging

KFACTOR = 0.7
THRESHOLD = {2: 0, 3: 0, 4: 0, 5: 0}


def calculate(candidates: List[collocation], dictionary: List[TaggedWord]) -> List[collocation]:
    logger = logging.getLogger()
    result_list = []
    logger.info("Начало статистической проверки ")
    candidates = sorted(candidates, key=itemgetter(1))
    min_word_count = candidates[0].wordcount
    max_word_count = candidates[-1].wordcount
    # TODO после двойного прогона осуществляется отсев терминов, почему?

    logger.info("Терминологические кандидаты отсортированы, мин и макс длины слов выяснены")
    # sl = StopList(use_settings=True)  # возможно, стоит убрать (двойная работа)
    # logger.debug("Кандидатов было {0}, длина от {1} до {2}".format(len(candidates), min_word_count, max_word_count))
    # candidates = sl.filter(candidates)
    # logger.info("Произведена фильтрация через стоп-лист, осталось {0} кандидатов".format(len(candidates)))
    logger.info("Переходим к алгоритму")
    for i in range(max_word_count, min_word_count - 1, -1):
        # TODO threshold + reverse order + remove shorter terms check
        ngrams = [candidate for candidate in candidates if candidate.wordcount == i]
        longer_grams = [candidate for candidate in candidates if candidate.wordcount > i]
        logger.debug("Обрабатываем термины из {0} слов, таких {1} к {2} элементов"
                     .format(i, len(ngrams), len(longer_grams)))
        for ngram in ngrams:
            if ngram.wordcount == max_word_count:
                longer_terms = []
            else:
                longer_terms = get_longer_terms(ngram, longer_grams, dictionary)

            if len(longer_terms) > 0:
                logger.info("Более длинные термины, содержащие рассматриваемый: {0} -> {1}".format(longer_terms, ngram.collocation))

            if len(longer_terms) == 0:
                result_list.append(ngram)
            elif len(longer_terms) > 0:
                for longer_term in longer_terms:
                    if longer_term.freq > KFACTOR * ngram.freq:
                        result_list.append(longer_term)
                    else:
                        result_list.append(ngram)
                        if longer_term in result_list:
                            result_list.remove(longer_term)
                        longer_grams.remove(longer_term)
                        candidates.remove(longer_term)

    result_list = sorted(result_list, key=itemgetter(2), reverse=True)
    logger.info("Список терминов сформирован, элементов: {0}".format(len(result_list)))
    return result_list
