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

    @property
    def id(self) -> int:
        return self.get('id', 0)

    @id.setter
    def id(self, value: int):
        if not(isinstance(value, int) and value >= 0):
            raise ValueError("Недопустимое значение id")
        self['id'] = value

    @property
    def collocation(self) -> str:
        return self.get('collocation', str())

    @collocation.setter
    def collocation(self, value: str):
        if not (isinstance(value, str) and value != ""):
            raise ValueError("Недопустимое значение словосочетания")
        self['collocation'] = value
        if value != str() and self.wordcount == 0:
            self.wordcount = len(value.split(' '))

    @property
    def wordcount(self) -> int:
        return self.get('wordcount', 0)

    @wordcount.setter
    def wordcount(self, value: int):
        if not (isinstance(value, int) and value >= 0):
            raise ValueError("Недопустимое значение wordcount")
        self['wordcount'] = value

    @property
    def freq(self) -> float:
        return self.get('freq', 0)

    @freq.setter
    def freq(self, value: float):
        if not (isinstance(value, int) and value >= 0):
            raise ValueError("Недопустимое значение wordcount")
        self['freq'] = value

    @property
    def pnormal_form(self) -> str:
        return self.get('pnormal_form', 0)

    @pnormal_form.setter
    def pnormal_form(self, value: str):
        if not (isinstance(value, str)):
            raise ValueError("Недопустимое значение нормальной формы")
        self['pnormal_form'] = value

    @property
    def llinked(self) -> list:
        return self.get('llinked', 0)

    @llinked.setter
    def llinked(self, value: list):
        if not (isinstance(value, list)):
            raise ValueError("Недопустимое значение списка связанных кандидатов")
        self['llinked'] = value

    """
    def __getattr__(self, attr):
        # TODO proper properties instead of this
        if attr not in ('id', 'collocation', 'wordcount', 'freq', 'pnormal_form', 'llinked'):
            raise KeyError("Ключ с таким именем отсутствует в словаре")
        return self[attr]

    def __setattr__(self, attr, value):
        if attr not in ('id', 'collocation', 'wordcount', 'freq', 'pnormal_form', 'llinked'):
            raise KeyError("Ключ с таким именем отсутствует в словаре")
        if attr == "collocation":
            self.wordcount = len(value.split(' '))
        self[attr] = value
    """

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
