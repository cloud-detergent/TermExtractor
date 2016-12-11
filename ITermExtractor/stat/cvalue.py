import math
from collections import namedtuple
from ITermExtractor.Morph import is_identical_word
from typing import List
from operator import itemgetter
import logging

candidate_terms = []
collocation = namedtuple('collocation', ['collocation', 'wordcount', 'freq'])
max_length = 5

params = namedtuple('params', ['name', 'cvalue'])
params_substr = namedtuple('params', ['name', 'freq', 'nested_freq', 'nested_inclusions'])
params_substr.__doc__ = "Параметры терминологических подстрок"
params_substr.name.__doc__ = "Подстрока"
params_substr.freq.__doc__ = "Общая частота встречаемости подстроки в корпусе f(b)"
params_substr.nested_freq.__doc__ = "частота встречаемости подстроки как вложенного термина в корпусе t(b)"
params_substr.nested_inclusions.__doc__ = "количество более длинных терминологических строк c(b)"
THRESHOLD = 1


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
                    term_substrings[occurrences[0]].nested_freq += candidate.freq  # if candidate is not nested
                    term_substrings[occurrences[0]].nested_inclusions += 1

    for candidate in other_candidates:
        occurrences = [sub[0] for sub in enumerate(term_substrings) if sub[1].name == candidate.collocation]  # we may already have it in the list
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
                        term_substrings.append(params_substr(name=substr, freq=get_total_freq(candidate, candidates),
                                                             nested_freq=candidate.freq, nested_inclusions=1))
                    else:
                        term_substrings[occurrences[0]].nested_freq += candidate.freq  # if candidate is not nested
                        term_substrings[occurrences[0]].nested_inclusions += 1

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
                        term_substrings.append(params_substr(name=substr, freq=get_total_freq(candidate, candidates),
                                                             nested_freq=candidate.freq, nested_inclusions=1))
                    else:
                        term_substrings[occurrences[0]].nested_freq += (candidate.freq - pta)  # if candidate is not nested
                        term_substrings[occurrences[0]].nested_inclusions += 1

    logging.info("Подсчет cvalue закончен, сортировка и выход")
    terms = sort_by_cvalue(terms)
    return terms


def sort_by_cvalue(input_list: List[params]) -> List[params]:
    result = sorted(input_list, key=itemgetter(1), reverse=True)
    return result
# term_substrings += [params_substr(name= substr, freq= calculate_nested_params(substr, candidates), nested_freq=1) for substr in substrs]


def make_substrs(collocation: str) -> List[str]:  # TODO а почему артиллерия не может быть термином
    """
    Возвращает набор возможных подстрок
    :param collocation: словосочетание
    :return: подстроки

    >>> make_substrs('занятие огневых позиций')
    ['занятие огневых', 'огневых позиций']
    >>> make_substrs('районы огневых позиций')
    ['районы огневых', 'огневых позиций']
    """
    if not isinstance(collocation, str):
        raise TypeError('Требуется строка')
    if collocation == '':
        return ''
    words = [word for word in collocation.split()] # TODO different 2/3/4w combinations
    substrings = []
    for wcount in range(2, len(words), -1):
        for j in range(0, len(words) - wcount):
            substrings.append(words[j:j+wcount])
    return substrings


'''
def is_nested(line: collocation_tuple, candidates: list(collocation_tuple)) -> bool:
    """
    Проверяет является ли термин вложенным
    :param line: термин
    :param candidates: список терминов
    :return: соотвествие состояния вложенности
    """
    contained = in_collocation_list(line=line, collocation_list=candidates)
    is_nested = contained and True
    return is_nested


def is_nested(line: collocation_tuple, line_list: list) -> bool:
    occurrences = sum(1 for l in line_list if contains(line.collocation, l.collocation))
    return occurrences > 0


def get_hub_terms(line: collocation_tuple, line_list: list) -> list:
    # термины, влючающие в себя указанный термин
    occurrences = [l.name for l in line_list if contains(line.collocation, l.collocation)]
    return occurrences
'''


def get_nested_freq(line: collocation, line_list: list) -> int:
    # частота встречаемости влож терм
    occurrences = sum(l.freq for l in line_list if contains(line.collocation, l.collocation))
    return occurrences


def get_total_freq(line: str, candidates: list) -> int:
    not_nested_freq = sum(candidates.freq for candidate in candidates if candidate.collocation == line)
    nested_freq = get_nested_freq(line, candidates)
    return nested_freq + not_nested_freq


def contains(line_1: str, line_2: str) -> bool:
    """
    Проверяет наличие строки line_1 в строке line_2
    :param line_1:
    :param line_2:
    :return:
     >>> contains("огня", "огонь артиллерии")
     True
     >>> contains("огонь", "огонь")
     False
    """
    if line_1 == line_2 or len(line_1) > len(line_2): # or is_identical_word(line_1, line_2):  # TODO overcomplicating stuff
        return False
    line_2words = line_2.split()
    if len(line_2words) <= 1:
        return False
    occurrences = sum(1 for word in line_2words if is_identical_word(word, line_1))
    return occurrences > 0
