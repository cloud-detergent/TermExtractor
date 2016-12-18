from collections import namedtuple

collocation = namedtuple('collocation', ['collocation', 'wordcount', 'freq'])
collocation.__doc__ = "Словосочетание со статистическими параметрами"
collocation.collocation.__doc__ = "Словосочетание, строка"
collocation.wordcount.__doc__ = "Количество слов в словосочетании"
collocation.freq.__doc__ = "Частота встречаемости в исходном корпусе"

TaggedWord = namedtuple('TaggedWord', ['word', 'pos', 'case', 'normalized'])
TaggedWord.__doc__ = "Размеченное слово"
TaggedWord.word.__doc__ = "Слово"
TaggedWord.pos.__doc__ = "Часть речи"
TaggedWord.case.__doc__ = "Падеж"
TaggedWord.normalized.__doc__ = "Нормальная форма слова"
