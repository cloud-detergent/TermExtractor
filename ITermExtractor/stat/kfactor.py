from ITermExtractor.Structures.WordStructures import collocation, TaggedWord
from typing import List
from operator import itemgetter
from ITermExtractor.Morph import make_substrs, is_identical_collocation_q, get_longer_terms, assign_tags
from ITermExtractor.stoplist import StopList
import logging

KFACTOR = 0.7
THRESHOLD = [0, 0, 0, 0]


def calculate(candidates: List[collocation], dictionary: List[TaggedWord]) -> List[collocation]:
    logger = logging.getLogger()
    result_list = []
    logger.info("Начало статистической проверки ")
    candidates = sorted(candidates, key=itemgetter(1))
    min_word_count = candidates[0].wordcount
    max_word_count = candidates[-1].wordcount
    sl = StopList(use_settings=True)  # возможно, стоит убрать (двойная работа)
    # TODO после двойного прогона осуществляется отсев терминов, почему?

    logger.info("Терминологические кандидаты отсортированы, мин и макс длины слов выяснены")
    logger.debug("Кандидатов было {0}, длина от {1} до {2}".format(len(candidates), min_word_count, max_word_count))
    candidates = sl.filter(candidates)
    logger.info("Произведена фильтрация через стоп-лист, осталось {0} кандидатов".format(len(candidates)))
    logger.info("Переходим к алгоритму")
    for i in range(min_word_count, max_word_count + 1):
        # TODO output progrlLess
        ngrams = [candidate for candidate in candidates if candidate.wordcount == i]
        longer_grams = [candidate for candidate in candidates if candidate.wordcount > i]
        logger.debug("Обрабатываем термины из {0} слов, таких {1} к {2} элементов"
                     .format(i + 1, len(ngrams), len(longer_grams)))
        for ngram in ngrams:
            if ngram.wordcount == max_word_count:
                longer_terms = []
            else:
                longer_terms = get_longer_terms(ngram, longer_grams, dictionary)
            if ngram.wordcount == min_word_count:
                shorter_terms = []
            else:
                shorter_terms = [assign_tags(s) for s in make_substrs(ngram.collocation)]

            logger.info("Проверяем словосочетание '{0}', в котором коротких подстрок {1}"
                        .format(ngram.collocation, len(shorter_terms)))
            logger.info("Более длинные термины, содержащие рассматриваемый: {0}"
                        .format(longer_terms))

            if len(longer_terms) == 0:
                result_list.append(ngram)
            elif len(longer_terms) > 0:
                for longer_terms in longer_terms:
                    if longer_terms.freq > KFACTOR * ngram.freq:
                        result_list.append(longer_terms)
                    else:
                        result_list.append(ngram)

            if len(shorter_terms) > 0:
                for shorter_term in shorter_terms:
                    if shorter_term.freq <= 1 / KFACTOR * ngram.freq:
                        # скорее всего, к этому моменту все подстроки должны быть добавлены
                        is_appended = [True for term in result_list
                                       if is_identical_collocation_q
                                       (assign_tags(term.collocation, dictionary), shorter_term)]
                        if not is_appended:
                            shorter_term_words = [word.word for word in shorter_term]
                            col = ' '.join(shorter_term_words)
                            result_list.append(collocation(
                                collocation=col,
                                wordcount=len(shorter_term_words),
                                freq=ngram.freq
                            ))
                            result_list.remove(ngram)
                            logger.debug("Подстрока кандидата '{0}' не была ранее в списке, но подходит по параметрам"
                                         .format(col))
                            logger.debug("Более длинный термин был удален")
        result_list = sorted(result_list, key=itemgetter(2), reverse=True)
    logger.info("Список терминов сформирован, элементов: {0}".format(len(result_list)))
    return result_list
