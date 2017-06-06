from ITermExtractor.Structures.WordStructures import Collocation
from ITermExtractor.linguistic_filter import *
from TextImporter import PlainTextImporter
import ITermExtractor.Morph as m
import unittest
import Runner
import os


class TestLinguisticFilter(unittest.TestCase):
    def test_filter_sentence(self):
        filter1 = NounPlusLinguisticFilter()
        filter2 = AdjNounLinguisticFilter()
        tagged_sentence = m.tag_collocation('Минометный батальон является мощным огневым средством пехоты во всех видах ее боевой деятельности')
        candidates = filter1.filter(tagged_sentence)

        expected_results = [Collocation(collocation='средством пехоты', pnormal_form='средство пехота', freq=1)]

        candidates = [r for r in candidates if r.wordcount > 1]
        self.assertEqual(sorted(candidates, key=itemgetter('collocation')), sorted(expected_results, key=itemgetter('collocation')))

        candidates = filter2.filter(tagged_sentence)
        expected_results = [Collocation(collocation='минометный батальон', pnormal_form='миномётный батальон', freq=1),
                            Collocation(collocation='боевой деятельности', pnormal_form='боевой деятельность', freq=1),
                            Collocation(collocation='всех видах', pnormal_form='весь вид', freq=1),
                            Collocation(collocation='мощным огневым средством', pnormal_form='мощный огневой средство', freq=1),
                            Collocation(collocation='мощным огневым средством пехоты', pnormal_form='мощный огневой средство пехота', freq=1),
                            Collocation(collocation='огневым средством', pnormal_form='огневой средство', freq=1),
                            Collocation(collocation='огневым средством пехоты', pnormal_form='огневой средство пехота', freq=1),
                            Collocation(collocation='средством пехоты', pnormal_form='средство пехота', freq=1)]

        candidates = [r for r in candidates if r.wordcount > 1]
        self.assertEqual(sorted(candidates, key=itemgetter('collocation')),
                         sorted(expected_results, key=itemgetter('collocation')))

    def test_concatenation(self):
        sentences = ['Огонь артиллерии планировать в соответствии с обеспеченностью боеприпасами',
                     'Подготовленные участки и огни артиллерии записывать на щитах орудий, таблицах за брусом, имея все необходимые данные для ведения огня артиллерии ночью и в условиях задымления',
                     'Система огня должна обеспечить непроницаемость боевых порядков для контратак пехоты противника и танков'
                     ]
        expected_results = [ {'collocation': 'ведения огня', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'ведение огонь', 'llinked': [], 'id': 0},
                             {'collocation': 'ведения огня артиллерии', 'wordcount': 3, 'freq': 1, 'pnormal_form': 'ведение огонь артиллерия', 'llinked': [], 'id': 0},
                             {'collocation': 'контратак пехоты', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'контратака пехота', 'llinked': [], 'id': 0},
                             {'collocation': 'контратак пехоты противника', 'wordcount': 3, 'freq': 1, 'pnormal_form': 'контратака пехота противник', 'llinked': [], 'id': 0},
                             {'collocation': 'обеспеченностью боеприпасами', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'обеспеченность боеприпас', 'llinked': [], 'id': 0},
                             {'collocation': 'огонь артиллерии', 'wordcount': 2, 'freq': 3, 'pnormal_form': 'огонь артиллерия', 'llinked': [], 'id': 0},
                             {'collocation': 'пехоты противника', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'пехота противник', 'llinked': [], 'id': 0},
                             {'collocation': 'система огня', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'система огонь', 'llinked': [], 'id': 0},
                             {'collocation': 'условиях задымления', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'условие задымление', 'llinked': [], 'id': 0},
                             {'collocation': 'щитах орудий', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'щит орудие', 'llinked': [], 'id': 0}]
        tag_info = [m.tag_collocation(s) for s in sentences]
        tag_cache = dict([(sentence_part.word.lower(), sentence_part)
                          for s in tag_info
                          for sentence_part in s if isinstance(sentence_part, TaggedWord)])
        collocations = []

        filter1 = NounPlusLinguisticFilter()
        for t in tag_info:
            fc = filter1.filter(t)
            collocations = collocations + fc

        result = concatenate_similar(tag_cache, collocations)
        linked_result = define_collocation_links(result)

        sorted_result = sorted([r for r in result if r.wordcount > 1], key=itemgetter('collocation'))
        sorted_expected_results = sorted(expected_results, key=itemgetter('collocation'))
        self.assertEqual(sorted_result, sorted_expected_results)

        self.assertCountEqual(result, linked_result)
        self.assertEqual(sorted(result, key=itemgetter('wordcount')), linked_result)

    def test_integrity_small(self):
        sentences = ['Огонь артиллерии планировать в соответствии с обеспеченностью боеприпасами',
                     'Подготовленные участки и огни артиллерии записывать на щитах орудий, таблицах за брусом, имея все необходимые данные для ведения огня артиллерии ночью и в условиях задымления',
                     'Система огня должна обеспечить непроницаемость боевых порядков для контратак пехоты противника и танков'
                     ]
        tag_info = [m.tag_collocation(s) for s in sentences]
        filter1 = NounPlusLinguisticFilter()
        collocations = filter1.filter_text(tag_info)
        result_with_links = list(filter(lambda x: len(x.llinked) > 0, collocations))
        result_dict = dict([(r.id, r) for r in collocations])
        link_integrity_checks = [all(link in result_dict for link in p.llinked) for p in result_with_links]
        self.assertTrue(all(link_integrity_checks))

    def test_integrity_big(self):
        text_importer = PlainTextImporter(os.path.join('..', 'data', 'input_text.txt'))
        input_text = text_importer.get_text()
        tag_info = Runner.parse_text(input_text)

        filter1 = NounPlusLinguisticFilter()
        collocations = filter1.filter_text(tag_info)
        result_with_links = list(filter(lambda x: len(x.llinked) > 0, collocations))

        result_dict = dict([(r.id, r) for r in collocations])
        # self.assertEqual(sorted(collocations, key=itemgetter('id')), sorted(result_with_links, key=itemgetter('id')))
        link_integrity_checks = [all(link in result_dict for link in p.llinked) for p in result_with_links]
        self.assertTrue(all(link_integrity_checks))

    def test_link_definer(self):
        text_importer = PlainTextImporter(os.path.join('..', 'data', 'input_text.txt'))
        filter1 = NounPlusLinguisticFilter()
        input_text = text_importer.get_text()
        sentences = Runner.parse_text(input_text)
        collocations = []

        for t in sentences:
            fc = filter1.filter(t)
            collocations = collocations + fc

        # tag_cache = dict([(spart.word.lower(), spart) for s in sentences for spart in s if isinstance(spart, TaggedWord)])
        cache = []
        for s in sentences:
            for sentence_part in s:
                if isinstance(sentence_part, Separator) or sentence_part is None:
                    continue
                word = sentence_part
                case = Case.nominative if word.pos in [PartOfSpeech.noun, PartOfSpeech.adjective] else word.case
                normal_word = TaggedWord(word=word.normalized, pos=word.pos, case=case, normalized=word.normalized)
                cache.append(normal_word)
        tag_cache = dict([(c.normalized, c) for c in cache])

        result = concatenate_similar(tag_cache, collocations)
        linked_result = define_collocation_links(result)
        self.assertEqual(sorted(result, key=itemgetter('wordcount')), linked_result)

        result_with_links = list(filter(lambda x: len(x.llinked) > 0, linked_result))
        result_dict = dict([(r.id, r) for r in linked_result])

        link_integrity_checks = [all(link in result_dict for link in p.llinked) for p in result_with_links]
        self.assertTrue(all(link_integrity_checks))
