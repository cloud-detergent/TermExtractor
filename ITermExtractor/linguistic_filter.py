import math
import helpers
import ITermExtractor.Morph as m
import multiprocessing
import logging
import copy

from ITermExtractor.Structures.Case import Case
from ITermExtractor.Structures.PartOfSpeech import PartOfSpeech
from typing import List, Dict, Tuple
from operator import itemgetter
from ITermExtractor.Structures.WordStructures import Collocation, TaggedWord, Separator
from itertools import groupby
from Tests.linguistic_filter import is_integral

LIMIT_PER_PROCESS = 80
# TODO общие структуры вынести в отдельный модуль


class LinguisticFilter(object):
    """
    Абстрактный родительский класс лингвистического фильтра,
     содержащий методы установления соответствия фразы данному фильтру
      и фильтрации предложения/словосочетания
    """

    _limit = 5; """Магическое значение максимальной длины термина, выраженной в количестве слов"""

    # TODO на каком-то этапе валится целостность по ссылкам. Заменяются?
    def filter_text(self, sentences: List[List[TaggedWord]], is_single_threaded: bool = False) -> List[Collocation]:
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
        logger = logging.getLogger()
        logger.info("Фильтрация фильтром {0}".format(str(type(self))))
        logger.info("Всего предложений {0}".format(len(sentences)))

        candidate_terms = list()
        for sentence in sentences:
            candidate_terms = candidate_terms + self.filter(sentence=sentence)
        logger.info("Предложения обработаны, переходим к соединению одинаковых ключей")

        cache = []
        for s in sentences:
            for sentence_part in s:
                if isinstance(sentence_part, Separator) or sentence_part is None:
                    continue
                word = sentence_part
                case = Case.nominative if word.pos in [PartOfSpeech.noun, PartOfSpeech.adjective] else word.case
                normal_word = TaggedWord(word=word.normalized, pos=word.pos, case=case, normalized=word.normalized)
                cache.append(normal_word) # `"большой" - потерялись теги
        tag_cache = dict([(c.normalized, c) for c in cache])

        prev_length = len(candidate_terms)
        logger.info("Предложения обработаны, соединяем схожие словоформы")
        candidate_terms = concatenate_similar(tag_cache, candidate_terms)
        # corrected_candidate_terms = parallel_conjugation(dict(tag_cache), candidate_terms, is_single_threaded)
        logger.info("Перечень терминологических кандидатов построен (всего {1}/{0})".format(prev_length, len(candidate_terms)))

        logger.info("Расставляем ссылки, вложенные термины")
        candidate_terms = define_collocation_links(candidate_terms)
        logger.info("Сортировка результата по длине словосочетания")
        candidate_terms = sorted(candidate_terms, key=itemgetter('wordcount'), reverse=True)
        logger.info("Список отсортирован")
        return candidate_terms

    def filter(self, sentence: List[TaggedWord and Separator]) -> List[Collocation]:
        """
        Из входного предложения отсеивает терминологические кандидаты
        :param sentence: предложение/словосочетание, список из кортежей (слово, часть речи)
        :param append_mode: флаг, показывающий добавлять ли термины в существующий список или нет
        :return: словарь терминологических кандидатов с количеством встречаемости
        """
        # прогонять по списку токенов, по-элементно прогонять слова из предложения
        if not isinstance(sentence, list):
            raise TypeError("Необходим список слов из предложения")
        if None in sentence:
            sentence = [p for p in sentence if p is not None]
        check_list = [isinstance(sentence_part, TaggedWord) or isinstance(sentence_part, Separator)
                      for sentence_part in sentence]
        if False in check_list:
            false_index = check_list.index(False) if False in check_list else 0
            raise TypeError("Необходим список слов из предложения", len(sentence),
                            False in check_list, false_index, sentence[false_index], sentence)

        for sentence_part in sentence:  # все некорректные слова выкидываем за борт
            if isinstance(sentence_part, Separator):
                continue
            word = sentence_part

            if not helpers.is_correct_word(word.word) or str.isspace(word.word) or word.word == '':
                sentence.remove(word)

        candidate_terms = list()

        min_wlimit = self.pattern.get_col_min_word_limit()
        max_wlimit = self.pattern.get_col_max_word_limit()
        max_wlimit = max_wlimit if max_wlimit <= self._limit else self._limit

        if len(sentence) < min_wlimit:
            return list()
        if len(sentence) < max_wlimit:
            max_wlimit = len(sentence)

        for word_count in range(max_wlimit, min_wlimit - 1, -1):
            for i in range(0, len(sentence) - word_count + 1):  # извлечение словосочетаний, длиной от 2 слов и более
                candidate_term = retrieve_collocation(sentence, i, word_count)
                if len(candidate_term) < word_count:
                    continue

                candidate_term_collocation = ' '.join([word[0] for word in candidate_term]).lower()
                pseudo_normal_form = ' '.join([word.normalized for word in candidate_term]).lower()
                if candidate_term_collocation.isupper():
                    candidate_term_collocation = candidate_term_collocation.lower()

                already_existing_indices = [i for i, term in enumerate(candidate_terms)
                            if term.collocation.lower() == candidate_term_collocation.lower()]
                is_appended = len(already_existing_indices) >= 1
                if is_appended:
                    index = already_existing_indices[0]
                    candidate_terms[index].add_freq()
                else:
                    flag = self.match(candidate_term)
                    if flag:
                        candidate_terms.append(Collocation(
                                        collocation=candidate_term_collocation,
                                        wordcount=len(candidate_term),
                                        freq=1,
                                        pnormal_form=pseudo_normal_form))
        return candidate_terms

    def match(self, phrase):
        return self.pattern.match(phrase)


