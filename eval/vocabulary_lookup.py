from typing import List, Dict, Tuple, Any
from main import open_text_stat, save_text_stat
from operator import itemgetter
from ITermExtractor.Structures.WordStructures import Separator, TaggedWord
from itertools import groupby
import os
import random
import ITermExtractor.Morph as m

default_voc = '../data/ru_militaryterms_1_0.dsl'


def load_vocabulary(input_file:str = default_voc) -> List[str]:
    """
    Загружает словарь
    :param input_file: Входной файл словаря
    :return: список терминов
    """
    word_list = list()
    with(open(input_file, mode='rt', encoding='utf-16')) as f:
        for line in f:
            if line == str() or line == '\n' or line.startswith('\t[m') or line.startswith('_') or line.startswith('#'):
                continue
            line = line.strip()
            line = line.strip('.,;')
            line = ' '.join(line.split())

            reduced_index = len(line)
            if '{(' in line:
                left_bracket = line.index('{(')
                right_bracket = line.index(')}', left_bracket)
                reduced_index = left_bracket - 1
                sub_term = line[left_bracket+2:right_bracket]

                line = line[0:reduced_index]
                if ')' not in sub_term:
                    word_list.append(sub_term)

            if '{' in line:
                reduced_index = line.index('{') - 1
            if '(' in line:
                reduced_index = line.index('(') - 1
            line = line[0:reduced_index]
            word_list.append(line)
    return word_list


def comparison_sample_preparation(word_list: List[str]) -> Dict[str, str]:
    """
    Готовит список к сравнению, перевод в псевдонормальную форму
    :param word_list: список терминов, извлеченных из словаря
    :return: словарь терминов: псевдонормальная форма = нормальная форма
    """
    result = []
    for w in word_list:
        collocation = m.tag_collocation(w)
        separator_check = [isinstance(e, Separator) for e in collocation]
        if True in separator_check:
            # print("Разделитель в словосочетании из словаря", w, collocation)
            regular_form = ' '.join([e.word for e in collocation if isinstance(e, TaggedWord)])
        else:
            regular_form = w
        pnormal_form = ' '.join([e.normalized for e in collocation if isinstance(e, TaggedWord)])

        result.append( (pnormal_form, regular_form) )
    return dict(result)


def comparison_terms_preparation(extracted_terms: Tuple[str, float]) -> Tuple[str, str, float]:
    """
    Готовит список извлеченных стат методом терминов к сравнению, перевод в псевдонормальную форму
    :param extracted_terms: список терминов, извлеченных стат методом из текста
    :return: список терминов + псевдонормальные формы
    """
    result = []
    for t in extracted_terms:
        collocation = m.tag_collocation(t[0])
        pnormal_form = ' '.join([e.normalized for e in collocation])
        result.append( (t[0], pnormal_form, t[1]) )
    return result


def compare(extracted_terms: Tuple[str, str, float], sample: Dict[str, str], in_list_precise=list(),
            in_list_precise_sample_in=list(), in_list_precise_extracted_in=list(), exclude_list=list()):
    for term in extracted_terms:
        if term[1] in sample.keys():
            in_list_precise.append(term)
        sample_nested_inclusion = [key for key in sample.keys() if all(w in term[1].split() for w in key.split()) and key != term[1] and key != str() ]
        extracted_nested_inclusion = [key for key in sample.keys()
                                      if all(w in key.split() for w in term[1].split()) and key != term[1] ]

        if len(sample_nested_inclusion) > 0:
            in_list_precise_sample_in.append((term, sample_nested_inclusion))
        if len(extracted_nested_inclusion) > 0:
            in_list_precise_extracted_in.append((term, extracted_nested_inclusion))
    included_items = in_list_precise + [t[0] for t in in_list_precise_sample_in + in_list_precise_extracted_in]
    exclude_list = [term for term in extracted_terms if term not in included_items]
    """for term in extracted_terms:
        # in_list_precise + [t[0] for t in in_list_precise_sample_in + in_list_precise_extracted_in]
        if not (term in in_list_precise
                or term in [t[0] for t in in_list_precise_extracted_in]
                or term in [t[0] for t in in_list_precise_sample_in]):
            exclude_list.append(term)
    """
    # TODO работает неправильно


def calc_fuzzy(extracted_terms: List[Tuple[str, float]], prepared_sample: Dict[str, str]) -> List[Tuple[str, float]]:
    """
    подсчет нечеткой оценки на множестве терминов
    :param extracted_terms: извлеченные термины
    :param prepared_sample: подготовленный образец - список терминов из словаря
    :return:
    """
    normalized_voc_terms = prepared_sample.keys()
    final_list_similar = list()
    for t in extracted_terms:
        r = has_similar(t[0], normalized_voc_terms)
        if r:
            similar_terms = get_similar(t[0], normalized_voc_terms)
            final_list_similar.append((t, similar_terms))
    return final_list_similar


