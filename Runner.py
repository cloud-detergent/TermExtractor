# module Runner
"""
Модуль содержит методы разделения текста на предложения, обработки текста, присвоения меток словам
"""

import re

import ITermExtractor.Morph as m


#from ITermExtractor.pos import Tagger


def split_sentences(input_text: str) -> list:
    # TODO учитывать списки с арабскими и римскими цифрами
    """
    Делит текст на предложения

    >>> split_sentences("Основная задача. Однако, в чем она заключается? Не в сиеминутном же восторге от бурной деятельности, воскликнет читатель! Да, это так.")
    ['Основная задача', 'Однако, в чем она заключается', 'Не в сиеминутном же восторге от бурной деятельности, воскликнет читатель', 'Да, это так']
    >>> split_sentences('Основные определения данной предметной области: \\n 1. Терминологичность - мера, подсчитывающая степень, с которой термин относится к определенной предметной области \\n 2. Синтагматичность - мера, определяющая силы ассоциации слов в термине между собой')
    ['Основные определения данной предметной области:', 'Терминологичность - мера, подсчитывающая степень, с которой термин относится к определенной предметной области', 'Синтагматичность - мера, определяющая силы ассоциации слов в термине между собой']
    >>> split_sentences('Основные определения данной предметной области: \\n I. Терминологичность - мера, подсчитывающая степень, с которой термин относится к определенной предметной области \\n IV. Синтагматичность - мера, определяющая силы ассоциации слов в термине между собой')
    ['Основные определения данной предметной области:', 'Терминологичность - мера, подсчитывающая степень, с которой термин относится к определенной предметной области', 'Синтагматичность - мера, определяющая силы ассоциации слов в термине между собой']


    :param input_text: текст, содержащий несколько предложений
    :return:
    """
    split_symbols = '[\dxvcmiXVCMI]{1,4}[.)]{1}\s|(?<=\w)+[.?!](\s|$)'  # Символы конца предложения + номера в списке
    sentences = re.split(split_symbols, input_text)
    sentences = [sentence.strip() for sentence in sentences if sentence is not None and sentence != '' and not str.isspace(sentence)]
    return sentences


def tag_collocation(word_collocation: str) -> list:
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


def parse_text(input_text: str) -> list:
    """
    Метод обрабатывает текст, деля его на предложения и присваивая каждому слову тэг/метку части речи
    :param input_text: текст, который необходимо пропарсить
    :return: список предложений с тэгами частей речи слов
    """
    tagged_sent_list = []
    sentences = split_sentences(input_text)
    for sentence in sentences:
        if sentence != "":
            tag_info = tag_collocation(sentence)
            tagged_sent_list.append(tag_info)
    return tagged_sent_list
