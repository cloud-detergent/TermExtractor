from typing import List, Any
from operator import itemgetter
LIMIT_PER_PROCESS = 80


def split_tasks(task_list: List[Any]):
    """
    Разделяет список на несколько для равномерного разделения процессов на параллельные потоки
    :param task_list: входной список
    :return: разделенный список
    """
    length = len(task_list)
    threads = 1
    if length > LIMIT_PER_PROCESS:
        threads = int(length / LIMIT_PER_PROCESS) + 1
    if threads == 1:
        split_list = [task_list]
    else:
        split_list = [task_list[LIMIT_PER_PROCESS * i:LIMIT_PER_PROCESS * (i + 1)] for i in range(threads)]
    return split_list


def remove_spans(term: str, spans: list) -> str:
    """
    Удаляет из строки слова, включенные в стоп-список
    :param term: термин
    :param spans: список интервалов
    :return: отредактированный термин
    >>> remove_spans('парково-хозяйственный', [(7, 7)])
    'парково хозяйственный'
    >>> remove_spans('белый высокооборотистый оптический привод', [(0, 5)])
    'высокооборотистый оптический привод'
    >>> remove_spans('новое высокоэтажное быстрое строительство', [(0, 5), (20, 27)])
    'высокоэтажное строительство'
    >>> remove_spans('трехэтажный раздел', [(12, 18)])
    'трехэтажный'
    """
    flag = False in [isinstance(span, tuple) and len(span) == 2 and isinstance(span[0], int)
                     and isinstance(span[1], int) and span[0] <= span[1] for span in spans]
    if flag:
        raise ValueError("Требуется список интервалов, упакованных в кортежи")
    allowed_spans = []
    max_len = len(term)
    for i in range(0, len(spans) + 1):
        if i == 0:
            if spans[i][0] >= 1:
                allowed_spans.append((0, spans[i][0]))
        elif i >= len(spans):
            if spans[i - 1][1] < max_len:
                allowed_spans.append((spans[i - 1][1] + 1, max_len))
        else:
            allowed_spans.append((spans[i - 1][1], spans[i][0]))

    parts = [term[span[0]: span[1]].strip() for span in allowed_spans]
    edited_term = ' '.join(parts)
    return edited_term


def is_correct_word(word: str) -> bool:
    """
    Checks word for correctitude: correct word consists only of alphabetic chars with optional dash
    :param word: string
    :return:

    >>> is_correct_word("парково-хозяйственный")
    True
    >>> is_correct_word("парково-хозяйi9999ственный")
    False
    >>> is_correct_word("артиллерия")
    True
    """
    if not isinstance(word, str) or word == "" or word.count(" ") > 1:
        return False
    flag = word.isalpha()
    if not flag and '-' in word:
        dash_index = word.index("-")
        remaining_word = word.replace("-", "", 1)
        flag = 0 < dash_index < len(word) and remaining_word.isalpha()
    return flag
