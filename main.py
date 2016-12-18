from ITermExtractor.linguistic_filter import (NounPlusLinguisticFilter, AdjNounLinguisticFilter, AdjNounReducedLinguisticFilter)
from ITermExtractor.linguistic_filter import collocation
from ITermExtractor.stoplist import StopList
from TextImporter import (DefaultTextImporter, PlainTextImporter, PdfTextImporter)
from typing import List
from operator import itemgetter
from ITermExtractor.Structures.WordStructures import TaggedWord
import sys
import Runner
import datetime
import os
import logger_settings
import logging
import ITermExtractor.stat.cvalue as cvalue
import ITermExtractor.stat.kfactor as kfactor
import pickle


def save_text_raw_terms(filename: str, input_list: List[collocation]):
    with open(file=filename, mode="wt", encoding="utf-8") as f:
        data = []
        for line in input_list:
            data.append("{0} = {1}{2}".format(line.collocation, line.freq, os.linesep))
        f.writelines(data)


def save_text_stat(filename: str, input_list: List[cvalue.params]):
    with open(file=filename, mode="wt", encoding="utf-8") as f:
        data = []
        for line in input_list:
            data.append("{0} = {1}{2}".format(line.name, line.cvalue, os.linesep))
        f.writelines(data)


def save_tag_data(filename: str, tag_list: List[TaggedWord]):
    with open(filename, 'wb') as fp:
        pickle.dump(tag_list, fp, pickle.HIGHEST_PROTOCOL)


def open_tag_data(filename: str) -> List[TaggedWord]:
    try:
        with open(filename, 'rb') as fp:
            data = pickle.load(fp)
    except FileNotFoundError:
        data = []
        logger.warning("Файл с размеченными словами отсутствует")
    except EOFError:
        data = []
        logger.warning("Файл с размеченными словами пуст")
    return data

__time_stamps__ = []


def track_time(desc: str = ""):
    __time_stamps__.append((desc, datetime.datetime.now()))


def difference(desc: str = ""):
    stamps = [stamp[1] for stamp in __time_stamps__ if stamp[0] == desc]
    if len(stamps) >= 2:
        diffs = [str(stamps[i+1] - stamps[i]) for i in range(len(stamps) - 1)]
    else:
        diffs = []
    return diffs


def input_menu(text: str, choices: List[str], is_menu_entry: bool = True) -> int or str:
    print("\n{0}".format(text))
    data = '\n'.join(["{0}) {1}".format(index + 1, choice) for index, choice in enumerate(choices)])
    print(data)
    while True:
        choice = input()
        if is_menu_entry:
            try:
                choice = int(choice)
                if not 0 < choice <= len(choices):
                    raise TypeError
            except Exception:
                print("Повторите ввод")
                continue
        break

    return choice

