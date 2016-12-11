import pickle
import re
import os
from typing import List
from ITermExtractor.stat.cvalue import collocation
from operator import itemgetter
from helpers import remove_spans


class StopList(object):
    # TODO приведение в начальную форму

    _path_ = "data/stop-list.pickle"

    def __init__(self, use_settings=False):
        self._List_ = []
        self._use_settings_ = use_settings
        if self._use_settings_:
            exists = os.path.exists(self._path_)
            if not exists:
                raise FileNotFoundError("Путь указывает на несуществующий файл. Использование настроек для стоп-листа невозможно")
            self.open_settings()

    """
    def __del__(self):
        if self._use_settings_:
            self.save_setting()
    """

    def open_settings(self):
        try:
            with open(self._path_, 'rb') as fp:
                self._List_ = pickle.load(fp)
            self._construct_pattern_()
        except EOFError:
            self._List_ = []
            print("Файл со стоп-листом пуст")

    def save_setting(self):
        with open(self._path_, 'wb') as fp:
            pickle.dump(self._List_, fp, pickle.HIGHEST_PROTOCOL)

    def append_item(self, item: str, construct_immediately: bool = True):
        if not isinstance(item, str):
            raise TypeError("Для включения в стоп-список элемента требуется строка")
        if item not in self._List_:
            self._List_.append(item)
            if construct_immediately:
                self._construct_pattern_()

    def append_list(self, item_list: list):
        if not isinstance(item_list, list) and False in [isinstance(item, str) for item in item_list]:
            raise TypeError("Требуется список элементов для влючения в стоп-список")
        if len(item_list) == 0:
            return
        for item in item_list:
            self.append_item(item, False)
        self._construct_pattern_()

    def remove_item(self, item: str):
        if not isinstance(item, str):
            raise TypeError("Для исключения из стоп-списока элемента требуется строка")
        if item in self._List_:
            self._List_.remove(item)
            self._construct_pattern_()

    def _construct_pattern_(self):
        if len(self._List_) == 0:
            return ""
        p_pattern = "\\b\\w*("
        for i in self._List_[0: len(self._List_) - 1]:
            p_pattern += "{0}|".format(i)
        p_pattern += "{0})\\w*\\b".format(self._List_[-1])
        self._Pattern = p_pattern
        return self._Pattern

    def find_all(self, text: str) -> bool:
        infolist = list(re.finditer(self._Pattern, text, re.IGNORECASE))
        return infolist

    def filter(self, candidate_terms: List[collocation]) -> List[collocation]:
        """
        Фильтрует список терминологических кандидатов в соответствии со стоп-списком
        :param candidate_terms: словарь со списком словосочетаний и частотой их встречаемости
        :return: отфильтрованный словарь терминологических кандидатов

        >>> sorted(sl.filter(var_1), key=itemgetter(2), reverse=True)
        [collocation(collocation='артиллерийский огонь', wordcount=2, freq=5), collocation(collocation='наступление года', wordcount=2, freq=5), collocation(collocation='январь', wordcount=1, freq=5), collocation(collocation='трехэтажный дом', wordcount=2, freq=3)]

        """
        # TODO удалять из списка при нахождении стоп-слова, не соединять термины
        flag = False in [isinstance(term, collocation) for term in candidate_terms]
        if flag:
            raise ValueError("Необходим список терминов с частотой встречаемости")
        if len(self._List_) == 0:
            return candidate_terms

        edited_terms = list(candidate_terms)
        for term in edited_terms:
            found = self.find_all(term.collocation)
            if len(found) > 0:
                spans = [(m.span()[0], m.span()[1]) for m in found]
                edited_term = remove_spans(term.collocation, spans)

                existing_nodes = [oterm for oterm in edited_terms if oterm.collocation == edited_term]
                if edited_term != "":
                    if len(existing_nodes) == 0:
                        edited_terms.append(
                            collocation(collocation=edited_term,
                                        freq=term.freq,
                                        wordcount=len(edited_term.split(' '))))
                    else:
                        node = existing_nodes[0]
                        edited_terms.append(
                            collocation(collocation=node.collocation,
                                        freq=term.freq + node.freq,
                                        wordcount=node.wordcount))
                        edited_terms.remove(node)
                    edited_terms.remove(term)
        return edited_terms

    def __str__(self):
        return ' '.join(self._List_)

    def str_column_enumerated(self):
        result = ""
        for index, item in enumerate(self._List_):
            separator = os.linesep if (index + 1) % 3 == 0 else "\t"
            result += "{0}) {1}{2}".format(index + 1, item, separator)
        return result

    def get_by_index(self, no):
        if not 0 <= no < len(self._List_):
            return None
        return self._List_[no]


def demo():
    sl = StopList(use_settings=True)
    print("Действия:")
    choice = -1
    while choice != 0:
        print("1. Вывести стоп-список")
        print("2. Загрузить стоп-список из файла")
        print("3. Записать стоп-список в файл")
        print("4. Добавить элемент")
        print("5. Удалить элемент")
        print("0. Выход")
        try:
            choice = int(input())
        except:
            print("Повторить ввод")
        if choice == 1:
            print(str(sl))
        elif choice == 2:
            sl.open_settings()
            print("Список загружен")
        elif choice == 3:
            sl.save_setting()
            print("Список сохранен")
        elif choice == 4:
            pattern = input()
            sl.append_item(pattern)
            print("Добавлено")
        elif choice == 5:
            print("Выберите номер элемента для удаления, 0 - отмена")
            print(sl.str_column_enumerated())
            while True:
                try:
                    number = int(input())
                    break
                except:
                    print("Повторить ввод")
            if number > 0:
                item = sl.get_by_index(number - 1)
                sl.remove_item(item)
                print("Удалено")
        elif choice == 0:
            pass
        else:
            print("Повторите ввод")
        print()

if __name__ == "__main__":
    import doctest
    path_play = os.path.split(__file__)[0]
    current_dir = os.path.join(path_play, "..")

    os.chdir(current_dir)
    # demo()
    sl = StopList(use_settings=False)
    sl.append_list(["раздел", "УТВЕРЖДАЮ", "подпись", "г"])  # TODO а будет ли удаляться строка (подпись)?
    str_list = [
        collocation(collocation="трехэтажный дом", wordcount=2, freq=2),
        collocation(collocation="трехэтажный раздельный дом", wordcount=3, freq=1),
        collocation(collocation="артиллерийский огонь", wordcount=2, freq=5),
        collocation(collocation="наступление года", wordcount=2, freq=5),
        collocation(collocation="январь г", wordcount=2, freq=5)
    ]
    doctest.testmod(extraglobs=
                    {'sl': sl,
                     'var_1': str_list
                     })
