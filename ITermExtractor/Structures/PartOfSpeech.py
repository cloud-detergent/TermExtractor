# module PartOfSpeech
"""
Содержит необходимые структуры и методы по работе с частями речи
Enum PartOfSpeech
Конвертер POSNameConverter
version 2
"""
from collections import namedtuple
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
    participle = 17,      """PRT — причастие (ющий)"""


class RepresentationMode(Enum):
    """
    Способы представления идентификаторов
    """
    ruscorpora = 1,     """ национальный корпус русского языка """
    opencorpora = 2,    """ открытый корпус """


class POSNameConverter(object):
    """
    Класс-конвертер enum'a части речи в понятную человеку форму (англ/русс)
    """

    POS_Structure = namedtuple('POS_Structure', ['Repr', 'name_ru', 'name_en'])
    RFrm = namedtuple('RepresentedForm', ['Mode', 'Name'])
    RFrm.__doc__ = "Форма представления идентификаторы части речи"
    RFrm.Mode.__doc__ = "Форма представления, enum RepresentationMode"
    RFrm.Name.__doc__ = "Дескриптор/идентификатор"
    POS_Structure.__doc__ = "Структура описания части речи"
    POS_Structure.Repr.__doc__ = "Варианты представления в корпусах"
    POS_Structure.name_ru.__doc__= "Наименование части речи на русском"
    POS_Structure.name_en.__doc__ = "Наименование части речи на английском"

    _table = {
        PartOfSpeech.noun: POS_Structure(Repr=(RFrm(RepresentationMode.ruscorpora, 'S'),
                                               RFrm(RepresentationMode.opencorpora, 'NOUN')),
                                         name_ru='существительное', name_en='noun'),
        PartOfSpeech.adjective: POS_Structure(Repr=(RFrm(RepresentationMode.ruscorpora, 'A'),
                                                    RFrm(RepresentationMode.opencorpora, 'ADJF'),
                                                    RFrm(RepresentationMode.opencorpora, 'ADJS')),
                                         name_ru='прилагательное', name_en='adjective'),
        PartOfSpeech.numeral: POS_Structure(Repr=(RFrm(RepresentationMode.ruscorpora, 'NUM'),
                                                    RFrm(RepresentationMode.opencorpora, 'NUMR')),
                                              name_ru='числительное', name_en='numeral'),
        PartOfSpeech.verb: POS_Structure(Repr=(RFrm(RepresentationMode.ruscorpora, 'V'),
                                               RFrm(RepresentationMode.opencorpora, 'VERB'),
                                               RFrm(RepresentationMode.opencorpora, 'INFN')),
                                            name_ru='глагол', name_en='verb'),
        PartOfSpeech.adverb: POS_Structure(Repr=(RFrm(RepresentationMode.ruscorpora, 'ADV'),
                                                 RFrm(RepresentationMode.opencorpora, 'ADVB'),
                                                 RFrm(RepresentationMode.opencorpora, 'COMP'),
                                                 ),
                                            name_ru='наречие', name_en='adverb'),
        PartOfSpeech.praedic: POS_Structure(Repr=(RFrm(RepresentationMode.ruscorpora, 'PRAEDIC'),
                                                  RFrm(RepresentationMode.opencorpora, 'PRED')),
                                            name_ru='предикатив', name_en='praedic'),
        PartOfSpeech.noun_pronoun: POS_Structure(Repr=(RFrm(RepresentationMode.ruscorpora, 'S-PRO'),
                                                  RFrm(RepresentationMode.opencorpora, 'NPRO')),
                                            name_ru='местоимение-существительное', name_en='noun pronoun'),
        PartOfSpeech.preposition: POS_Structure(Repr=(RFrm(RepresentationMode.ruscorpora, 'PR'),
                                                      RFrm(RepresentationMode.opencorpora, 'PREP')),
                                            name_ru='предлог', name_en='preposition'),
        PartOfSpeech.conjunction: POS_Structure(Repr=(RFrm(RepresentationMode.ruscorpora, 'CONJ'),
                                                      RFrm(RepresentationMode.opencorpora, 'CONJ')),
                                            name_ru='союз', name_en='conjunction'),
        PartOfSpeech.interjection: POS_Structure(Repr=(RFrm(RepresentationMode.ruscorpora, 'INTJ'),
                                                       RFrm(RepresentationMode.opencorpora, 'INTJ')),
                                                name_ru='междометие', name_en='interjection'),
        PartOfSpeech.particle: POS_Structure(Repr=(RFrm(RepresentationMode.ruscorpora, 'PART'),
                                                   RFrm(RepresentationMode.opencorpora, 'PRCL')),
                                                name_ru='частица', name_en='particle'),
        PartOfSpeech.participle: POS_Structure(Repr=(RFrm(RepresentationMode.opencorpora, 'PRTF'),
                                                   RFrm(RepresentationMode.opencorpora, 'PRTS')),
                                             name_ru='причастие', name_en='participle'),
    }

    @staticmethod
    def to_enum(field: str) -> PartOfSpeech:
        """
        Возвращает enum части речи, соответствующий входной строке
        :param string: Обозначение части речи, исп. в национальном корпусе русского языка
        :return: enum PartOfSpeech, обозначающий часть речи

        >>> POSNameConverter.to_enum("a")
        <PartOfSpeech.adjective: (3, 'A  прилагательное (коричневый, таинственный, морской)')>
        >>> POSNameConverter.to_enum("abc")
        ''
        >>> POSNameConverter.to_enum("adVB")
        <PartOfSpeech.adverb: (4, 'ADV наречие (сгоряча, очень)')>
        >>> POSNameConverter.to_enum('')
        Traceback (most recent call last):
        ...
        ValueError: Аргументом должна быть строка с наименованием части речи
        >>> POSNameConverter.to_enum('PRCL')
        <PartOfSpeech.particle: (15, 'PART — частица (бы, же, пусть)')>
        """
        if not isinstance(field, str):
            raise TypeError("Аргумент должен быть строкой")

        if "" == field:
            raise ValueError('Аргументом должна быть строка с наименованием части речи')

        cap_string = field.upper()
        found = ""
        for pos in list(POSNameConverter._table.keys()):
            val_list = POSNameConverter._table[pos].Repr
            descrs = [val.Name for val in val_list]
            if cap_string in descrs:
                found = pos
                break
        return found

    @staticmethod
    def get_human_name_r(e: PartOfSpeech) -> str:
        """
        Возвращает метку части речи на русском языке
        :param e: enum PartOfSpeech
        :return: метка на русском

        >>> POSNameConverter.get_human_name_r(PartOfSpeech.noun)
        'существительное'
        >>> POSNameConverter.get_human_name_r(1)
        Traceback (most recent call last):
        ...
        TypeError: Аргумент должен быть типа перечисления PartOfSpeech
        """
        if not isinstance(e, PartOfSpeech):
            raise TypeError("Аргумент должен быть типа перечисления PartOfSpeech")

        definitive = POSNameConverter._table[e]
        return definitive.name_ru

    @staticmethod
    def get_human_name_en(e: PartOfSpeech) -> str:
        """
        Возвращает метку части речи на английском языке
        :param e: enum PartOfSpeech
        :return: метка на английском

        >>> POSNameConverter.get_human_name_en(PartOfSpeech.noun)
        'noun'
        >>> POSNameConverter.get_human_name_en(1)
        Traceback (most recent call last):
        ...
        TypeError: Аргумент должен быть типа перечисления PartOfSpeech
        """
        if not isinstance(e, PartOfSpeech):
            raise TypeError("Аргумент должен быть типа перечисления PartOfSpeech")

        definitive = POSNameConverter._table[e]
        return definitive.name_en

    @staticmethod
    def get_corpus_def(e: PartOfSpeech, corpus: RepresentationMode) -> list:
        """
        Возвращает метку части речи спецификации, используемой в национальном корпусе русского языка и opencorpora
        :param e: enum PartOfSpeech
        :param corpus: тип дефициниции, используемый в корпусах
        :return: метка вида, используемого в корпусах

        >>> POSNameConverter.get_corpus_def(PartOfSpeech.noun, RepresentationMode.opencorpora)
        ['NOUN']

        >>> POSNameConverter.get_corpus_def(PartOfSpeech.adjective, RepresentationMode.opencorpora)
        ['ADJF', 'ADJS']

        >>> POSNameConverter.get_corpus_def(PartOfSpeech.praedic, RepresentationMode.ruscorpora)
        ['PRAEDIC']

        >>> POSNameConverter.get_corpus_def(1, RepresentationMode.ruscorpora)
        Traceback (most recent call last):
        ...
        TypeError: Аргумент должен быть типа перечисления PartOfSpeech
        """
        # TODO в любом случае в методах нужны проверки аргументов
        if not isinstance(e, PartOfSpeech):
            raise TypeError("Аргумент должен быть типа перечисления PartOfSpeech")
        if not isinstance(corpus, RepresentationMode):
            raise TypeError("Аргумент должен содержать сведения о форме представления части речи")

        definitive = POSNameConverter._table[e]
        rucorp_def = [repr.Name for repr in definitive.Repr if repr.Mode == RepresentationMode.ruscorpora]
        opencorp_def = [repr.Name for repr in definitive.Repr if repr.Mode == RepresentationMode.opencorpora]
        if corpus == RepresentationMode.opencorpora:
            return opencorp_def
        elif corpus == RepresentationMode.ruscorpora:
            return rucorp_def