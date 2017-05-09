from ITermExtractor.linguistic_filter import (NounPlusLinguisticFilter, AdjNounLinguisticFilter, AdjNounReducedLinguisticFilter)
from ITermExtractor.linguistic_filter import Collocation
from ITermExtractor.stoplist import StopList
from TextImporter import (DefaultTextImporter, PlainTextImporter, PdfTextImporter)
from typing import List
from ITermExtractor.Structures.WordStructures import TaggedWord
import Runner
import datetime
import os
import logger_settings
import logging
import ITermExtractor.stat.cvalue_revisited as cvalue
import ITermExtractor.stat.kfactor as kfactor
import pickle
from ITermExtractor.Tests.linguistic_filter import is_integral


def save_text_raw_terms(filename: str, input_list: List[Collocation]):
    with open(file=filename, mode="wt", encoding="utf-8") as f:
        data = []
        for line in input_list:
            data.append("{0} | {1} | {2} | {3} | {4}{5}".format(line.collocation, line.freq, line.id, line.pnormal_form, '-'.join([str(l) for l in line.llinked]), os.linesep))
        f.writelines(data)


def open_raw_terms(filename: str) -> List[Collocation]:
    result_list = []
    with open(file=filename, mode="rt", encoding="utf-8") as f:
        data = f.readlines()
        for line in data:
            parts = line.split(" | ")
            col = parts[0]
            freq = float(parts[1])
            i = int(parts[2])
            nf = parts[3]
            linked = [int(id) for id in parts[4].split('-')] if parts[4] != "\n" else list()
            result_list.append(Collocation(collocation=col, freq=freq, cid=i, pnormal_form=nf, llinked=linked))
    return result_list


def save_text_stat(filename: str, input_list: List[cvalue.params]):
    with open(file=filename, mode="wt", encoding="utf-8") as f:
        data = []
        for line in input_list:
            data.append("{0} = {1}{2}".format(line.name, round(line.cvalue, 3), os.linesep))
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


def input_menu(text: str, choices: List[str], is_menu_entry: bool = True, show_options: bool = True) -> int or str:
    print("\n{0}".format(text))
    data = '\n'.join(["{0}) {1}".format(index + 1, choice) for index, choice in enumerate(choices)])
    print(data if show_options else str())
    while True:
        choice = input()
        if is_menu_entry:
            try:
                choice = int(choice)
                if not 0 < choice <= len(choices):
                    raise TypeError
            except:
                print("Повторите ввод")
                continue
        break

    return choice