class NounPlusLinguisticFilter(LinguisticFilter):
    _filter_pattern = "Noun+Noun"

    def __init__(self):
        self.pattern = FilterPatternConjuction([FilterPatternToken(PartOfSpeech.noun, 1, math.inf)])


class AdjNounLinguisticFilter(LinguisticFilter):
    def __init__(self):
        token_1 = FilterPatternToken(PartOfSpeechStruct([PartOfSpeech.adjective, PartOfSpeech.noun], "|"), 0, math.inf)
        token_2 = FilterPatternToken(PartOfSpeech.noun, 1)
        self.pattern = FilterPatternConjuction([token_1, token_2])


class AdjNounReducedLinguisticFilter(LinguisticFilter):
    """Модифицированный вариант фильтра Adj|Noun для метода k-factor"""
    def __init__(self):
        token_1 = FilterPatternToken(PartOfSpeechStruct([PartOfSpeech.adjective, PartOfSpeech.noun], "|"), 1, 1)
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

    def match(self, phrase: List[TaggedWord]) -> bool:
        # проверка с конца, как правило в шаблонах последний токен требует 1 вхождение
        check_flag = False in [isinstance(element, m.TaggedWord) for element in phrase]
        if check_flag:
            raise ValueError("Необходим список кортежей(строка, часть речи)")
        if len(phrase) == 0:
            return False
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


def set_ids(collocations: List[Collocation]) -> List[Collocation]:
    for collocation in collocations:
        collocation.id = id(collocation)
    return collocations


def concatenate_similar(word_dict: Dict[str, TaggedWord], collocations: List[Collocation]) -> List[Collocation]:
    """
    http://stackoverflow.com/a/3749740 - группировка
    Группирует схожие словоформы
    :param word_dict: кэш слов, ранее обработанных pymorphy
    :param collocations: полученные прежде словосочетания
    :return: список словосочетания, соединенных в одну словоформу
    """
    collocations = set_ids(collocations)
    grouped_collocations = {}
    collocations = sorted(collocations, key=itemgetter('pnormal_form'))
    for key, value_sitter in groupby(collocations, key=itemgetter('pnormal_form')):
        grouped_collocations[key] = list(value_sitter)

    final_list = []
    for key, c_vars in grouped_collocations.items():
        index = 0
        if len(c_vars) > 1:
            tagged_pnormal_collocation = [word_dict.get(word, word) for word in key.split(' ')]
            if len(tagged_pnormal_collocation) == 1:
                c_vars[index].collocation = c_vars[index].pnormal_form
            elif len(tagged_pnormal_collocation) == 2:
                variant = m.get_biword_coll_normal_form(tagged_pnormal_collocation)
                c_vars[index].collocation = variant
            elif len(tagged_pnormal_collocation) > 2:  # TODO добавить +1 слово, где главное заменено на норм форму
                main_word = m.get_main_word(tagged_pnormal_collocation)
                new_var = m.replace_main_word(c_vars[0], main_word)
                c_vars.append(new_var)
                index = m.get_collocation_normal_form(key, c_vars, main_word)

            updated_freq = sum([c.freq for c in c_vars])
            c_vars[index].freq = updated_freq
        final_list.append(c_vars[index])
    return final_list