def calc_full_fuzzy_array(extracted_terms: List[Tuple[str, float]], prepared_sample: Dict[str, str]) -> List[float]:
    """
    подсчет нечеткой оценки на множестве терминов
    :param extracted_terms: извлеченные термины
    :param prepared_sample: подготовленный образец - список терминов из словаря
    :return:
    """
    normalized_voc_terms = prepared_sample.keys()
    similarity_list = list()
    for t in extracted_terms:
        similar_terms = get_similar(t[0], normalized_voc_terms)
        similarity_list.append(max(similar_terms, key=itemgetter(1))[1] if len(similar_terms) > 0 else 0)
    return similarity_list


def run_comparison(extracted_terms: List[Tuple[str, float]], prepared_sample: Dict[str, str] = dict(), caption = str()) -> Tuple[str, Dict[str, list]]:
    """
    Runs comparison functions
    :param extracted_terms: term extraction method results
    :param prepared_sample: sample from a vocabulary
    :return: detailed results combined into categories
    """
    if prepared_sample == dict():
        data = load_vocabulary()
        prepared_sample = comparison_sample_preparation(data)
        prep_list = comparison_terms_preparation(extracted_terms)

    in_list_precise = list()
    in_list_precise_sample_in = list()
    in_list_precise_extracted_in = list()
    in_list_fuzzy = list()
    exclude_list_precise = list()
    exclude_list_fuzzy = list()
    compare(prep_list, prepared_sample, in_list_precise, in_list_precise_sample_in, in_list_precise_extracted_in, exclude_list_precise)
    in_list_fuzzy = calc_fuzzy(extracted_terms, prepared_sample)

    for term in extracted_terms:
        if term not in [t[0] for t in in_list_fuzzy]:
            exclude_list_fuzzy.append(term)

    print('\n', caption, ':\n')
    print('Всего: ', len(extracted_terms))
    print('Число совпавших по словарю точно: ', len(in_list_precise))
    print('\t\tтермины словаря вложенные в извлеченные : ', len(in_list_precise_sample_in))
    print('\t\tизвлеченные вложенные в термины словаря : ', len(in_list_precise_extracted_in))
    print('\t\tЧисло совпавших нечетко: ', len(in_list_fuzzy))

    # for key, value_sitter in groupby(in_list_fuzzy, key=itemgetter('wordcount')):
    # print('\t\tЧисло извлеченных терминов, не в списке четкой формальной оценки: ', len(exclude_list_precise))
    # print('\t\tЧисло извлеченных терминов, не в списке нечеткой формальной оценки: ', len(exclude_list_fuzzy))

    # TODO должны ли входить четко совпавшие со словарными термины из нечеткого списка?
    result = (caption, {
        'voc': in_list_precise,
        'voc_nested': in_list_precise_sample_in,
        'extracted_nested': in_list_precise_extracted_in,
        'fuzzy': in_list_fuzzy
    })
    return result


def calc_similarity(str_1: str, str_2: str) -> float:
    """
    Подсчитывает близость 2 строк как отношение числа совпавших слов к общему количеству уникальных слов
    :param str_1: строка 1
    :param str_2: строка 2
    :return: степень близости [0, 1]
    """
    if not (isinstance(str_1, str) and isinstance(str_2, str)) or str_1 == str() or str_2 == str():
        return 0
    str_1_words = str_1.split()
    str_2_words = str_2.split()
    common_count = len([w for w in str_1_words if w in str_2_words])
    unique_sum_count = len(str_1_words) + len(str_2_words) - common_count
    return common_count / unique_sum_count


def has_similar(str_1: str, str_list: List[str]) -> bool:
    for s in str_list:
        result = calc_similarity(str_1, s) >= 0.5
        if result:
            break
    return result


def get_similar(str_1: str, str_list: List[str]) -> List[Tuple[str, float]]:
    similar_list = [(s, calc_similarity(str_1, s)) for s in str_list if calc_similarity(str_1, s) >= 0.5]
    return similar_list


def select_random_excerpt(input_list: List[Tuple[str, Any]], req_numbers_by_length: Dict[int, int]) -> List:
    """
    Извлечение случайно выбранной части из списка
    :param input_list: входной список терминов
    :param req_numbers_by_length: требуемые длины избранных терминов по количествам слов
    :return:
    """
    excerpt = list()
    for wordcount, req_length in req_numbers_by_length.items():
        wordcount_group = [t for t in input_list if len(t[0].split()) == wordcount]
        if len(wordcount_group) <= req_length:
            bit = wordcount_group
        else:
            bit = random.sample(wordcount_group, req_length)
        excerpt += bit
    return excerpt


