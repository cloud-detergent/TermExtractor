# module PartOfSpeech
"""
Содержит необходимые структуры и методы по работе с частями речи
Enum PartOfSpeech
Конвертер POSNameConverter
"""
from enum import Enum


class PartOfSpeech(Enum):
    """
    @see http://www.ruscorpora.ru/corpora-morph.html
    Перечисление возможных частей речи
    """
    noun = 1,               """S существительное (яблоня, лошадь, корпус, вечность)"""
    verb = 2,               """V глагол (пользоваться, обрабатывать)"""
    adjective = 3,          """A  прилагательное (коричневый, таинственный, морской)"""
    adverb = 4,             """ADV наречие (сгоряча, очень)"""
    praedic = 5,            """PRAEDIC предикатив (жаль, хорошо, пора)"""
    parenth = 6,            """PARENTH вводное слово (кстати, по-моему)"""
    noun_pronoun = 7,       """S-PRO местоимение-существительное (она, что)"""
    adjective_pronoun = 8,  """A-PRO местоимение-прилагательное (который, твой)"""
    adverb_pronoun = 9,     """ADV-PRO местоименное наречие (где, вот)"""
    praedic_pronoun = 10,    """PRAEDIC-PRO местоимение-предикатив (некого, нечего)"""
    numeral = 11,            """NUM числительное (четыре, десять, много)"""
    numeral_adjective = 12, """A-NUM числительное-прилагательное (один, седьмой, восьмидесятый)"""
    preposition = 13,       """PR — предлог (под, напротив)"""
    conjunction = 14,       """CONJ — союз (и, чтобы)"""
    particle = 15,          """PART — частица (бы, же, пусть)"""
    interjection = 16,      """INTJ — междометие (увы, батюшки)"""


class POSNameConverter(object):
    """
    Класс-конвертер enum'a части речи в понятную человеку форму (англ/русс)
    """
    _table = {
        PartOfSpeech.noun: ('S', 'существительное', 'noun'),
        PartOfSpeech.adjective: ('A', 'прилагательное', 'adjective'),
        PartOfSpeech.numeral: ('NUM', 'числительное','numeral'),
        PartOfSpeech.numeral_adjective: ('A-NUM', 'числительное-прилагательное', 'numeral adjective'),
        PartOfSpeech.verb: ('V', 'глагол', 'verb'),
        PartOfSpeech.adverb: ('ADV', 'наречие', 'adverb'),
        PartOfSpeech.praedic:('PRAEDIC', 'предикатив', 'praedic'),
        PartOfSpeech.parenth: ('PARENTH', 'вводное','parenth'),
        PartOfSpeech.noun_pronoun: ('S-PRO', 'местоимение-существительное', 'noun pronoun'),
        PartOfSpeech.adjective_pronoun: ('A-PRO', 'местоимение-прилагательное'),
        PartOfSpeech.adverb_pronoun: ('ADV-PRO', 'местоименное наречие', 'adverb pronoun'),
        PartOfSpeech.praedic_pronoun: ('PRAEDIC-PRO', 'местоимение-предикатив', 'praedic pronoun'),
        PartOfSpeech.preposition: ('PR', 'предлог', 'preposition'),
        PartOfSpeech.conjunction: ('CONJ', 'союз', 'conjunction'),
        PartOfSpeech.particle: ('PART', 'частица', 'particle'),
        PartOfSpeech.interjection: ('INTJ', 'междометие', 'interjection')
    }

    @staticmethod
    def recognise_enum(string):
        """
        Возвращает enum части речи, соответствующий входной строке
        :param string: Обозначение части речи, исп. в национальном корпусе русского языка
        :return: enum PartOfSpeech, обозначающий часть речи
        """
        if not isinstance(string, str):
            raise TypeError("Аргумент должен быть строкой")

        cap_string = string.upper()
        found = ""
        for pos in list(POSNameConverter._table.keys()):
            if (POSNameConverter._table[pos])[0] == cap_string:
                found = pos
                break
        return found

    @staticmethod
    def get_human_name_r(e):
        """
        Возвращает метку части речи на русском языке
        :param e: enum PartOfSpeech
        :return: метка на русском
        """
        if not isinstance(e, PartOfSpeech):
            raise TypeError("Аргумент должен быть типа перечисления PartOfSpeech")

        definitive = POSNameConverter._table[e]
        return definitive[1]

    @staticmethod
    def get_human_name_en(e):
        """
        Возвращает метку части речи на английском языке
        :param e: enum PartOfSpeech
        :return: метка на английском
        """
        if not isinstance(e, PartOfSpeech):
            raise TypeError("Аргумент должен быть типа перечисления PartOfSpeech")

        definitive = POSNameConverter._table[e]
        return definitive[2]

    @staticmethod
    def get_corpus_def(e):
        """
        Возвращает метку части речи спецификации, используемой в национальном корпусе русского языка
        :param e: enum PartOfSpeech
        :return: метка вида, используемого в национальном корпусе
        """
        if not isinstance(e, PartOfSpeech):
            raise TypeError("Аргумент должен быть типа перечисления PartOfSpeech")

        definitive = POSNameConverter._table[e]
        return definitive[0]

    @staticmethod
    def get_all_en():
        """
        Возвращает список всех частей речи
        :return:
        """
        definitive = POSNameConverter._table.keys()
        return definitive[1]