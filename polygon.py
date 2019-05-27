import os
from operator import itemgetter
import logging
import Runner
import logger_settings
from ITermExtractor.linguistic_filter import VerbalLinguisticFilter
from TextImporter import DefaultTextImporter, PlainTextImporter, PdfHtmlTextImporter, FileArrayImporter
from main import input_menu, save_text_raw_terms

if __name__ == "__main__":
    logger_settings.setup()
    logger = logging.getLogger()
    logger.info("\n=================Запуск поиска глаголов=================\n")

    choice_source = input_menu("Выберите источник",
                               ["Стандартный текст", "Текстовый файл", "Pdf-документ", "Список файлов"])
    if choice_source != 1:
        choice_source_filename = input_menu("Введите имя файла (0-использовать стандартный файл)", [], False)
        choice_source_std = choice_source_filename == '0'

    if choice_source == 1:
        logger.info("Выбран тестовый модуль")
        text_importer = DefaultTextImporter()
    elif choice_source == 2:
        if choice_source_std:
            test_file = os.path.join('data', 'default-doc.txt')
        else:
            test_file = os.path.join('data', choice_source_filename)
        logger.info("Выбран текстовый файл '{0}'".format(test_file))
        text_importer = PlainTextImporter(test_file)
    elif choice_source == 3:
        if choice_source_std:
            test_file = os.path.join('data', 'Cборник боевых документов ВОВ выпуск 12.pdf')
        else:
            test_file = os.path.join('data', choice_source_filename)

        word_limit = int(input_menu("Ограничение по количеству слов", [], False))

        logger.info("Выбран pdf документ '{0}'".format(test_file))
        text_importer = PdfHtmlTextImporter(filename=test_file, word_limit=word_limit)
    elif choice_source == 4:
        if choice_source_std:
            test_file = os.path.join('data', 'Corpus', 'list.txt')
        else:
            test_file = os.path.join('data', choice_source_filename)
        logger.info("Выбран файл со списком'{0}'".format(test_file))
        text_importer = FileArrayImporter(test_file)

    logger.debug('Данные ')
    input_text = text_importer.get_text()
    tagged_sentence_list = Runner.parse_text(input_text=input_text)

    verbal_filter = VerbalLinguisticFilter()
    filtered_verbs = verbal_filter.filter_text(tagged_sentence_list)
    save_text_raw_terms(os.path.join('result', 'inter-verbs.txt'),
                        sorted(filtered_verbs, key=itemgetter('freq'), reverse=True), True)

    logger.info("Конец поиска глаголов")
