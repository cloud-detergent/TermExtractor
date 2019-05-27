import os
import unittest

import Runner
from ITermExtractor.PartOfSpeech import PartOfSpeech
from ITermExtractor.Structures.Case import Case
from ITermExtractor.Structures.WordStructures import TaggedWord, contains_sentence
from TextImporter import PlainTextImporter


class TestTextParsing(unittest.TestCase):
    @unittest.skip
    def test_document_splitting(self):
        test_file = os.path.join('..', 'data', 'default-doc.txt')
        text_importer = PlainTextImporter(test_file)

        input_text = text_importer.get_text()
        documents = text_importer.get_documents(input_text)
        tagged_documents = [Runner.parse_text(input_text=document) for document in documents]
        self.assertEqual(list(), list())

    def test_tagged_document_splitting(self):
        sentence = [TaggedWord(word='ПРИКАЗ', pos=PartOfSpeech.noun, case=Case.accusative, normalized='приказ'),
                    TaggedWord(word='ВОЙСКАМ', pos=PartOfSpeech.noun, case=Case.dative, normalized='войско'),
                    TaggedWord(word='УДАРНОЙ', pos=PartOfSpeech.adjective, case=Case.genitive, normalized='ударный'),
                    TaggedWord(word='АРМИИ', pos=PartOfSpeech.noun, case=Case.genitive, normalized='армия')]
        result = contains_sentence(sentence, 'Приказ', 4)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