if __name__ == "__main__":
    USE_FILTER_1 = True
    USE_FILTER_2 = True
    RERUN_FILTER_1 = True
    RERUN_FILTER_2 = True
    USE_CVALUE_1 = USE_CVALUE_2 = USE_KFACTOR = False

    logger_settings.setup()
    logger = logging.getLogger()
    # logger = logger_settings.get_logger()
    logger.info("\n============================================Запуск==============================================\n")

    # choice_single_thread = input_menu("Обрабатывать данные в одном потоке?", ["Да", "Нет"]) == 1

    choice_tag_cache_read = input_menu("Использовать предыдущие данные морфологического анализа ?", ["Да", "Нет"]) == 1
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
            start_index = 600  # int(input_menu("Стартовый индекс", [], False))

            logger.info("Выбран pdf документ '{0}'".format(test_file))
            text_importer = PdfTextImporter(filename=test_file, word_limit=word_limit, start_index=start_index)  # sys.argv[1]
            # TODO есть предложения, части которых разделены '\n'. части обрабатываются как отдельные предложения?

    choice_stoplist = input_menu("Использовать стоп-лист?", ["Да", "Нет"]) == 1

    options = ['c-value с Noun+ фильтром', 'c-value с Adj|Noun фильтром', 'kfactor', 'закончить выбор']
    choice_algorithms = -1
    while choice_algorithms != len(options):
        choice_algorithms = input_menu("Выбор алгоритмов", options, show_options=choice_algorithms == -1)
        USE_CVALUE_1 = USE_CVALUE_1 or choice_algorithms == 1
        USE_CVALUE_2 = USE_CVALUE_2 or choice_algorithms == 2
        USE_KFACTOR = USE_KFACTOR or choice_algorithms == 3

        # USE_FILTER_1 = USE_CVALUE_1 or USE_KFACTOR
        # USE_FILTER_2 = USE_CVALUE_2
    print("Выбор осуществлен")
    if not choice_tag_cache_read:
        input_text = text_importer.get_text()

    track_time()

    tagged_sentence_list = []
    terms1 = []
    terms2 = []
    filtered_terms1 = []
    filtered_terms2 = []

    if choice_tag_cache_read:
        tagged_sentence_list = open_tag_data(os.path.join('result', 'tags'))
        logger.info("Теги взяты из файла, в котором {0}"
                    .format("пусто" if len(tagged_sentence_list) == 0 else "есть данные"))
        terms1 = open_raw_terms(os.path.join('result','inter-noun_plus.txt'))
        terms2 = open_raw_terms(os.path.join('result','inter-adj_noun.txt'))
        RERUN_FILTER_1 = False
        RERUN_FILTER_2 = False

    if not choice_tag_cache_read or len(tagged_sentence_list) == 0:
        tagged_sentence_list = Runner.parse_text(input_text=input_text)
        logger.debug("Текст обработан, количество слов с тегами {0}".format(len(tagged_sentence_list)))
        if choice_tag_cache_write:
            save_tag_data(os.path.join('result', 'tags'), tagged_sentence_list)
            with open(os.path.join('data', 'input_text.txt'), mode="wt") as f:
                f.write(input_text)
            logger.info("Теги сохранены в файл")

    logger.debug("Начало извлечения списка терминов")
    if USE_FILTER_1 and RERUN_FILTER_1:
        logger.info("Фильтр 1: Начало")
        filter1 = NounPlusLinguisticFilter()
        terms1 = filter1.filter_text(tagged_sentence_list)
        logger.info("Фильтр 1: список терминов извлечен")

    if USE_FILTER_2 and RERUN_FILTER_2:
        logger.info("Фильтр 2: Начало")
        filter2 = AdjNounLinguisticFilter()
        terms2 = filter2.filter_text(tagged_sentence_list)  # choice_single_thread
        logger.info("Фильтр 2: список терминов извлечен")

    if choice_stoplist:
        logger.info("Начинаем фильтрацию - стоп-лист")
        sl = StopList(use_settings=True)
        if USE_FILTER_1:
            filtered_terms1 = sl.filter(terms1)
            logger.info("Отфильтрован список 1, было/стало {0}/{1}".format(len(terms1), len(filtered_terms1)))
        if USE_FILTER_2:
            filtered_terms2 = sl.filter(terms2)
            logger.info("Отфильтрован список 2, было/стало {0}/{1}".format(len(terms2), len(filtered_terms2)))
    else:
        filtered_terms1 = terms1
        filtered_terms2 = terms2

    logger.info("Запись промежуточных результатов в файлы")
    if USE_FILTER_1 and RERUN_FILTER_1:
        save_text_raw_terms(os.path.join('result', 'inter-noun_plus.txt'), filtered_terms1)
    if USE_FILTER_2 and RERUN_FILTER_2:
        save_text_raw_terms(os.path.join('result', 'inter-adj_noun.txt'), filtered_terms2)
    logger.info("Данные записаны")

    dictionary = [word for sentence in tagged_sentence_list for word in sentence]

    logger.info("Подсчитываем cvalue")
    track_time("cvalue")
    if USE_FILTER_1 and USE_CVALUE_1:
        logger.info("Переход к подчету, фильтр 1, к обработке {0}".format(len(filtered_terms1)))
        cvalue_res_1 = cvalue.calculate(filtered_terms1)
    track_time("cvalue")
    if USE_FILTER_2 and USE_CVALUE_2:
        logger.info("Переход к подчету, фильтр 2, к обработке {0}".format(len(filtered_terms2)))
        cvalue_res_2 = cvalue.calculate(filtered_terms2)
    track_time("cvalue")

    logger.info("Подсчет закончен, сохраняем результаты в файл")
    if USE_FILTER_1 and USE_CVALUE_1:
        save_text_stat(os.path.join('result', 'cvalue_noun_plus.txt'), cvalue_res_1)
    if USE_FILTER_2 and USE_CVALUE_2:
        save_text_stat(os.path.join('result', 'cvalue_adj_noun.txt'), cvalue_res_2)

    logger.info("Подсчитываем kfactor, к обработке {0}".format(len(filtered_terms1)))
    track_time("kfactor")
    if USE_FILTER_2 and USE_KFACTOR:
        kfactor_res = kfactor.calculate(filtered_terms1, dictionary)
        logging.info("Подсчет закончен, сохраняем результаты в файл")
        save_text_raw_terms(os.path.join('result', 'kfactor_noun_plus.txt'), kfactor_res)
    track_time("kfactor")

    # TODO Удалять кандидаты с 1 словом ?
    track_time()
    logger.info("Алгоритм работал {0} c.".format(difference()))
    logger.info("Из которых cvalue работал {0} c.".format(difference("cvalue")))
    logger.info("Из которых kfactor работал {0} c.".format(difference("kfactor")))
    logger.info("Конец")
    print("Конец обработки данных")