if __name__ == "__main__":
    logger_settings.setup()
    logger = logging.getLogger()
    logger.info("\n============================================Запуск==============================================\n")

    choice_tag_cache_read = input_menu("Брать информацию из кэша лингвистической информации?", ["Да", "Нет"]) == 1
    if not choice_tag_cache_read:
        choice_source = input_menu("Выберите источник", ["Стандартный текст", "Текстовый файл", "Pdf-документ"])
        if choice_source != 1:
            choice_source_filename = input_menu("Введите имя файла (0-использовать стандартный файл)", [], False)
            choice_source_std = choice_source_filename == '0'

        choice_tag_cache_write = input_menu("Сохранять лингвистическую информацию в кэш?", ["Да", "Нет"]) == 1

        if choice_source == 1:
            logger.info("Выбран тестовый модуль")
            text_importer = DefaultTextImporter()
        elif choice_source == 2:
            if choice_source_std:
                test_file = os.path.join('data', 'doc-2.txt')
            else:
                test_file = os.path.join('data', choice_source_filename)
            logger.info("Выбран текстовый файл '{0}'".format(test_file))
            text_importer = PlainTextImporter(test_file)
        else:
            if choice_source_std:
                test_file = os.path.join('data', 'Cборник боевых документов ВОВ выпуск 12.pdf')
            else:
                test_file = os.path.join('data', choice_source_filename)

            word_limit = int(input_menu("Ограничение по количеству слов", [], False))
            start_index = 800  # int(input_menu("Стартовый индекс", [], False))

            logger.info("Выбран pdf документ '{0}'".format(test_file))
            text_importer = PdfTextImporter(filename=test_file, word_limit=word_limit, start_index=start_index)  # sys.argv[1]
            # TODO есть предложения, части которых разделены '\n'. части обрабатываются как отдельные предложения?
        input_text = text_importer.get_text()

    track_time()

    tagged_sentence_list = []
    if choice_tag_cache_read:
        tagged_sentence_list = open_tag_data(os.path.join('result', 'tags'))
        logger.info("Теги взяты из файла, в котором {0}"
                    .format("пусто" if len(tagged_sentence_list) == 0 else "есть данные"))
    if not choice_tag_cache_read or len(tagged_sentence_list) == 0:
        tagged_sentence_list = Runner.parse_text(input_text=input_text)
        logger.debug("Текст обработан, количество слов с тегами {0}".format(len(tagged_sentence_list)))
        if choice_tag_cache_write:
            save_tag_data(os.path.join('result', 'tags'), tagged_sentence_list)
            logger.info("Теги сохранены в файл")

    USE_FILTER_1 = True
    USE_FILTER_2 = True

    logger.debug("Начало извлечения списка терминов")
    if USE_FILTER_1:
        logger.info("Фильтр 1: Начало")
        filter1 = NounPlusLinguisticFilter()
        terms1 = filter1.filter_text(tagged_sentence_list)
        logger.info("Фильтр 1: список терминов извлечен")

    if USE_FILTER_2:
        logger.info("Фильтр 2: Начало")
        filter2 = AdjNounLinguisticFilter()
        terms2 = filter2.filter_text(tagged_sentence_list)
        logger.info("Фильтр 2: список терминов извлечен")
    """
    logger.info("Фильтр 3: Начало")
    terms3 = filter3.filter_text(tagged_sentence_list)
    logger.info("Фильтр 3: список терминов извлечен")
    """
    logger.info("Начинаем фильтрацию - стоп-лист")
    sl = StopList(use_settings=True)

    if USE_FILTER_1:
        filtered_terms1 = sl.filter(terms1)
    logger.info("Отфильтрован список 1, было/стало {0}/{1}"
                .format(len(terms1), len(filtered_terms1)))
    if USE_FILTER_2:
        filtered_terms2 = sl.filter(terms2)
        logger.info("Отфильтрован список 2, было/стало {0}/{1}"
                .format(len(terms2), len(filtered_terms2)))

    logger.info("Запись промежуточных результатов в файлы")
    if USE_FILTER_1:
        save_text_raw_terms(os.path.join('result', 'noun_plus.txt'), filtered_terms1)
    if USE_FILTER_2:
        save_text_raw_terms(os.path.join('result', 'adj_noun.txt'), filtered_terms2)
    logger.info("Данные записаны")

    logger.info("Подсчитываем cvalue")
    dictionary = [word for sentence in tagged_sentence_list for word in sentence]
    cvalue.set_dictionary(dictionary)
    track_time("cvalue")
    if USE_FILTER_1:
        max_1 = max(terms1, key=itemgetter(1)).wordcount
        cvalue_res_1 = cvalue.calculate(filtered_terms1, max_1)
    track_time("cvalue")
    if USE_FILTER_2:
        max_2 = max(terms2, key=itemgetter(1)).wordcount
        cvalue_res_2 = cvalue.calculate(filtered_terms2, max_2)
    track_time("cvalue")

    logger.info("Подсчет закончен, сохраняем результаты в файл")
    if USE_FILTER_1:
        save_text_stat(os.path.join('result', 'noun_plus_cvalue.txt'), cvalue_res_1)
    if USE_FILTER_2:
        save_text_stat(os.path.join('result', 'adj_noun_cvalue.txt'), cvalue_res_2)

    logger.info("Подсчитываем kfactor")
    track_time("kfactor")
    """
    kfactor_res = kfactor.calculate(filtered_terms2, dictionary)
    """
    track_time("kfactor")
    logging.info("Подсчет закончен, сохраняем результаты в файл")
    """
    save_text_raw_terms(os.path.join('result', 'adj_noun_kfactor.txt'), kfactor_res)
    """

    # TODO Удалять кандидаты с 1 словом ?
    track_time()
    logger.info("Алгоритм работал {0} c.".format(difference()))
    logger.info("Из которых cvalue работал {0} c.".format(difference("cvalue")))
    logger.info("Из которых kfactor работал {0} c.".format(difference("kfactor")))
    logger.info("Конец")
