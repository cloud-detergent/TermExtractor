import math
import helpers
import ITermExtractor.Morph as m
from ITermExtractor.Structures.PartOfSpeech import PartOfSpeech
from typing import List, Dict
from operator import itemgetter
from ITermExtractor.Structures.WordStructures import collocation, TaggedWord
import multiprocessing
import logging

LIMIT_PER_PROCESS = 80
# TODO общие структуры вынести в отдельный модуль


class LinguisticFilter(object):
    """
    Абстрактный родительский класс лингвистического фильтра,
     содержащий методы установления соответствия фразы данному фильтру
      и фильтрации предложения/словосочетания
    """

    _limit = 5; """Магическое значение максимальной длины термина, выраженной в количестве слов"""

    def filter_text(self, sentences: List[List[TaggedWord]], is_single_threaded: bool = False) -> List[collocation]:
        """
        Извлечение терминологических кандидатов из текста, разбитого на предложения
        :param sentences: предложения
        :param is_single_threaded: флаг, True - выполнять в одном потоке
        :return: словарь терминологических кандидатов с количеством встречаемости
        """
        if not isinstance(sentences, list):
            raise TypeError('Необходим список предложений')
        if len(sentences) == 0:
            return []
        total_count = len(sentences)
        logger = logging.getLogger()
        logger.info("Фильтрация фильтром {0}".format(str(type(self))))
        logger.info("Всего предложений {0}".format(total_count))
        for sentence in sentences:
            self.filter(sentence=sentence, append_mode=True)
        logger.info("Предложения обработаны, переходим к соединению одинаковых ключей")

        word_list = [(word.word, word) for sentence in sentences for word in sentence]  # Get the list of all word tags
        corrected_candidate_terms = parallel_conjugation(dict(word_list), self._candidate_terms_, is_single_threaded)
        logger.info("Перечень терминологических кандидатов построен (всего {1}/{0})".format(len(self._candidate_terms_), len(corrected_candidate_terms)))
        logger.info("Сортировка результата по частоте")
        corrected_candidate_terms = LinguisticFilter.sort_by_wordcount(corrected_candidate_terms)
        logger.info("Список отсортирован")
        return corrected_candidate_terms

    @staticmethod
    def sort_by_wordcount(input_list: List[collocation]) -> List[collocation]:
        result = sorted(input_list, key=itemgetter(1), reverse=True)
        return result

    def filter(self, sentence: List[TaggedWord], append_mode: bool = False) -> List[collocation]:
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
        if not isinstance(sentence, list) or False in [isinstance(word, TaggedWord) for word in sentence]:
            raise TypeError("Необходим список слов из предложения")
        for word in sentence:  # все некорректные слова выкидываем за борт
            if not helpers.is_correct_word(word.word) or str.isspace(word.word) or word.word == '':
                sentence.remove(word)

        min_wlimit = self.pattern.get_col_min_word_limit()
        max_wlimit = self.pattern.get_col_max_word_limit()
        max_wlimit = max_wlimit if max_wlimit <= self._limit else self._limit

        if len(sentence) < min_wlimit:
            # logging.debug("В предложении слишком мало слов {0}".format(len(sentence)))  # TODO доп фильтрация на уровне извлечения предложений
            return self._candidate_terms_ if append_mode else []
        if len(sentence) < max_wlimit:
            # logging.debug("{0} сл. < {1} сл., уменьшаем верхнюю границу".format(len(sentence), max_wlimit))
            max_wlimit = len(sentence)

        if not append_mode:
            self._candidate_terms_ = []

        # TODO почему-то выделяются ' налетами', 'открытия '
        for word_count in range(max_wlimit, min_wlimit - 1, -1):
            for i in range(0, len(sentence) - word_count + 1):  # извлечение словосочетаний, длиной от 2 слов и более
                candidate_term = sentence[i:i+word_count]
                candidate_term_collocation = ' '.join([word[0] for word in candidate_term])

                already_existing_indices = [i for i, term in enumerate(self._candidate_terms_)
                            if term.collocation.lower() == candidate_term_collocation.lower()]
                is_appended = len(already_existing_indices) >= 1
                if is_appended:
                    index = already_existing_indices[0]
                    tmp = self._candidate_terms_[index][:2] + (self._candidate_terms_[index].freq + 1,)
                    self._candidate_terms_[index] = collocation(*tmp)
                else:
                    flag = self.match(candidate_term)
                    if flag:
                        self._candidate_terms_.append(collocation(
                                        collocation=candidate_term_collocation,
                                        wordcount=len(candidate_term),
                                        freq=1))
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


