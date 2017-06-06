from ITermExtractor.Structures.WordStructures import Separator
from ITermExtractor.linguistic_filter import *
import ITermExtractor.Morph as m
import unittest


class TestMorphy(unittest.TestCase):
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

    def test_collocation_separator_tags(self):
        collocation = 'направление движения каждого отделения (подгруппы) и бойца-специалиста'
        expected_results = [ TaggedWord(word='направление', pos=PartOfSpeech.noun, case=Case.nominative, normalized='направление'),
                             TaggedWord(word='движения', pos=PartOfSpeech.noun, case=Case.genitive,
                                        normalized='движение'),
                             TaggedWord(word='каждого', pos=PartOfSpeech.adjective, case=Case.genitive,
                                        normalized='каждый'),
                             TaggedWord(word='отделения', pos=PartOfSpeech.noun, case=Case.genitive,
                                        normalized='отделение'),
                             Separator(symbol='('),
                             TaggedWord(word='подгруппы', pos=PartOfSpeech.noun, case=Case.genitive,
                                        normalized='подгруппа'),
                             Separator(symbol=')'),
                             TaggedWord(word='и', pos=PartOfSpeech.conjunction, case=Case.none,
                                        normalized='и'),
                             TaggedWord(word='бойца-специалиста', pos=PartOfSpeech.noun, case=Case.genitive,
                                        normalized='боец-специалист'),
                            ]
        results = m.tag_collocation(collocation)
        self.assertEqual(results, expected_results)

        collocation = 'состав группы обеспечения [9] (одно-два противотанковых орудия, два-три орудия полковой артиллерии), минометы, пулеметы, снайперы'
        expected_results = [ TaggedWord(word='состав', pos=PartOfSpeech.noun, case=Case.accusative, normalized='состав'),
                             TaggedWord(word='группы', pos=PartOfSpeech.noun, case=Case.genitive,
                                        normalized='группа'),
                             TaggedWord(word='обеспечения', pos=PartOfSpeech.noun, case=Case.genitive,
                                        normalized='обеспечение'),
                             Separator(symbol='('),
                             TaggedWord(word='одно-два', pos=PartOfSpeech.adverb, case=Case.none,
                                        normalized='одно-два'),
                             TaggedWord(word='противотанковых', pos=PartOfSpeech.adjective, case=Case.genitive,
                                        normalized='противотанковый'),
                             TaggedWord(word='орудия', pos=PartOfSpeech.noun, case=Case.genitive,
                                        normalized='орудие'),
                             Separator(symbol=','),
                             TaggedWord(word='два-три', pos=PartOfSpeech.numeral, case=Case.nominative,
                                        normalized='два-три'),
                             TaggedWord(word='орудия', pos=PartOfSpeech.noun, case=Case.genitive,
                                        normalized='орудие'),
                             TaggedWord(word='полковой', pos=PartOfSpeech.adjective, case=Case.nominative,
                                        normalized='полковой'),
                             TaggedWord(word='артиллерии', pos=PartOfSpeech.noun, case=Case.genitive,
                                        normalized='артиллерия'),
                             Separator(symbol=')'),
                             Separator(symbol=','),
                             TaggedWord(word='минометы', pos=PartOfSpeech.noun, case=Case.nominative,
                                        normalized='миномёт'),
                             Separator(symbol=','),
                             TaggedWord(word='пулеметы', pos=PartOfSpeech.noun, case=Case.nominative,
                                        normalized='пулемёт'),
                             Separator(symbol=','),
                             TaggedWord(word='снайперы', pos=PartOfSpeech.noun, case=Case.nominative,
                                        normalized='снайпер'),
                            ]
        results = m.tag_collocation(collocation)
        self.assertEqual(results, expected_results)

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
                             Separator(symbol='('),
                             TaggedWord(word='дивизион', pos=PartOfSpeech.noun, case=Case.nominative, normalized='дивизион'),
                             Separator(symbol=')'),
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

    def test_collocation_normal_form(self):
        variants_1 = [ Collocation(collocation='огонь артиллерии', pnormal_form='огонь артиллерия', freq=1),
                     Collocation(collocation='огня артиллерии', pnormal_form='огонь артиллерия', freq=1),
                     Collocation(collocation='огню артиллерии', pnormal_form='огонь артиллерия', freq=1),
                     Collocation(collocation='огне артиллерии', pnormal_form='огонь артиллерия', freq=1)]
        variants_2 = [Collocation(collocation='состояние инженерных оборудований',
                                  pnormal_form='состояние инженерный оборудование', freq=1),
                      Collocation(collocation='состоянием инженерных оборудований',
                                  pnormal_form='состояние инженерный оборудование', freq=1),
                      Collocation(collocation='состояний инженерного оборудования',
                                  pnormal_form='состояние инженерный оборудование', freq=1),
                      Collocation(collocation='состоянии инженерного оборудования',
                                  pnormal_form='состояние инженерный оборудование', freq=1),
                      Collocation(collocation='состояние инженерного оборудования',
                                  pnormal_form='состояние инженерный оборудование', freq=1),
                      ]
        index_1 = m.get_collocation_normal_form('огонь артиллерия', variants_1, 'огонь')
        index_2 = m.get_collocation_normal_form('состояние инженерный оборудование', variants_2, 'состояние')
        self.assertEqual(index_1, 0)
        self.assertEqual(index_2, 4)

if __name__ == "__main__":
    unittest.main()
