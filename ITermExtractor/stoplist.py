import pickle
import re
import os

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

    def __del__(self):
        if self._use_settings_:
            self.save_setting()

    def open_settings(self):
        try:
            with open(self._path_, 'rb') as fp:
                self._List_ = pickle.load(fp)
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

    def filter(self, candidate_terms: dict) -> dict:
        """
        Фильтрует список терминологических кандидатов в соответствии со стоп-списком
        :param candidate_terms: словарь со списком словосочетаний и частотой их встречаемости
        :return: отфильтрованный словарь терминологических кандидатов

        >>> sl.filter(var_1)

        """
        # TODO удалять из списка при нахождении стоп-слова, не соединять термины
        flag = False in [isinstance(candidate_terms[term], int) and isinstance(term, str) for term in candidate_terms.keys()]
        if flag:
            raise ValueError("Необходим словарь терминов с частотой встречаемости")
        if len(self._List_) == 0:
            return candidate_terms

        edited_terms = dict(candidate_terms)
        for term in edited_terms.keys():
            found = self.find_all(term)
            if len(found) > 0:
                spans = [(m.span()[0], m.span()[1]) for m in found]
                edited_term = remove_spans(term, spans)

                if edited_terms[edited_term] > 0:
                    del edited_terms[term]
                else:
                    edited_terms[edited_term] = edited_terms[term]
        return edited_terms


if __name__ == "__main__":
    import doctest
    path_play = os.path.split(__file__)[0]
    current_dir = os.path.join(path_play, "..")

    os.chdir(current_dir)
    sl = StopList(use_settings=True)
    sl.append_list(["раздел", "УТВЕРЖДАЮ", "подпись"])  # TODO а будет ли удаляться строка (подпись)?
    str_dict_1 = {"трехэтажный дом": 2,
                  "трехэтажный раздел": 1,
                  "артиллерийский огонь": 5,
            }
    doctest.testmod(extraglobs=
                    {'sl': sl,
                     'var_1': str_dict_1
                     })
# TODO test this!

