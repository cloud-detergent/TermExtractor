import math
import helpers
import ITermExtractor.Morph as m
from ITermExtractor.Structures.PartOfSpeech import PartOfSpeech
import logging
from typing import Any, List
from ITermExtractor.Morph import TaggedWord
from ITermExtractor.stat.cvalue import collocation_tuple


class LinguisticFilter(object):
    """
    Абстрактный родительский класс лингвистического фильтра,
     содержащий методы установления соответствия фразы данному фильтру
      и фильтрации предложения/словосочетания
    """

    _limit = 5; """Магическое значение максимальной длины термина, выраженной в количестве слов"""

    # TODO redo type hints,
    def filter_text(self, sentences: List[List[TaggedWord]]) -> List[collocation_tuple]:
        """
        Извлечение терминологических кандидатов из текста, разбитого на предложения
        :param sentences: предложения
        :return: словарь терминологических кандидатов с количеством встречаемости
        """
        if not isinstance(sentences, list):
            raise TypeError('Необходим список предложений')
        if len(sentences) == 0:
            return []
        total_count = len(sentences)
        current_no = 0
        logger = logging.getLogger()
        logger.info("Фильтрация фильтром {0}".format(str(type(self))))
        for sentence in sentences:
            self.filter(sentence=sentence, append_mode=True)
            current_no += 1
            logger.debug("Обработано {0}/{1} предложение".format(current_no, total_count))
        return self._candidate_terms_

    def filter(self, sentence: List[TaggedWord], append_mode: bool = False) -> List[collocation_tuple]:
        """
        Из входного предложения отсеивает терминологические кандидаты
        :param sentence: предложение/словосочетание, список из кортежей (слово, часть речи)
        :param append_mode: флаг, показывающий добавлять ли термины в существующий список или нет
        :return: словарь терминологических кандидатов с количеством встречаемости
#  Основная задача его заключается в непосредственной поддержке стрелковых рот и сопровождении их огнем и движением
        >>> sent_info = m.tag_collocation('Минометный батальон (дивизион) является мощным огневым средством пехоты во всех видах ее боевой деятельности')
        >>> sorted(nlf.filter(sent_info))
        [('боевой деятельности', 1), ('огневым средством', 1), ('огневым средством пехоты', 1), ('средством пехоты', 1)]

        >>> sorted(alf.filter(sent_info))
        [('Минометный батальон', 1), ('боевой деятельности', 1), ('всех видах', 1), ('мощным огневым', 1), ('мощным огневым средством', 1), ('мощным огневым средством пехоты', 1), ('огневым средством', 1), ('огневым средством пехоты', 1), ('средством пехоты', 1)]
        """
        # прогонять по списку токенов, по-элементно прогонять слова из предложения
        # TODO протестировать методы
        if not isinstance(sentence, list) or False in [isinstance(word, TaggedWord) for word in sentence]:
            raise TypeError("Необходим список слов из предложения")
        for word in sentence:  # все некорректные слова выкидываем за борт
            if not helpers.is_correct_word(word.word):
                sentence.remove(word)

        min_wlimit = self.pattern.get_col_min_word_limit()
        max_wlimit = self.pattern.get_col_max_word_limit()
        max_wlimit = max_wlimit if max_wlimit <= self._limit else self._limit
        if not append_mode:
            self._candidate_terms_ = []
        #len(sentence)
        # TODO ограничивать потолок количества слов кол-вом слов в предложении
        for word_count in range(max_wlimit, min_wlimit - 1, -1):
            for i in range(0, len(sentence) - word_count + 1):  # извлечение словосочетаний, длиной от 2 слов и более
                candidate_term = sentence[i:i+word_count]
                candidate_term_collocation = ' '.join([word[0] for word in candidate_term])
                try:
                    element_id = m.in_collocation_list(candidate_term, self._candidate_terms_)
                    # TODO ввести в collocation_tuple лист с тегами
                except ValueError as e:
                    logging.error("Ошибка при фильтрации предложения {0}".format(e))
                    continue

                if element_id is not None:
                    self._candidate_terms_[element_id].freq += 1
                else:
                    flag = self.match(candidate_term)
                    if flag:
                        self._candidate_terms_.append(collocation_tuple(collocation=candidate_term_collocation, wordcount=len(candidate_term), freq=1))
        return self._candidate_terms_

    def match(self, phrase):
        return self.pattern.match(phrase)


class NounPlusLinguisticFilter(LinguisticFilter):
    _filter_pattern = "Noun+Noun"

    def __init__(self):
        self.pattern = FilterPatternConjuction([FilterPatternToken(PartOfSpeech.noun, 2, math.inf)])
        self._candidate_terms_ = []


class AdjNounLinguisticFilter(LinguisticFilter):
    def __init__(self):
        token_1 = FilterPatternToken(PartOfSpeechStruct([PartOfSpeech.adjective, PartOfSpeech.noun], "|"), 1, math.inf)
        token_2 = FilterPatternToken(PartOfSpeech.noun, 1)
        self.pattern = FilterPatternConjuction([token_1, token_2])
        self._candidate_terms_ = []


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

    def match(self, phrase: List[TaggedWord]) -> bool:
        # проверка с конца, как правило в шаблонах последний токен требует 1 вхождение
        # TODO обновить, переписать метод установления соответствия
        check_flag = False in [isinstance(element, m.TaggedWord) for element in phrase]
        if check_flag:
            raise ValueError("Необходим список кортежей(строка, часть речи)")

        flag = False
        if not self.__iscomplex__:
            flag = self.pattern[0].match(phrase)
        elif len(self.pattern) == 2: # костылеподобно
            flag |= self.pattern[1].match([phrase[-1]])
            flag &= self.pattern[0].match(phrase[0: len(phrase) - 1])
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

    def match(self, phrase: List[TaggedWord]) -> bool:
        """
        Сравнивает соответствие частей речи в фразе
        :param phrase: словосочетание
        :return: финальный вердикт и список соответствия шаблону
        """

        check_list = [isinstance(word, m.TaggedWord) for word in phrase]
        #var1 = [not p for p in check_list]
        if False in check_list:
            raise ValueError("Необходим список слов, упакованных в кортежи TaggedWord")
        count_flag = self.min_count <= len(phrase) <= self.max_count
        pos_flag = True

        pos_check_list = [self.POS.match(word.pos) for word in phrase]
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
    import doctest
    doctest.testmod(extraglobs=
                    {'nlf': NounPlusLinguisticFilter(),
                     'alf': AdjNounLinguisticFilter(),
                     })
    '''
    import Runner
    #pattern = FilterPatternToken(PartOfSpeech.noun, 2, math.inf)
    filter1 = NounPlusLinguisticFilter()
    filter2 = AdjNounLinguisticFilter()

    phrases = ["огонь минометов", "минометный батальон", "стрелковый полк"]
    tagged_phrases = [Runner.tag_collocation(phrase, point='../') for phrase in phrases]
    for phrase in tagged_phrases:
        result1 = filter1.match(phrase)
        result2 = filter2.match(phrase)
        print("Фраза {0} {1} и {2}".format(phrase, "соответствует" if result1 else "не подходит", "соответствует" if result2 else "не подходит"))
    '''