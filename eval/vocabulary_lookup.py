from typing import List, Dict, Tuple, Any
from main import open_text_stat, save_text_stat
import ITermExtractor.Morph as m
import ITermExtractor.stat.cvalue_revisited as cvalue
from ITermExtractor.Structures.WordStructures import Separator, TaggedWord
import os
import random

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
            print("Разделитель в словосочетании из словаря", w, collocation)
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


def compare(extracted_terms: Tuple[str, str, float], sample: Dict[str, str], in_list_precise=list(), in_list_fuzzy_sample_in=list(), in_list_fuzzy_extracted_in=list()):
    for term in extracted_terms:
        if term[1] in sample.keys():
            in_list_precise.append(term)
        sample_nested_inclusion = [key for key in sample.keys() if key in term[1]]
        extracted_nested_inclusion = [key for key in sample.keys() if term[1] in key]
        if len(sample_nested_inclusion) > 0:
            in_list_fuzzy_sample_in.append(term)
        if len(extracted_nested_inclusion) > 0:
            in_list_fuzzy_extracted_in.append(term)


def run_comparison(extracted_terms: Tuple[str, float]):
    data = load_vocabulary()
    prep_sample = comparison_sample_preparation(data)
    prep_list = comparison_terms_preparation(extracted_terms)

    in_list_precise = list()
    in_list_fuzzy_sample_in = list()
    in_list_fuzzy_extracted_in = list()
    compare(prep_list, prep_sample, in_list_precise, in_list_fuzzy_sample_in, in_list_fuzzy_extracted_in)
    print(in_list_precise)
    print(in_list_fuzzy_sample_in)
    print(in_list_fuzzy_extracted_in)


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

    cvalue_1 = open_text_stat(file_1)
    cvalue_2 = open_text_stat(file_2)
    kfactor_1 = open_text_stat(file_3)
    kfactor_2 = open_text_stat(file_4)

    # <editor-fold desc="Длинный список">
    run_comparison(cvalue_1)
    run_comparison(cvalue_2)
    run_comparison(kfactor_1)
    run_comparison(kfactor_2)
    # </editor-fold>

    # <editor-fold desc="Короткий список">
    random.seed()
    cvalue_1_short = [t for i, t in enumerate(cvalue_1) if i < 100]
    cvalue_2_short = [t for i, t in enumerate(cvalue_2) if i < 100]
    kfactor_1_short = select_random_excerpt(kfactor_1, {1: 20, 2: 20, 3: 20, 4: 20, 5: 20})
    kfactor_2_short = select_random_excerpt(kfactor_2, {1: 20, 2: 20, 3: 20, 4: 20, 5: 20})

    run_comparison(cvalue_1)
    run_comparison(cvalue_2)
    run_comparison(kfactor_1)
    # </editor-fold>

    # <editor-fold desc="Средней список">
    random.seed()
    cvalue_1_short = [t for t in cvalue_1 if t[1] > 1]
    cvalue_2_short = [t for t in cvalue_2 if t[1] > 1]
    kfactor_1_short = [t for t in kfactor_1 if t[1] > 1]
    kfactor_2_short = [t for t in kfactor_2 if t[1] > 1]

    run_comparison(cvalue_1_short)
    run_comparison(cvalue_2_short)
    run_comparison(kfactor_1_short)
    run_comparison(kfactor_2_short)
    # </editor-fold>