#  Основная задача его заключается в непосредственной поддержке стрелковых рот и сопровождении их огнем и движением

    def test_collocation_retrieval(self):
        sentence_piece = [TaggedWord(word='состав', pos=PartOfSpeech.noun, case=Case.accusative, normalized='состав'),
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

        # <editor-fold desc="# No separator test suite">
        result_start_one = retrieve_collocation(sentence_piece, 0, 1)
        result_start_two = retrieve_collocation(sentence_piece, 0, 2)
        result_start_three = retrieve_collocation(sentence_piece, 0, 3)

        expected_results_start_one = [
            TaggedWord(word='состав', pos=PartOfSpeech.noun, case=Case.accusative, normalized='состав')]

        expected_results_start_two = [
            TaggedWord(word='состав', pos=PartOfSpeech.noun, case=Case.accusative, normalized='состав'),
            TaggedWord(word='группы', pos=PartOfSpeech.noun, case=Case.genitive,
                       normalized='группа')]

        expected_results_start_three = [
            TaggedWord(word='состав', pos=PartOfSpeech.noun, case=Case.accusative, normalized='состав'),
            TaggedWord(word='группы', pos=PartOfSpeech.noun, case=Case.genitive,
                       normalized='группа'),
            TaggedWord(word='обеспечения', pos=PartOfSpeech.noun, case=Case.genitive,
                       normalized='обеспечение')]

        self.assertEqual(result_start_one, expected_results_start_one)
        self.assertEqual(result_start_two, expected_results_start_two)
        self.assertEqual(result_start_three, expected_results_start_three)

        # </editor-fold>

        # <editor-fold desc="# Separator in the middle test suite">
        result_two = retrieve_collocation(sentence_piece, 2, 2)
        result_three = retrieve_collocation(sentence_piece, 2, 3)

        expected_results_two = [
            TaggedWord(word='обеспечения', pos=PartOfSpeech.noun, case=Case.genitive,
                       normalized='обеспечение')]

        expected_results_three = [
            TaggedWord(word='обеспечения', pos=PartOfSpeech.noun, case=Case.genitive,
                       normalized='обеспечение')]

        self.assertEqual(result_two, expected_results_two)
        self.assertEqual(result_three, expected_results_three)

        # </editor-fold>

        # <editor-fold desc="# Separator in the start test suite">
        result_start_one = retrieve_collocation(sentence_piece, 3, 1)
        result_start_two = retrieve_collocation(sentence_piece, 3, 2)
        result_start_three = retrieve_collocation(sentence_piece, 3, 3)

        self.assertEqual(result_start_one, list())
        self.assertEqual(result_start_two, list())
        self.assertEqual(result_start_three, list())

        # </editor-fold>


def is_integral(collocation_list: List[Collocation]) -> bool:
    collocation_dict = dict([(r.id, r) for r in collocation_list])
    collocation_with_links = list(filter(lambda x: len(x.llinked) > 0, collocation_list))
    link_integrity_checks = [all(link in collocation_dict for link in p.llinked) for p in collocation_with_links]
    flag = all(link_integrity_checks)
    return flag

if __name__ == "__main__":
    unittest.main()