if __name__ == "__main__":
    file_1 = os.path.join('..', 'result', 'cvalue_noun_plus.txt')
    file_2 = os.path.join('..', 'result', 'cvalue_adj_noun.txt')
    file_3 = os.path.join('..', 'result', 'kfactor_noun_plus.txt')
    file_4 = os.path.join('..', 'result', 'kfactor_adj_noun.txt')

    file_5 = os.path.join('..', 'result', 'glossex_noun_plus.txt')
    file_6 = os.path.join('..', 'result', 'glossex_adj_noun.txt')

    cvalue_1 = open_text_stat(file_1)
    cvalue_2 = open_text_stat(file_2)
    kfactor_1 = open_text_stat(file_3)
    kfactor_2 = open_text_stat(file_4)
    glossex_1 = open_text_stat(file_5)
    glossex_2 = open_text_stat(file_6)

    prepared_sample = dict()

    # <editor-fold desc="Короткий список">
    random.seed()
    cvalue_1_short = [t for i, t in enumerate(cvalue_1) if i < 100]
    cvalue_2_short = [t for i, t in enumerate(cvalue_2) if i < 100]
    kfactor_1_short = select_random_excerpt(kfactor_1, {1: 20, 2: 20, 3: 20, 4: 20, 5: 20})
    kfactor_2_short = select_random_excerpt(kfactor_2, {1: 20, 2: 20, 3: 20, 4: 20, 5: 20})

    glossex_1_short = [t for i, t in enumerate(glossex_1) if i < 100]
    glossex_2_short = [t for i, t in enumerate(glossex_2) if i < 100]

    run_comparison(cvalue_1_short, prepared_sample, 'C-value short 1')
    run_comparison(cvalue_2_short, prepared_sample, 'C-value short 2')
    run_comparison(kfactor_1_short, prepared_sample, 'kFactor short 1')
    run_comparison(kfactor_2_short, prepared_sample, 'kFactor short 2')
    run_comparison(glossex_1_short, prepared_sample, 'GlossEx short 1')
    run_comparison(glossex_2_short, prepared_sample, 'GlossEx short 2')
    # </editor-fold>

    # <editor-fold desc="Средний список">
    cvalue_1_middle = [t for t in cvalue_1 if t[1] > 1]
    cvalue_2_middle = [t for t in cvalue_2 if t[1] > 1]
    kfactor_1_middle = [t for t in kfactor_1 if t[1] > 1]
    kfactor_2_middle = [t for t in kfactor_2 if t[1] > 1]
    glossex_1_middle = [t for t in glossex_1 if t[1] > 1]
    glossex_2_middle = [t for t in glossex_2 if t[1] > 1]

    run_comparison(cvalue_1_middle, prepared_sample, 'C-value middle 1')
    run_comparison(cvalue_2_middle, prepared_sample, 'C-value middle 2')
    run_comparison(kfactor_1_middle, prepared_sample, 'kFactor middle 1')
    run_comparison(kfactor_2_middle, prepared_sample, 'kFactor middle 2')
    run_comparison(glossex_1_middle, prepared_sample, 'GlossEx middle 1')
    run_comparison(glossex_2_middle, prepared_sample, 'GlossEx middle 2')
    # </editor-fold>

    # <editor-fold desc="Длинный список">
    run_comparison(cvalue_1, prepared_sample, 'C-value 1')
    run_comparison(cvalue_2, prepared_sample, 'C-value 2')
    run_comparison(kfactor_1, prepared_sample, 'kFactor 1')
    run_comparison(kfactor_2, prepared_sample, 'kFactor 2')
    run_comparison(glossex_1, prepared_sample, 'GlossEx 1')
    run_comparison(glossex_2, prepared_sample, 'GlossEx 2')
    # </editor-fold>
    """
    # <editor-fold desc="Короткий список">
    random.seed()
    requirements = {
        1: 20,
        2: 20,
        3: 20,
        4: 20,
        5: 20,
    }

    cvalue_1_short = [t for n, t in enumerate(cvalue_1) if n <= 100]
    cvalue_2_short = [t for n, t in enumerate(cvalue_2) if n <= 100]
    kfactor_1_short = select_random_excerpt(kfactor_1, requirements)
    kfactor_2_short = select_random_excerpt(kfactor_2, requirements)

    run_comparison(cvalue_1_short, prepared_sample)
    run_comparison(cvalue_2_short, prepared_sample)
    run_comparison(kfactor_1_short, prepared_sample)
    run_comparison(kfactor_2_short, prepared_sample)
    # </editor-fold>

    # <editor-fold desc="Длинный список">
    run_comparison(cvalue_1, prepared_sample)
    run_comparison(cvalue_2, prepared_sample)
    run_comparison(kfactor_1, prepared_sample)
    run_comparison(kfactor_2, prepared_sample)
    # </editor-fold>
    """
