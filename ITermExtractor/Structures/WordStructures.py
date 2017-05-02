from collections import namedtuple

TaggedWord = namedtuple('TaggedWord', ['word', 'pos', 'case', 'normalized'])
TaggedWord.__doc__ = "Размеченное слово"
TaggedWord.word.__doc__ = "Слово"
TaggedWord.pos.__doc__ = "Часть речи"
TaggedWord.case.__doc__ = "Падеж"
TaggedWord.normalized.__doc__ = "Нормальная форма слова"


class Collocation(dict):
    # TODO логика сравнивания 2 экземпляров, без id
    """
    Словосочетание со статистическими параметрами
    """

    def __init__(self, cid=0, collocation=str(), wordcount=0, freq=0, pnormal_form=str(), llinked=list()):
        """
        Конструктор класса-словаря
        :param collocation: Словосочетание, строка
        :param wordcount: Количество слов в словосочетании
        :param freq: Количество упоминаний словоформы в исходном корпусе
        :param pnormal_form: Псевдо нормальная форма словосочетания: все слова в норм форме
        :param llinked: Список ссылок на более длинные словосочетаний / те же словоформы
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
