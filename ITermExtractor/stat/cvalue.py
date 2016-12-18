import math
from collections import namedtuple
from ITermExtractor.Morph import is_identical_word, make_substrs, get_longer_terms
from typing import List
from operator import itemgetter
import logging
from ITermExtractor.Structures.WordStructures import collocation
from ITermExtractor.Structures.WordStructures import TaggedWord

params = namedtuple('params', ['name', 'cvalue'])
params_substr = namedtuple('params', ['name', 'freq', 'nested_freq', 'nested_inclusions'])
params_substr.__doc__ = "Параметры терминологических подстрок"
params_substr.name.__doc__ = "Подстрока"
params_substr.freq.__doc__ = "Общая частота встречаемости подстроки в корпусе f(b)"
params_substr.nested_freq.__doc__ = "частота встречаемости подстроки как вложенного термина в корпусе t(b)"
params_substr.nested_inclusions.__doc__ = "количество более длинных терминологических строк c(b)"
THRESHOLD = 1
linguistic_container = None

class LinguisticContainer(object):
    __dictionary__ = []

    def __init__(self, dictionary: List[TaggedWord]):
        self.__dictionary__ = dictionary

    def get_dictionary(self):
        return self.__dictionary__


def calculate(candidates: List[collocation], max_len: int) -> List[params]:
    """
    Подсчитывает c-value для списка терминологических кандидатов
    :param candidates: список терминологических кандидатов  collocation_tuple('словосочетание', 'число слов', 'частота')
    :param max_len: максимальное значение количества слов в списке
    :return: список терминов со значениями c-value
    """
    terms = []
    term_substrings = []
    max_len_candidates = [candidate for candidate in candidates if candidate.wordcount == max_len]
    other_candidates = [candidate for candidate in candidates if candidate.wordcount < max_len]
    # other_candidates = candidates - max_len_candidates # retract union

    for candidate in max_len_candidates:
        cval = math.log(candidate.wordcount, 2) * candidate.freq
        if cval > THRESHOLD:
            terms.append(params(name=candidate.collocation, cvalue=cval))
            substrs = make_substrs(candidate.collocation)
            for substr in substrs:
                # TODO check if they exist
                occurrences = [sub[0] for sub in enumerate(term_substrings) if sub[1].name == substr]
                existing_val = len(occurrences)
                if existing_val == 0:
                    term_substrings.append(params_substr(name=substr, freq=get_total_freq(candidate, candidates), nested_freq=candidate.freq, nested_inclusions=1))
                else:
                    # term_substrings[occurrences[0]].nested_freq += candidate.freq  # if candidate is not nested
                    # term_substrings[occurrences[0]].nested_inclusions += 1
                    data = term_substrings[occurrences[0]]
                    term_substrings[occurrences[0]] = params_substr(
                        name=data.name, freq=data.freq,
                        nested_freq=data.nested_freq + candidate.freq,
                        nested_inclusions=data.nested_inclusions + 1
                    )

    for candidate in other_candidates:
        occurrences = [sub[0] for sub in enumerate(term_substrings) if sub[1].name == candidate.collocation]   # we may already have it in the list
        if len(occurrences) == 0:
            cval = math.log(candidate.wordcount, 2) * candidate.freq

            if cval > THRESHOLD:
                terms.append(params(name=candidate.collocation, cvalue=cval))
                substrs = make_substrs(candidate.collocation)
                for substr in substrs:
                    # TODO check if they exist
                    occurrences = [sub[0] for sub in enumerate(term_substrings) if sub[1].name == substr]
                    # TODO правильно ли проверяет наличие при разных склонениях?
                    existing_val = len(occurrences)
                    if existing_val == 0:
                        term_substrings.append(params_substr(
                            name=substr, freq=get_total_freq(candidate, candidates),
                            nested_freq=candidate.freq, nested_inclusions=1)
                        )
                    else:
                        data = term_substrings[occurrences[0]]
                        # term_substrings[occurrences[0]].nested_freq += candidate.freq  # if candidate is not nested
                        # term_substrings[occurrences[0]].nested_inclusions += 1
                        term_substrings[occurrences[0]] = params_substr(
                            name=data.name, freq=data.freq,
                             nested_freq=data.nested_freq + 1,
                             nested_inclusions=data.nested_inclusions + 1
                        )

        else:  # в списке уже есть
            item = term_substrings[occurrences[0]]
            pta = item.nested_inclusions
            cval = math.log(candidate.wordcount, 2) * (candidate.freq - 1 / pta * item.nested_freq)

            if cval > THRESHOLD:
                terms.append(params(name=candidate.collocation, cvalue=cval))

                substrs = make_substrs(candidate.collocation)
                for substr in substrs:
                    # TODO check if they exist
                    occurrences = [sub[0] for sub in enumerate(term_substrings) if sub[1].name == substr]
                    existing_val = len(occurrences)
                    if existing_val == 0:
                        term_substrings.append(params_substr(
                            name=substr, freq=get_total_freq(candidate, candidates),
                            nested_freq=candidate.freq, nested_inclusions=1))
                    else:
                        # term_substrings[occurrences[0]].nested_freq += (candidate.freq - pta)  # if candidate is not nested
                        # term_substrings[occurrences[0]].nested_inclusions += 1
                        data = term_substrings[occurrences[0]]
                        term_substrings.append(params_substr(
                            name=data.name, freq=data.freq,
                            nested_freq=data.freq + candidate.freq - pta,
                            nested_inclusions=data.nested_inclusions + 1))

    logging.info("Подсчет cvalue закончен, сортировка и выход")
    terms = sort_by_cvalue(terms)
    return terms


def sort_by_cvalue(input_list: List[params]) -> List[params]:
    result = sorted(input_list, key=itemgetter(1), reverse=True)
    return result
# term_substrings += [params_substr(name= substr, freq= calculate_nested_params(substr, candidates), nested_freq=1) for substr in substrs]


def get_total_freq(line: collocation, candidates: List[collocation]) -> int:
    global linguistic_container
    longer_terms = get_longer_terms(line, candidates, linguistic_container.get_dictionary())
    not_nested_freq = sum(candidate.freq for candidate in longer_terms)
    return line.freq + not_nested_freq


def set_dictionary(dictionary: List[TaggedWord]):
    global linguistic_container
    linguistic_container = LinguisticContainer(dictionary)
    logging.debug("Передан словарь слов, {0} элементов".format(len(linguistic_container.get_dictionary())))