class AdjNounReducedLinguisticFilter(LinguisticFilter):
    """Модифицированный вариант фильтра Adj|Noun для метода k-factor"""
    def __init__(self):
        token_1 = FilterPatternToken(PartOfSpeechStruct([PartOfSpeech.adjective, PartOfSpeech.noun], "|"), 1, 1)
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
        elif len(self.pattern) == 2:  # костылеподобно
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
        if False in check_list:
            raise ValueError("Необходим список слов, упакованных в кортежи TaggedWord")
        word_length = len([True for word in phrase if len(word) > 1])
        count_flag = self.min_count <= word_length <= self.max_count  # len(phrase)
        pos_flag = True

        pos_check_list = [self.POS.match(word.pos) for word in phrase]
        for check_list in pos_check_list:
            pos_flag &= check_list

        return pos_flag & count_flag  # , pos_check_list


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


def parallel_conjugation(word_dict: Dict[str, TaggedWord], candidate_list: List[collocation],
                         is_single_threaded: bool = False) -> List[collocation]:
    logging.info("Разделяем на потоки")
    spliced_candidate_list = split_tasks(candidate_list)
    args = list(zip([word_dict for i in range(len(spliced_candidate_list))], spliced_candidate_list))
    if not is_single_threaded:
        logging.debug("Разделили аргументы по задачам ({0})".format(len(args)))
        with multiprocessing.Pool(processes=len(args)) as pool:
            result = pool.starmap(conjugate, args)
        grouped_result = [element for line in result for element in line]
    else:
        grouped_result = []
        for arg in args:
            grouped_result += conjugate(arg[0], arg[1])
    logging.debug("Готовы результаты обработки")
    return grouped_result

# TODO adj\noun фильтр, collocation вперемешку с TaggedWord, как?


def conjugate(word_dict: Dict[str, TaggedWord], candidates_list: List[collocation]) -> List[collocation]:
    """
    Сопоставляет одни и те же словосочетания в разных словоформах и суммирует в итоговом списке терминологических кандидатов их частоты встречаемости
    :param word_dict: словарь размеченных слов, встреченных в заданном тексте
    :param candidates_list: список терминологических кандидатов
    :return: словарь терминологических кандидатов
    """
    # TODO соединять ключи словаря, отличающиеся друг от друга склонением и
    # TODO регистром !!!
    # TODO желательно приводить в норм форму
    # todo отсеивать словосочетания со словом в 1 букву

    joined_form_list = []
    local_sorted_key_list = [([word_dict[word] for word in term.collocation.split(" ")])
                             for term in candidates_list]

    for key_tag in local_sorted_key_list:
        element_matches = m.count_includes(key_tag, local_sorted_key_list)
        if len(element_matches) == 1:
            match_index = element_matches[0][0]
            joined_form_list.append(candidates_list[match_index])
        else:
            normal_form_local_index = m.get_collocation_normal_form([element[1] for element in element_matches])
            if normal_form_local_index != -1:
                base_index = element_matches[normal_form_local_index][0]
            else:
                base_index = element_matches[0][0]

            base_key = local_sorted_key_list[base_index]
            if base_key not in joined_form_list:
                remaining_keys = [element[0] for element in element_matches
                                  if element[0] != base_index]
                col = ' '.join([key.word for key in base_key])
                summary_freq = sum(candidates_list[key].freq for key in remaining_keys)
                wordcount = len(key_tag)
                joined_form_list.append(collocation(collocation=col, wordcount=wordcount, freq=summary_freq))

        for i, lst in reversed(element_matches):
            del local_sorted_key_list[i]
    return joined_form_list


def split_tasks(task_list: List[collocation]):
    """
    Разделяет список на несколько для равномерного разделения процессов на параллельные потоки
    :param task_list: входной список
    :return: разделенный список
    """
    sorted_list = sorted(task_list, key=itemgetter(1, 0))
    length = len(sorted_list)
    threads = 1
    if length > LIMIT_PER_PROCESS:
        threads = int(length / 80) + 1
    if threads == 1:
        split_list = [sorted_list]
    else:
        split_list = [sorted_list[LIMIT_PER_PROCESS * i:LIMIT_PER_PROCESS * (i + 1)] for i in range(threads)]
    return split_list
