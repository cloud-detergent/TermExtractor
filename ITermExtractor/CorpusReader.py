import zipfile as z;
import xml.parsers.expat as xp


def grep(lines, query):
    for line in lines:
        if query in line:
            yield line


def to_string(zinfo_files):
    for f in zinfo_files:
        yield f.filename


class CorpusReader(object):
    path = "data/shuffled_rnc.zip"

    def __init__(self):
        isValid = z.is_zipfile(self.path)
        if not isValid:
            raise (AttributeError("Файл архива не поддерживается"))
        self._parser = xp.ParserCreate()
        self._parser.StartElementHandler = self.start_element
        self._parser.EndElementHandler = self.end_element
        self._parser.CharacterDataHandler = self.char_data

    def start_element(self, name, attr):
        if name == 'ana':
            self._info = attr

    def end_element(self, name):
        if name == 'se':
            self._sentences.append(self._sentence)
            self._sentence = []
        elif name == 'w':
            self._sentence.append((self._cdata, self._info))
        elif name == 'ana':
            self._cdata = ''

    def char_data(self, content):
        self._cdata += content


    def getXmlElements(self):
        self.arch = z.ZipFile(self.path, "r")
        files = self.arch.infolist()
        srt_files = grep(lines=to_string(files), query=".xml")
        self.arch.close()
        return list(srt_files)

    def readXmlContent(self, name):
        self.arch = z.ZipFile(self.path, "r")
        files = self.arch.infolist()
        srt_files = grep(lines=to_string(files), query=name)

        if len(list(srt_files)) != 1:
            raise AttributeError("Файл с данным именем отсутствует в архиве")

        content = self.arch.read(name=name)
        self.arch.close()

        self._sentence = []
        self._sentences = []
        self._cdata = ''
        self._info = ''

        self._parser.Parse(content)

        return self._sentences
