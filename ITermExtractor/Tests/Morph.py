from ITermExtractor.Structures.Case import Case
from ITermExtractor.linguistic_filter import *
import ITermExtractor.Morph as m
import unittest


class TestLinguisticFilter(unittest.TestCase):
    def test_word_tag(self):
        words = ['огонь', 'артиллерии', 'боевого', 'огневым', 'батальон', 'ее', '(дивизион)']
        expected_results = [TaggedWord(word='огонь', pos=PartOfSpeech.noun, case=Case.nominative, normalized='огонь'),
                            TaggedWord(word='артиллерии', pos=PartOfSpeech.noun, case=Case.genitive, normalized='артиллерия'),
                            TaggedWord(word='боевого', pos=PartOfSpeech.adjective, case=Case.genitive,
                                       normalized='боевой'),
                            TaggedWord(word='огневым', pos=PartOfSpeech.adjective, case=Case.ablative,
                                       normalized='огневой'),
                            TaggedWord(word='батальон', pos=PartOfSpeech.noun, case=Case.nominative,
                                       normalized='батальон'),
                            TaggedWord(word='ее', pos=PartOfSpeech.noun_pronoun, case=Case.genitive,
                                       normalized='она'),
                            TaggedWord(word='дивизион', pos=PartOfSpeech.noun, case=Case.nominative,
                                       normalized='дивизион')
                            ]
        for k, v in zip(words, expected_results):
            result = m.tag_word(k)
            self.assertEqual(result, v)

    def test_collocation_tag(self):
        collocations = ['огонь артиллерии', 'парково-хозяйственный день', 'слушать громко']
        expected_results = [ [TaggedWord(word='огонь', pos=PartOfSpeech.noun, case=Case.nominative, normalized='огонь'),
                              TaggedWord(word='артиллерии', pos=PartOfSpeech.noun, case=Case.genitive,
                                       normalized='артиллерия')],
                             [TaggedWord(word='парково-хозяйственный', pos=PartOfSpeech.adjective, case=Case.nominative,
                                       normalized='парково-хозяйственный'),
                              TaggedWord(word='день', pos=PartOfSpeech.noun, case=Case.accusative,
                                       normalized='день')],  # TODO по неведомой причине слову дается винительный падеж
                             [TaggedWord(word='слушать', pos=PartOfSpeech.verb, case=Case.none,
                                       normalized='слушать'),
                              TaggedWord(word='громко', pos=PartOfSpeech.adverb, case=Case.none,
                                       normalized='громко')] ]
        for k, v in zip(collocations, expected_results):
            result = m.tag_collocation(k)
            self.assertEqual(result, v)

        sentences = ['Минометный батальон (дивизион) является мощным огневым средством пехоты во всех видах ее боевой деятельности', 'Основная задача его заключается в непосредственной поддержке стрелковых рот и сопровождении их огнем и движением']
        expected_results = [[TaggedWord(word='Минометный', pos=PartOfSpeech.adjective, case=Case.nominative, normalized='миномётный'),
                             TaggedWord(word='батальон', pos=PartOfSpeech.noun, case=Case.nominative, normalized='батальон'),
                             TaggedWord(word='дивизион', pos=PartOfSpeech.noun, case=Case.nominative, normalized='дивизион'),
                             TaggedWord(word='является', pos=PartOfSpeech.verb, case=Case.none, normalized='являться'),
                             TaggedWord(word='мощным', pos=PartOfSpeech.adjective, case=Case.ablative, normalized='мощный'),
                             TaggedWord(word='огневым', pos=PartOfSpeech.adjective, case=Case.ablative, normalized='огневой'),
                             TaggedWord(word='средством', pos=PartOfSpeech.noun, case=Case.ablative, normalized='средство'),
                             TaggedWord(word='пехоты', pos=PartOfSpeech.noun, case=Case.genitive, normalized='пехота'),
                             TaggedWord(word='во', pos= PartOfSpeech.preposition, case = Case.none, normalized='в'),
                             TaggedWord(word='всех', pos=PartOfSpeech.adjective, case=Case.genitive, normalized='весь'),
                             TaggedWord(word='видах', pos=PartOfSpeech.noun, case=Case.prepositional, normalized='вид'),
                             TaggedWord(word='ее', pos= PartOfSpeech.noun_pronoun, case = Case.genitive, normalized = 'она'),
                             TaggedWord(word='боевой', pos=PartOfSpeech.adjective, case=Case.ablative, normalized='боевой'),
                             TaggedWord(word='деятельности', pos=PartOfSpeech.noun, case=Case.genitive, normalized='деятельность')],

                            [TaggedWord(word='Основная', pos=PartOfSpeech.adjective, case=Case.nominative,
                                        normalized='основный'),
                             TaggedWord(word='задача', pos=PartOfSpeech.noun, case=Case.nominative,
                                        normalized='задача'),
                             TaggedWord(word='его', pos= PartOfSpeech.noun_pronoun, case=Case.accusative, normalized='он'),
                             TaggedWord(word='заключается', pos=PartOfSpeech.verb, case=Case.none, normalized='заключаться'),
                             TaggedWord(word='в', pos= PartOfSpeech.preposition, case=Case.none, normalized='в'),
                             TaggedWord(word='непосредственной', pos=PartOfSpeech.adjective, case=Case.prepositional,
                                       normalized='непосредственный'),
                             TaggedWord(word='поддержке', pos=PartOfSpeech.noun, case=Case.prepositional, normalized='поддержка'),
                             TaggedWord(word='стрелковых', pos=PartOfSpeech.adjective, case=Case.genitive, normalized='стрелковый'),
                             TaggedWord(word='рот', pos=PartOfSpeech.noun, case=Case.genitive, normalized='рота'),
                             TaggedWord(word='и', pos= PartOfSpeech.conjunction, case=Case.none, normalized='и'),
                             TaggedWord(word='сопровождении', pos=PartOfSpeech.noun, case=Case.prepositional, normalized='сопровождение'),
                             TaggedWord(word='их', pos= PartOfSpeech.noun_pronoun, case=Case.genitive, normalized='они'),
                             TaggedWord(word='огнем', pos=PartOfSpeech.noun, case=Case.ablative, normalized='огонь'),
                             TaggedWord(word='и', pos= PartOfSpeech.conjunction, case=Case.none, normalized='и'),
                             TaggedWord(word='движением', pos=PartOfSpeech.noun, case=Case.ablative, normalized='движение')]]

        for k, v in zip(sentences, expected_results):
            result = m.tag_collocation(k)
            self.assertEqual(result, v)

if __name__ == "__main__":
    unittest.main()
