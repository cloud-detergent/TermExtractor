from ITermExtractor.PartOfSpeech import POSNameConverter, PartOfSpeech
from helpers import concat_words
import math


class LinguisticFilter(object):
    """
    Абстрактный родительский класс лингвистического фильтра,
     содержащий методы установления соответствия фразы данному фильтру
      и фильтрации предложения/словосочетания
    """

    _limit = 5; """Магическое значение максимальной длины термина, выраженной в количестве слов"""

    def filter(self, sentence: list) -> dict:
        """
        Из входного предложения отсеивает терминологические кандидаты
        :param sentence: предложение/словосочетание, список из кортежей (слово, часть речи)
        :return: словарь терминологических кандидатов с количеством встречаемости
        """
        # прогонять по списку токенов, по-элементно прогонять слова из предложения
        # TODO протестировать методы
        min_wlimit = self.pattern.get_col_min_word_limit()
        max_wlimit = self.pattern.get_col_max_word_limit()
        max_wlimit = max_wlimit if max_wlimit <= self._limit else self._limit
        candidate_terms = {}

        for wcount in range(max_wlimit, min_wlimit -1, -1):
            # print("Ищем термины длиной в {0} слова".format(wcount))
            for i in range(0, len(sentence) - wcount + 1):
                candidate_term = sentence[i:i+wcount]
                candidate_term_collocation = concat_words([word[0] for word in candidate_term])
                if candidate_term_collocation in candidate_terms.keys():
                    candidate_terms[candidate_term_collocation] += 1
                else:
                    flag = self.match(candidate_term)
                    if flag:
                        candidate_terms[candidate_term_collocation] = 1
        return candidate_terms

    def match(self, phrase):
        return self.pattern.match(phrase)


class NounPlusLinguisticFilter(LinguisticFilter):
    _filter_pattern = "Noun+Noun"

    def __init__(self):
        self.pattern = FilterPatternConjuction([FilterPatternToken(PartOfSpeech.noun, 2, math.inf)])


class AdjNounLinguisticFilter(LinguisticFilter):
    def __init__(self):
        token_1 = FilterPatternToken(PartOfSpeechStruct([PartOfSpeech.adjective, PartOfSpeech.noun], "|"), 1, math.inf)
        token_2 = FilterPatternToken(PartOfSpeech.noun, 1)
        self.pattern = FilterPatternConjuction([token_1, token_2])


class FilterPatternConjuction(object):
    def __init__(self, tokens: list):
        check_list = [isinstance(token, FilterPatternToken) for token in tokens]
        if False in check_list or len(tokens) == 0:
            raise ValueError("Требуется список токенов FilterPatternToken")
        self.pattern = list(tokens)
        self.__iscomplex__ = len(tokens) > 1

    def get_col_min_word_limit(self):
        min_word_limit = sum(token.min_count for token in self.pattern)
        return min_word_limit

    def get_col_max_word_limit(self):
        max_word_limit = sum(token.max_count for token in self.pattern)
        return max_word_limit

    def match(self, phrase: list) -> bool:
        # проверка с конца, как правило в шаблонах последний токен требует 1 вхождение
        # TODO обновить, переписать метод установления соответствия
        check_flag = False in [isinstance(element, tuple) and isinstance(element[0], str) and isinstance(element[1], PartOfSpeech) for element in phrase]
        if check_flag:
            raise ValueError("Необходим список кортежей(строка, часть речи)")

        flag = False
        if not self.__iscomplex__:
            flag = self.pattern[0].match(phrase)
        elif len(self.pattern) == 2: # костылеподобно
            flag |= self.pattern[1].match([phrase[-1]])
            flag &= self.pattern[0].match(phrase[0: len(phrase)-1])
        return flag


class FilterPatternToken(object):
    """
    Элемент шаблона лингвистического фильтра
    """

    def __init__(self, pos, min_count=0, max_count=1):
        """
        :param pos: PartOfSpeechStruct or PartOfSpeech
        :param min_count: x>=0
        :param max_count: 1<=x<math.inf
        """
        if not isinstance(pos, PartOfSpeechStruct) and not isinstance(pos, PartOfSpeech):
            raise ValueError("Требуется аргумент типа PartOfSpeech или PartOfSpeechStruct")
        if max_count < min_count:
            raise ValueError("Максимальное количество вхождений не может быть меньше минимального количества вхождений")
        if max_count <= 0 or min_count < 0:
            raise ValueError("Недопустимые значения аргументов")

        if isinstance(pos, PartOfSpeech):
            pos = PartOfSpeechStruct(pos)
        self.POS = pos
        self.min_count = min_count
        self.max_count = max_count

    def match(self, phrase: list) -> bool:
        """
        Сравнивает соответствие частей речи в фразе
        :param phrase: словосочетание
        :return: финальный вердикт и список соответствия шаблону
        """

        check_list = [isinstance(word, tuple) and isinstance(word[0], str) and isinstance(word[1], PartOfSpeech) for word in phrase]
        #var1 = [not p for p in check_list]
        if False in check_list:
            raise ValueError("Необходим список слов, состоящий из 2 компонентов: слова и его части речи")
        count_flag = self.min_count <= len(phrase) <= self.max_count
        pos_flag = True

        pos_check_list = [self.POS.match(word[1]) for word in phrase]
        for check_list in pos_check_list:
            pos_flag &= check_list

        return pos_flag & count_flag#, pos_check_list


class PartOfSpeechStruct:
    """
    структура, описывающая тип токена
    Может представлять одну часть речи (Noun, Prep, ...)
    Или же сложные конструкции типа ( Adj|Noun )
    """

    def __init__(self, pos_list, operation=""):
        """
        Конструктор принимающий список токенов частей речи и тип операции между ними
        :param pos_list: список частей речи
        :param operation: операция между токенами, как правило, | ( Adj | Noun )
        """
        if isinstance(pos_list, PartOfSpeech):
            pos_list = [pos_list]
        if not isinstance(pos_list, list):
            raise ValueError("Требуется аргумент типа список")

        check_list = [isinstance(pos, PartOfSpeech) for pos in pos_list]
        if False in check_list:
            raise ValueError("Требуется аргумент типа список объектов PartOfSpeech")

        if len(pos_list) > 1 and operation == "":
            raise ValueError("Необходимо указать тип операции между частями речи в шаблоне")

        self.pos_list = pos_list
        self.operation = operation

    def match(self, pos: PartOfSpeech) -> bool:
        """
        Устанавливает соответствие части речи шаблону
        :param pos: часть речи
        :return: да/нет
        """
        flag = False
        if len(self.pos_list) == 1:
            flag = pos == self.pos_list[0]
        else:
            for pos_fl in self.pos_list:
                flag |= pos == pos_fl
        return flag


# парсер выражений, может быть? как регулярка, только с частями речи
# Noun+Noun   (Adj|Noun)+Noun
if __name__ == "__main__":
    import Runner
    #pattern = FilterPatternToken(PartOfSpeech.noun, 2, math.inf)
    filter1 = NounPlusLinguisticFilter()
    filter2=AdjNounLinguisticFilter()

    phrases = ["огонь минометов", "минометный батальон", "стрелковый полк"]
    tagged_phrases = [Runner.tag_collocation(phrase, point='../') for phrase in phrases]
    for phrase in tagged_phrases:
        result1 = filter1.match(phrase)
        result2 = filter2.match(phrase)
        print("Фраза {0} {1} и {2}".format(phrase, "соответствует" if result1 else "не подходит", "соответствует" if result2 else "не подходит"))