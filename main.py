from ITermExtractor.linguistic_filter import (NounPlusLinguisticFilter, AdjNounLinguisticFilter, LinguisticFilter)
from ITermExtractor.linguistic_filter import collocation
from ITermExtractor.stoplist import StopList
from TextImporter import (DefaultTextImporter, PlainTextImporter)
from typing import List
from operator import itemgetter
from ITermExtractor.Morph import TaggedWord
import sys
import Runner
import datetime
import os
import logger_settings
import logging
import ITermExtractor.stat.cvalue as cvalue
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


if __name__ == "__main__":
    logger_settings.setup()
    logger = logging.getLogger()
    logger.info("\n============================================Запуск==============================================\n")

    start_time = datetime.datetime.now()
    force_test_file_usage = True
    use_pseudo_text_fetcher = len(sys.argv) != 2
    save_tagdata_to_log = True
    if use_pseudo_text_fetcher and not force_test_file_usage:
        logger.info("Не указано имя входного файла - будет использоваться тестовый модуль")
        textImp = DefaultTextImporter(number=2)
    elif force_test_file_usage:
        test_file = os.path.join('data', 'doc-2.txt')
        textImp = PlainTextImporter(test_file)
        logger.info("Используем входной текстовый файл по умолчанию {0}".format(test_file))
    else:
        textImp = PlainTextImporter(filename=sys.argv[1])
        logger.info("Файл для обработки был передан через аргумент ('{0}')".format(sys.argv[1]))

    # TODO убирать при разборе символы тире, дефисов, нижних подчеркиваний
    inputText = textImp.getText()
    tagged_sentence_list = []
    if save_tagdata_to_log:
        tagged_sentence_list = open_tag_data(os.path.join('result', 'tags'))
        logger.info("Теги взяты из файла, в котором {0}"
                    .format("пусто" if len(tagged_sentence_list) == 0
                            else "есть данные"))
    if not save_tagdata_to_log or len(tagged_sentence_list) == 0:
        tagged_sentence_list = Runner.parse_text(input_text=inputText)
        logger.debug("Текст обработан, количество слов с тегами {0}".format(len(tagged_sentence_list)))
        if save_tagdata_to_log:
            save_tag_data(os.path.join('result', 'tags'), tagged_sentence_list)
            logger.info("Теги сохранены в файл")

    logger.debug("Начало извлечения списка терминов")
    filter1 = NounPlusLinguisticFilter()
    filter2 = AdjNounLinguisticFilter()

    logger.info("Фильтр 1: Начало")
    terms1 = filter1.filter_text(tagged_sentence_list)
    logger.info("Фильтр 1: список терминов извлечен")

    logger.info("Фильтр 2: Начало")
    terms2 = filter2.filter_text(tagged_sentence_list)
    logger.info("Фильтр 2: список терминов извлечен")

    logger.info("Начинаем фильтрацию - стоп-лист")
    sl = StopList(use_settings=True)
    filtered_terms1 = sl.filter(terms1)
    filtered_terms2 = sl.filter(terms2)
    logger.info("Отфильтрован список 1, было/стало {0}/{1}"
                .format(len(terms1), len(filtered_terms1)))
    logger.info("Отфильтрован список 2, было/стало {0}/{1}"
                .format(len(terms2), len(filtered_terms2)))

    logger.info("Запись промежуточных результатов в файлы")
    save_text_raw_terms(os.path.join('result', 'noun_plus.txt'), filtered_terms1)
    save_text_raw_terms(os.path.join('result', 'adj_noun.txt'), filtered_terms2)
    logger.info("Данные записаны")

    logger.info("Подсчитываем cvalue")
    max_1 = max(terms1, key=itemgetter(1)).wordcount
    max_2 = max(terms2, key=itemgetter(1)).wordcount
    cvalue_res_1 = cvalue.calculate(filtered_terms1, max_1)
    cvalue_res_2 = cvalue.calculate(filtered_terms2, max_2)
    logging.info("Подсчет закончен, сохраняем результаты в файл")
    save_text_stat(os.path.join('result', 'noun_plus_cvalue.txt'), cvalue_res_1)
    save_text_stat(os.path.join('result', 'adj_noun_cvalue.txt'), cvalue_res_2)

    # TODO Удалять кандидаты с 1 словом
    end_time = datetime.datetime.now()
    logger.info("Алгоритм работал {0} c.".format(end_time - start_time))
    logger.info("Конец")
