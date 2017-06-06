# module Runner
"""
Модуль содержит методы разделения текста на предложения, обработки текста, присвоения меток словам
"""

import re
import os
import ITermExtractor.Morph as m
from typing import List
from ITermExtractor.Morph import TaggedWord, Separator


def split_sentences(input_text: str) -> str:
    """
    Делит текст на предложения
    :param input_text: текст, содержащий несколько предложений, разделенный новыми линиями
    :return:

    >>> split_sentences("Основная задача. Однако, в чем она заключается? Не в сиеминутном же восторге от бурной деятельности, воскликнет читатель! Да, это так.")
    'Основная задача\\nОднако, в чем она заключается\\nНе в сиеминутном же восторге от бурной деятельности, воскликнет читатель\\nДа, это так'
    >>> split_sentences('Основные определения данной предметной области: \\n 1. Терминологичность - мера, подсчитывающая степень, с которой термин относится к определенной предметной области \\n 2. Синтагматичность - мера, определяющая силы ассоциации слов в термине между собой')
    'Основные определения данной предметной области\\nТерминологичность - мера, подсчитывающая степень, с которой термин относится к определенной предметной области\\nСинтагматичность - мера, определяющая силы ассоциации слов в термине между собой'
    >>> split_sentences('Основные определения данной предметной области: \\n I. Терминологичность - мера, подсчитывающая степень, с которой термин относится к определенной предметной области \\n IV. Синтагматичность - мера, определяющая силы ассоциации слов в термине между собой')
    'Основные определения данной предметной области\\nТерминологичность - мера, подсчитывающая степень, с которой термин относится к определенной предметной области\\nСинтагматичность - мера, определяющая силы ассоциации слов в термине между собой'

    """
    split_symbols = r'[\dxvcmiXVCMI]{1,4}[.)]{1}\s|(?<=\w)+[.?!:](\s+|$)'  # Символы конца предложения + номера в списке
    contents_symbols = r'(?<=\w\b)[ ]*\.{2,}\d{1,5}'  # Символы разделители пунктов содержания
    divided_by_new_line_sentences_symbols = r'(?<=\w\b)[\r\n]+(?=\b\w)|(?<=\w\b,)[\r\n]+(?=\b\w)'  # Для предложений, в середине который \n
    reference_symbols = r'\[[\d\u00ab?\w+\u00bb?\u2010-\u2015\.\s]+\]'  # Символы-ссылки на литературу
    brackets_writings_symbols = r'\(([\w ]+)\)'  # для доп информации в скобках

    spaced_words_pattern = r'\b(\w ){3,}\w\b'  # TODO вернуться к обработке разреженных слов
    #  TODO возможно какую-то доп обработку: командира батальона (полка) -> командира батальона, командира полка

    sentences = re.sub(pattern=divided_by_new_line_sentences_symbols, repl=' ', string=input_text)
    sentences = re.sub(pattern=contents_symbols, repl=os.linesep, string=sentences)
    sentences = re.sub(pattern=split_symbols, repl=os.linesep, string=sentences)
    sentences = re.sub(pattern=reference_symbols, repl=os.linesep, string=sentences)
    sentences = re.sub(pattern=brackets_writings_symbols, repl=r'\1', string=sentences)
    sentences = re.sub(pattern=r"[^\S\r\n]+", repl=" ", string=sentences)
    sentences = re.sub(pattern=r"[^\S\r\n]*[\r\n][^\S\r\n]*", repl=os.linesep, string=sentences)
    sentences = re.sub(pattern=r"[\r\n]{2,}", repl=os.linesep, string=sentences)
    sentences = re.sub(pattern=r"[\r\n]$", repl="", string=sentences)
    # sentences = re.split(split_symbols, input_text)
    # sentences = [sentence.strip() for sentence in sentences if sentence is not None and sentence != '' and not str.isspace(sentence)]
    return sentences


def tag_collocation(word_collocation: str) -> List[TaggedWord and Separator]:
    """
    Обрабатывает словосочетание, присваивая каждому слову метку части речи
    :param word_collocation: словосочетание
    :return: список слов с частями речи
    """
    tagged = m.tag_collocation(word_collocation)
    return tagged

    #tagger = Tagger()
    #tagger.load(point + "tmp/svm.model", point + "tmp/ids.pickle") ## зависит от точки запуска

    #for word, label in tagger.label(word_collocation):
    #    label = tagger.get_label(label)
    #    #desc = POSNameConverter.get_corpus_def(label)
    #    tagged.append((word, label))


def parse_text(input_text: str) -> List[List[TaggedWord]]:
    """
    Метод обрабатывает текст, деля его на предложения и присваивая каждому слову тэг/метку части речи
    :param input_text: текст, который необходимо пропарсить
    :return: список предложений с тэгами частей речи слов
    """
    tagged_sent_list = []
    sentences = split_sentences(input_text)
    for sentence in sentences.splitlines():
        if sentence != "":
            tag_info = tag_collocation(sentence)
            # tagged_sent_list += tag_info
            tagged_sent_list.append(tag_info)
    return tagged_sent_list