# TODO или в отдельный модуль
def define_collocation_links(collocations: List[Collocation]) -> List[Collocation]:
    """
    Определение списка более длинных словосочетаний
    :param collocations: сзвлеченные словосочетания
    :return: обновленный список словосочетаний + ссылки
    """
    grouped_by_len = {}
    lengths = []
    cloned = copy.deepcopy(collocations)
    sorted_collocations = sorted(cloned, key=itemgetter('wordcount'))
    collocations_dict = dict([(c.id, c) for c in sorted_collocations])

    for key, value_sitter in groupby(sorted_collocations, key=itemgetter('wordcount')):
        grouped_by_len[key] = list(value_sitter)
        lengths.append(key)

    lengths = sorted(lengths)
    for curr_len in lengths:
        for collocation in list(grouped_by_len[curr_len]):
            query_key = collocation.pnormal_form
            containers = []
            for j in range(curr_len, len(lengths)):  # выборка всех словосочетаний, содержащих query_key
                containers = containers + [hl_coll for hl_coll in grouped_by_len[lengths[j]]
                                   if query_key in hl_coll.pnormal_form]
            collocations_dict[collocation.id].llinked = [c.id for c in containers]  # вот они, ссылки
    return list(collocations_dict.values())


# TODO obsolete
def parallel_conjugation(word_dict: Dict[str, TaggedWord], candidate_list: List[Collocation],
                         is_single_threaded: bool = False) -> List[Collocation]:
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

# TODO adj-noun фильтр, collocation вперемешку с TaggedWord, как?


def conjugate(word_dict: Dict[str, TaggedWord], candidates_list: List[Collocation]) -> List[Collocation]:
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
    local_sorted_key_list = [([word_dict.get(word, None) for word in term.collocation.split(" ")])
                             for term in candidates_list]

    # if None in local_sorted_key_list:
    local_sorted_key_list = list(filter(lambda a: a is not None, local_sorted_key_list))

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
                if None in base_key:
                    continue
                remaining_keys = [element[0] for element in element_matches
                                  if element[0] != base_index]
                col = ' '.join([key.word for key in base_key])
                summary_freq = sum(candidates_list[key].freq for key in remaining_keys)
                wordcount = len(key_tag)
                joined_form_list.append(Collocation(collocation=col, wordcount=wordcount, freq=summary_freq))

        for i, lst in reversed(element_matches):
            del local_sorted_key_list[i]
    return joined_form_list


def split_tasks(task_list: List[Collocation]):
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


def retrieve_collocation(sentence: List[TaggedWord and Separator], start_index: int, collocation_length: int) -> List[TaggedWord]:
    """
    Получение словосочетаний с учетом разделителей
    :param sentence: предложение с размеченными словами и разделителями
    :param start_index: откуда стартовать
    :param collocation_length: длина словосочетания, которое неббходимо извлечь
    :return:
    """
    if not isinstance(sentence, list) or len(sentence) == 0 or start_index >= len(sentence) \
            or collocation_length > len(sentence):
        return None

    result_collocation = []
    len_diff = len(sentence) - (start_index + collocation_length)
    if len_diff <= 0:
        collocation_length += len_diff
    for i in range(start_index, start_index + collocation_length):
        if isinstance(sentence[i], TaggedWord):
            if len(sentence[i].word) == 1 and sentence[i].pos not in [PartOfSpeech.preposition, PartOfSpeech.conjunction]:
                continue
            result_collocation.append(sentence[i])
        if isinstance(sentence[i], Separator):
            break
    return result_collocation
