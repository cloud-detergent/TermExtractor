# module Runner
"""
Модуль содержит методы разделения текста на предложения, обработки текста, присвоения меток словам
"""

from ITermExtractor.PartOfSpeech import POSNameConverter
from ITermExtractor.pos import Tagger
import re


def split_sentences(input_text: str) -> list:
    """
    Делит текст на предложения

    >>> split_sentences("Основная задача. Однако, в чем она заключается? Не в сиеминутном же восторге от бурной деятельности, воскликнет читатель! Да, это так.")
    ['Основная задача', 'Однако, в чем она заключается', 'Не в сиеминутном же восторге от бурной деятельности, воскликнет читатель', 'Да, это так']

    :param input_text: текст, содержащий несколько предложений
    :return:
    """
    sentence_end_symbols = '[.!?]'
    sentences = re.split(sentence_end_symbols, input_text)
    sentences.remove("")
    for i in range(0, len(sentences)):
        if sentences[i][0] == ' ':
            sentences[i] = sentences[i][1:]

    return sentences


def tag_collocation(word_collocation: str, point="") -> list:
    """
    Обрабатывает словосочетание, присваивая каждому слову метку части речи
    :param word_collocation: словосочетание
    :param point: костылик, требующийся для вызова из-под linguistic_filter
    :return: список слов с частями речи
    """
    tagger = Tagger()
    tagger.load(point + "tmp/svm.model", point + "tmp/ids.pickle") ## зависит от точки запуска

    tagged = []
    for word, label in tagger.label(word_collocation):
        label = tagger.get_label(label)
        #desc = POSNameConverter.get_corpus_def(label)
        tagged.append((word, label))
    return tagged


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
