import pickle
import re

from helpers import remove_spans


class StopList(object):
    # TODO приведение в начальную форму

    _path_ = "data/stop-list.pickle"

    def __init__(self, use_settings=False):
        self.List = []
        self._use_settings = use_settings
        if self._use_settings:
            self.open_settings()

    def __delete__(self, instance):
        if instance._use_settings:
            instance.save_setting()

    def open_settings(self):
        fp = open(self._path_, 'rb')
        self.List = pickle.load(fp)
        fp.close()

    def save_setting(self):
        fp = open(self._path_, 'wb')
        pickle.dump(self.List, fp, pickle.HIGHEST_PROTOCOL)
        fp.close()

    def _construct_pattern_(self):
        # TODO добавить слот, отслеживать изменение self.List и вызывать сей метод
        if len(self.List) == 0:
            return ""
        p_pattern = "\\b\\w*("
        for i in self.List[0: len(self.List) - 1]:
            p_pattern += "{0}|".format(i)
        p_pattern += "{0})\\w*\\b".format(self.List[-1])
        self._Pattern = p_pattern
        return self._Pattern

    def match(self, text: str) -> bool:
        infolist = list(re.finditer(self._Pattern, text, re.IGNORECASE))
        return infolist

    def filter(self, candidate_terms: dict) -> str:
        # TODO удалять из списка при нахождении стоп-слова, не соединять термины
        flag = False in [isinstance(candidate_terms[term], int) and isinstance(term, str) for term in candidate_terms.keys()]
        if flag:
            raise ValueError("Необходим словарь терминов с частотой встречаемости")
        if len(self.List) == 0:
            return candidate_terms

        edited_terms = dict(candidate_terms)
        for term in edited_terms.keys():
            found = self.match(term)
            if len(found) > 0:
                spans = [(m.span()[0], m.span()[1]) for m in found]
                edited_term = remove_spans(term, spans)

                if edited_terms[edited_term] > 0:
                    del edited_terms[term]
                else:
                    edited_terms[edited_term] = edited_terms[term]
        return edited_terms

if __name__ == "__main__":
    sl = StopList()
    sl.List.append("весел")
    pattern = sl._construct_pattern_()
    istr = {"трехэтажный дом": 2,
            "веселый трехэтажный дом": 1,
            "артиллерийский огонь": 5,
            }
    #match_list = sl.match(istr)
    #print(pattern, match_list)
    filtered_list = sl.filter(istr)
    print(filtered_list)


