import textract
import io
import re
import logging
import os


class TextImporter(object):
    """
    Абстрактный класс, использующийся для импорта начального текста
    """
    def get_text(self) -> str:
        """
        Возвращает текст из источника
        :return: текст
        """
        return ""


class DefaultTextImporter(TextImporter):
    """
    Cтандартный текст
    """
    __defaultText = "Основная задача его заключается в непосредственной поддержке стрелковых рот и сопровождении их огнем и движением. Огонь минометных батальонов взаимодействует с огнем стрелкового оружия и артиллерии."

    def __init__(self, number=1):
        self.__text_number = number

    def get_text(self) -> str:
        return self.__defaultText


class PlainTextImporter(TextImporter):
    """
    Текст из файла
    """
    def __init__(self, filename):
        self.FileName = filename

    def get_text(self):
        with open(file=self.FileName, mode="rt", encoding="utf-8") as f:
            text = f.read()
        return text


class PdfHtmlTextImporter(TextImporter):
    """
    Текст из pdf документа
    """
    __WORD_LIMIT__ = 1000
    __separators__ = '[ .?!\n—"]+'

    def __init__(self, filename: str, word_limit: int = -1, start_index: int = 0):
        """
        :param filename: имя файла
        :param word_limit: ограничение по количеству слов
        :param start_index: номер начального слова, с которого следует начать фрагмент
        """
        if not (filename.endswith(".pdf") or filename.endswith(".html") or filename.endswith(".htm")):
            raise TypeError("Требуется html или pdf документ")
        self.FileName = filename
        self.__WORD_LIMIT__ = word_limit
        self.__START_INDEX__ = start_index

    def get_text(self) -> str:
        """
        Извлекает текст из pdf документа и выделяет при необходимости из него фрагмент
        :return: текст
        """
        logger = logging.getLogger()
        logger.debug("Начало извлечения текста из документа")
        text = textract.process(self.FileName)
        logger.debug("Текст извлечен")
        text = text.decode('utf-8')
        logger.debug("Текст перекодирован в utf-8")
        if self.__WORD_LIMIT__ != -1:
            logger.info("Выделение фрагмента текста длиной {0} сл., с {1} сл.".format(self.__WORD_LIMIT__, self.__START_INDEX__))
            word_count = len(re.split(self.__separators__, text))

            if word_count > self.__WORD_LIMIT__ + self.__START_INDEX__:
                current_word_index = 0

                with io.StringIO(initial_value=text) as input_stream, io.StringIO() as output_stream:
                    while current_word_index <= self.__WORD_LIMIT__ + self.__START_INDEX__:
                        line = input_stream.readline()
                        line_words = re.split(self.__separators__, line)
                        while line_words.count('') > 0:
                            line_words.remove('')

                        current_word_index += len(line_words)
                        if current_word_index >= self.__START_INDEX__:
                            line = line.replace("\n\n", '\n')
                            output_stream.write(line)
                    text = output_stream.getvalue()
                    logger.info("Фрагмент из {0} сл извлечен".format(current_word_index - self.__START_INDEX__))
        return text


class FileArrayImporter(TextImporter):

    def __init__(self, filelist_name: str):
        """
        :param filelist_name: имя файла со списком документов
        """
        self.__files__ = list()
        if filelist_name == str():
            raise ValueError('Требуется наименование файла, хранящего список документов')
        if not (os.path.exists(filelist_name) and os.path.isfile(filelist_name)):
            raise ValueError('Файл с наименованием \'{0}\' не сушествует'.format(filelist_name))

        with open(file=filelist_name, mode="rt", encoding="utf-8") as f:
            text = f.readlines()
            for line in text:
                current_file = os.path.join(os.path.dirname(filelist_name), line).strip()
                if os.path.exists(current_file) and os.path.isfile(current_file):
                    self.__files__.append(current_file)

    def get_text(self):
        text_corpus = list()
        for file in self.__files__:
            local_text = str()
            logging.debug('Извлекаем содержимое из файла \'{0}\''.format(file))
            if file.endswith('txt'):
                local_text = PlainTextImporter(file).get_text()
            elif file.endswith('pdf') or file.endswith('html') or file.endswith('htm'):
                local_text = PdfHtmlTextImporter(file).get_text()
            if len(local_text) > 0:
                text_corpus.append(local_text)
        text = '\n'.join(text_corpus)
        return text


