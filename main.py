import sys

import Runner
from ITermExtractor.linguistic_filter import (NounPlusLinguisticFilter, AdjNounLinguisticFilter)
from ITermExtractor.CorpusReader import CorpusReader
from TextImporter import (DefaultTextImporter, PlainTextImporter)

# TODO время проверять на заготовленном документе doc.txt
isUsingPseTextFetcher = len(sys.argv) != 2
if isUsingPseTextFetcher:
    print("Не указано имя входного файла - будет использоваться тестовый модуль")
    textImp = DefaultTextImporter(number=2)
else:
    textImp = PlainTextImporter(filename=sys.argv[1])

inputText = textImp.getText()
# print ("В любом случае, полученный текст гласит:\n{0}".format(inputText))

# TODO необходимо для тренировки svm
#reader = CorpusReader()
#files = reader.getXmlElements()


#
# for file in files:
#    print(file)

# print("В первом файле (\"{0}\") у нас содержится:".format(files[0]), end="\n-\n-")
# input()
# sentences = reader.readXmlContent(files[0])
# print(sentences[0:2])
# print("Время тренировать модель ")
# SVMTrainer()

# ---------------------------------------#

tagged_sentence_list = Runner.parse_text(input_text=inputText)
filter1 = NounPlusLinguisticFilter()
filter2 = AdjNounLinguisticFilter()
for sentence in tagged_sentence_list:
    terms1 = filter1.filter(sentence)
    terms2 = filter2.filter(sentence)
    print("Предложение ", sentence)
    print("Термины раз", terms1)
    print("Термины два", terms2)
    print("_____________________")

# -----------------------------------#
# sentences = Runner.split_sentences(inputText2)
# print("Список предложений {0}".format(sentences))
# input()
#
# for sentence in sentences:
#     tagInfo = Runner.tag_sentence(sentence)
#     print("Предложение: \"{0}\"\n{1}".format(sentence, tagInfo))