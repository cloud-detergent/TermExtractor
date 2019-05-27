from typing import List, Any
from operator import itemgetter
import re
import logging

from ITermExtractor.Structures.WordStructures import TaggedWord, contains_sentence

LIMIT_PER_PROCESS = 80
THREAD_LIMIT = 8
document_title_re = re.compile('^([А-Я/\d,№()–-]{1,20}[\s\n]){3,}', re.MULTILINE)


def split_tasks(task_list: List[Any], processes: int=0):
    """
    Разделяет список на несколько для равномерного разделения процессов на параллельные потоки
    :param task_list: входной список
    :return: разделенный список
    """
    length = len(task_list)
    threads = 1
    data_array_limit = LIMIT_PER_PROCESS
    if processes == 0:
        if length > LIMIT_PER_PROCESS:
            threads = int(length / LIMIT_PER_PROCESS) + 1
            threads = THREAD_LIMIT if threads > THREAD_LIMIT else threads
            data_array_limit = int(length / threads)
            logging.debug('Настроили количество потоков и список задач: {0} потоков по {1} строк'.format(threads, data_array_limit))
    else:
        threads = processes
        data_array_limit = int(length / threads)
    if threads == 1:
        split_list = [task_list]
    else:
        split_list = [task_list[data_array_limit * i:data_array_limit * (i + 1)] for i in range(threads)]
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


def get_documents(text: List[List[TaggedWord]], keys: List[str]=list()) -> tuple:
    if not isinstance(text, list) or not isinstance(keys, list) or any((not isinstance(key, str) for key in keys)):
        return text,

    current_document = []
    documents = []
    for sentence in text:
        contains = [contains_sentence(sentence, key, 4) for key in keys]
        if any(contains):
            documents.append(current_document)
            current_document = [sentence]
        else:
            if len(sentence) != 0:
                current_document.append(sentence)
    documents.append(current_document)

    return documents
