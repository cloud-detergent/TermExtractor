from collections import namedtuple
from copy import deepcopy

TaggedWord = namedtuple('TaggedWord', ['word', 'pos', 'case', 'normalized'])
TaggedWord.__doc__ = "Размеченное слово"
TaggedWord.word.__doc__ = "Слово"
TaggedWord.pos.__doc__ = "Часть речи"
TaggedWord.case.__doc__ = "Падеж"
TaggedWord.normalized.__doc__ = "Нормальная форма слова"


class Collocation(dict):
    """
    Словосочетание со статистическими параметрами
    """

    def __init__(self, collocation: str=str(), wordcount: int=0, freq: int=0, pnormal_form: str=str(), llinked: list=list(), cid: int=0):
        """
        Конструктор класса-словаря
        :param collocation: Словосочетание, строка
        :param wordcount: Количество слов в словосочетании
        :param freq: Количество упоминаний словоформы в исходном корпусе
        :param pnormal_form: Псевдо нормальная форма словосочетания: все слова в норм форме
        :param llinked: Список ссылок на более длинные словосочетаний / те же словоформы
        :param cid: id
        """
        if collocation != str() and wordcount == 0:
            wordcount = len(collocation.split(' '))
        default_values = dict(zip(('collocation', 'wordcount', 'freq', 'pnormal_form', 'llinked', 'id'), (collocation, wordcount, freq, pnormal_form, llinked, cid)))
        for k, v in default_values.items():
            self[k] = v

    def add_freq(self, increment=1):
        self.freq += increment

    def __getattr__(self, attr):
        if attr not in ('id', 'collocation', 'wordcount', 'freq', 'pnormal_form', 'llinked'):
            raise KeyError("Ключ с таким именем отсутствует в словаре")
        return self[attr]

    def __setattr__(self, attr, value):
        if attr not in ('id', 'collocation', 'wordcount', 'freq', 'pnormal_form', 'llinked'):
            raise KeyError("Ключ с таким именем отсутствует в словаре")
        if attr == "collocation":
            self.wordcount = len(value.split(' '))
        self[attr] = value

    def __eq__(self, other):
        if other is None:
            return False
        required_attributes = ('collocation', 'wordcount', 'freq')
        type_check = isinstance(other, Collocation) or (isinstance(other, dict) and all([attr in other for attr in required_attributes]))
        if not type_check:
            return False
        equality_check = self.collocation == other.get('collocation', str()) and \
                         self.freq == other.get('freq', -1) and \
                         self.pnormal_form == other.get('pnormal_form', str())
        return equality_check

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.items():
            setattr(result, k, deepcopy(v, memodict))
        return result
