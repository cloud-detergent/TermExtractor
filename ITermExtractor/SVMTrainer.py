from sys import stderr
from ITermExtractor.pos import Tagger, tagset
from ITermExtractor.CorpusReader import CorpusReader
import re


def SVMTrainer():
    """Неработающий модуль: переписать, разобраться"""
    creader = CorpusReader()
    corpus_files = creader.getXmlElements()

    sentences = []
    sentence_labels = []
    sentence_words = []

    for corpus_part in corpus_files:
        sentences.append(creader.readXmlContent(corpus_part))

    re_pos = re.compile('([\w-]+)(?:[^\w-]|$)'.format('|'.join(tagset)))

    tagger = Tagger()

    for sentence in sentences:
        labels = []
        words = []
        for word in sentence:
            gr = word[1]['gr']
            m = re_pos.match(gr)
            if not m:
                print(gr, file=stderr)

            pos = m.group(1)
            if pos == 'ANUM':
                pos = 'A-NUM'

            label = tagger.get_label_id(pos)
            if not label:
                print(gr, file=stderr)

            labels.append(label)

            body = word[0].replace('`', '')
            words.append(body)

        sentence_labels.append(labels)
        sentence_words.append(words)

    tagger.train(sentence_words, sentence_labels, True)
    tagger.train(sentence_words, sentence_labels)
    tagger.save('tmp/svm.model', 'tmp/ids.pickle')