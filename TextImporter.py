class TextImporter(object):
    """Абстрактный класс импорта текста"""
    def getText(self):
        return ""


class DefaultTextImporter(TextImporter):
    """
    Класс, возвращающий стандартный текст
    """
    __defaultText = "Съешь же ещё этих мягких французских булок, да выпей чаю"
    __defaultText2 = "Основная задача его заключается в непосредственной поддержке стрелковых рот и сопровождении их огнем и движением. Огонь минометных батальонов взаимодействует с огнем стрелкового оружия и артиллерии."
    __text_number = 0

    def __init__(self, number=1):
        self.__text_number = number

    def getText(self):
        if self.__text_number == 1:
            return self.__defaultText
        else:
            return self.__defaultText2


class PlainTextImporter(TextImporter):
    def __init__(self, filename):
        self.FileName = filename

    def getText(self):
        f = open(self.FileName, "rt")
        text = f.read()
        return text


class PdfTextImporter(TextImporter):
    def __init__(self, fileName):
        self.FileName = fileName

    def getText(self):
        f = open(self.FileName, "rt")
        text = f.read()
        return text