import itertools
import math
import logging
import multiprocessing
from collections import namedtuple
from typing import List, Dict
from operator import itemgetter
from ITermExtractor.Structures.WordStructures import Collocation, TaggedWord, Separator
from itertools import groupby
from helpers import split_tasks
from ITermExtractor.Morph import find_candidate_by_id

params = namedtuple('params', ['name', 'termhood', 'unithood'])
params.__doc__ = "Параметры терминологических подстрок"
params.name.__doc__ = "Слово/Фраза"
params.termhood.__doc__ = "Терминологичность"
params.unithood.__doc__ = "Синтагматичность"

cinfo = namedtuple('candidate_info', ['candidate', 'words'])
cinfo.__doc__ = "Параметры терминологических подстрок"
cinfo.candidate.__doc__ = "Слово/Фраза"
cinfo.words.__doc__ = "Слова, составляющие, словарь"


# терминологичность высчитывает вероятность нахождения слова в доменно-спец документе, но как определять какой из них является доменно специфичным, если все документы посвящены 1 пред обл?
# или же считать по всем и определять максимальное знач?
def calculate_word_document_probability(word: str, document: List[List[TaggedWord]]):
    """
    Подсчет вероятности встречаемости слова в документе
    :param word: слово с тегами
    :param document: документ с тегами
    :return:
    """
    freq = 0
    for sentence in document:
        for w in sentence:
            if isinstance(w, Separator) or w is None:
                continue
            if w.normalized == word:
                freq += 1
    # total_word_count = sum(map(lambda x: len(x), filter(lambda  x: isinstance(x, TaggedWord), document)))
    total_word_count = len(list(filter(lambda x: isinstance(x, TaggedWord), itertools.chain(*document))))
    probability = freq / total_word_count
    return word, probability


# TODO test
def calculate_word_probabilities(candidates: List[Collocation], documents: List[List[TaggedWord]]) -> List[cinfo]:
    """
    Подсчитывает вероятности встречаемости слов из кандидатов и сводит в единую структуру
    :param candidates: кандидаты в термины
    :param documents: документы
    :return:
    """
    # TODO calc all w probs -> dict
    # candidate, [word, word_prob_doc, word_prob_general]
    words = []
    candidate_infos = []
    for candidate in candidates:
        normalized_words = candidate.pnormal_form.split()
        words += normalized_words
        info = (candidate, words)
        candidate_infos.append(info)

    words = list(set(words))
    corpora = list(itertools.chain(*documents))
    word_dict = {}

    for word in words:
        word_arg = [word for i in range(len(documents))]
        document_probabilities = list(map(calculate_word_document_probability, word_arg, documents))  # Pd(Wi)
        corpora_probability = calculate_word_document_probability(word, corpora)
        pd_wi = max(document_probabilities, key=itemgetter(1))
        pd_wi = pd_wi[1] if pd_wi is not None else 0
        word_dict[word] = (pd_wi, corpora_probability)

    for i in range(len(candidate_infos)):
        can = candidate_infos[i][0]
        words = candidate_infos[i][1]
        can_word_info = [word_dict[w] for w in words]
        candidate_infos[i] = cinfo(can, can_word_info )

    return candidate_infos


def threading_calculate(candidates: List[Collocation], documents: List[List[TaggedWord]], processes: int=1) -> List[params]:
    with multiprocessing.Pool(processes=processes) as pool:
        candidate_tasks = split_tasks(candidates, processes)
        document_tasks = [documents for i in range(processes)]
        args = zip(candidate_tasks, document_tasks)
        result = pool.starmap(calculate, args)
    return result


def calculate(candidates: List[Collocation], documents: List[List[TaggedWord]]) -> List[params]:
    result = list()

    corpora = list(itertools.chain(*documents))
    # corpora_words = list(filter(lambda x: isinstance(x, TaggedWord), itertools.chain(*corpora)))
    logging.debug("Начало подсчета GlossEx")
    counter = 0

    for candidate in candidates:
        if counter % 250 == 0:
            logging.debug("Подсчет знач для {0}/{1}".format(counter, len(candidates)))
        counter += 1
        normalized_words = candidate.pnormal_form.split()
        args = list(itertools.product(normalized_words, documents))
        word_args = list(map(lambda x: x[0], args))
        document_args = list(map(lambda x: x[1], args))
        document_probabilities = list(map(calculate_word_document_probability, word_args, document_args))  # Pd(Wi)

        document_probabilities_srt = sorted(document_probabilities, key=itemgetter(0))
        document_probabilities_grp = groupby(document_probabilities_srt, key=itemgetter(0))
        # list(map(lambda x: (x[0], list(x[1])), document_probabilities_grp))
        document_probabilities_chosen = list(map(lambda key_probs: max(key_probs[1], default=(key_probs[0], 0)), document_probabilities_grp))

        # corpora_arg = itertools.product(corpora_words, repeat=len(normalized_words))
        corpora_arg = [corpora for i in range(len(normalized_words))]

        with multiprocessing.Pool(processes=len(normalized_words)) as pool:
            args = zip(normalized_words, corpora_arg)
            corpora_probabilities = pool.starmap(calculate_word_document_probability, args)

        # corpora_probabilities = map(calculate_word_document_probability, normalized_words, corpora_arg)

        word_probabilities = [(w1, a, b)
                              for w1, a in document_probabilities_chosen
                              for w2, b in corpora_probabilities if w1 == w2]

        termhood = candidate.wordcount ** (-1) * sum([math.log2(dp / cp) for w, dp, cp in word_probabilities])

        total_corpora_word_count = sum(list(map(lambda x: len(x), corpora)))
        u_demominator = sum(map(lambda x: x[1] * total_corpora_word_count, corpora_probabilities))
        unithood = candidate.wordcount * candidate.freq * math.log10(candidate.freq) / u_demominator
        # TODO возможно, freq здесь не количество вхождений
        result.append(params(candidate.collocation, termhood, unithood))

    logging.debug("Конец обработки, GlossEx")
    return result
