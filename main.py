import sys
import Runner
from ITermExtractor.linguistic_filter import (NounPlusLinguisticFilter, AdjNounLinguisticFilter)
from ITermExtractor.stoplist import StopList
from TextImporter import (DefaultTextImporter, PlainTextImporter)
import datetime
import logging

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG)

# TODO время проверять на заготовленном документе doc.txt
force_test_file_usage = True
isUsingPseTextFetcher = len(sys.argv) != 2
if isUsingPseTextFetcher and not force_test_file_usage:
    print("Не указано имя входного файла - будет использоваться тестовый модуль")
    textImp = DefaultTextImporter(number=2)
elif force_test_file_usage:
    print("Using default text input file")
    textImp = PlainTextImporter("data/doc.txt")
else:
    textImp = PlainTextImporter(filename=sys.argv[1])

# TODO убирать при разборе символы тире, дефисов, нижних подчеркиваний
inputText = textImp.getText()

tagged_sentence_list = Runner.parse_text(input_text=inputText)
print("Начало извлечения списка терминов, время {0}".format(datetime.datetime.now()))
filter1 = NounPlusLinguisticFilter()
filter2 = AdjNounLinguisticFilter()
terms1 = filter1.filter_text(tagged_sentence_list)
print("Фильтр 1: список терминов извлечен, время {0}".format(datetime.datetime.now()))
terms2 = {}
# terms2 = filter2.filter_text(tagged_sentence_list)
print("Фильтр 2: список терминов извлечен, время {0}".format(datetime.datetime.now()))
print("Термины, полученные фильтром Noun+")
terms1_srt = list(terms1.keys())
terms1_srt.sort(key=lambda x: terms1.get(x))
for k in terms1_srt:
    print("{0} \t\t = \t\t{1}".format(k, terms1.get(k)))

print("Начинаем фильтрацию - стоп-лист")
sl = StopList()


print("Термины, полученные фильтром Adj|Noun")
for k, v in terms2.items():
    print("{0} \t\t = \t\t{1}".format(k, v))
"""
for sentence in tagged_sentence_list:
    terms1 = filter1.filter(sentence)
    terms2 = filter2.filter(sentence)
    print("Предложение ", sentence)
    print("Термины раз", terms1)
    print("Термины два", terms2)
    print("_____________________")
"""
# TODO фильтровать, прогонять через стоп-список, Удалять кандидаты с 1 словом и сортировать по частоте встречаемости
# TODO откатать на тестовом файле + считать максммальную длину терминов в словах
# -----------------------------------#
# sentences = Runner.split_sentences(inputText2)
# print("Список предложений {0}".format(sentences))
# input()
#
# for sentence in sentences:
#     tagInfo = Runner.tag_sentence(sentence)
#     print("Предложение: \"{0}\"\n{1}".format(sentence, tagInfo))