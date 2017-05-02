from ITermExtractor.Structures.WordStructures import Collocation
from ITermExtractor.linguistic_filter import *
import ITermExtractor.Morph as m
import unittest


class TestLinguisticFilter(unittest.TestCase):
    def test_filter_sentence(self):
        filter1 = NounPlusLinguisticFilter()
        filter2 = AdjNounLinguisticFilter()
        tagged_sentence = m.tag_collocation('Минометный батальон является мощным огневым средством пехоты во всех видах ее боевой деятельности')
        candidates = filter1.filter(tagged_sentence)

        expected_results = [Collocation(collocation='средством пехоты', pnormal_form='средство пехота', freq=1)]

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

        self.assertEqual(sorted(candidates, key=itemgetter('collocation')),
                         sorted(expected_results, key=itemgetter('collocation')))

    def test_concatenation(self):
        sentences = ['Огонь артиллерии планировать в соответствии с обеспеченностью боеприпасами',
                     'Подготовленные участки и огни артиллерии записывать на щитах орудий, таблицах за брусом, имея все необходимые данные для ведения огня артиллерии ночью и в условиях задымления',
                     'Система огня должна обеспечить непроницаемость боевых порядков для контратак пехоты противника и танков'
                     ]
        expected_results = [{'collocation': 'ведения огня', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'ведение огонь', 'llinked': [], 'id': 0},
                             {'collocation': 'ведения огня артиллерии', 'wordcount': 3, 'freq': 1, 'pnormal_form': 'ведение огонь артиллерия', 'llinked': [], 'id': 0},
                             {'collocation': 'контратак пехоты', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'контратака пехота', 'llinked': [], 'id': 0},
                             {'collocation': 'контратак пехоты противника', 'wordcount': 3, 'freq': 2, 'pnormal_form': 'контратака пехота противник', 'llinked': [], 'id': 0},
                             {'collocation': 'контратак пехоты противника танков', 'wordcount': 4, 'freq': 1, 'pnormal_form': 'контратака пехота противник танк', 'llinked': [], 'id': 0},
                             {'collocation': 'обеспеченностью боеприпасами', 'wordcount': 2, 'freq': 2, 'pnormal_form': 'обеспеченность боеприпас', 'llinked': [], 'id': 0},
                             {'collocation': 'огонь артиллерии', 'wordcount': 2, 'freq': 4, 'pnormal_form': 'огонь артиллерия', 'llinked': [], 'id': 0},
                             {'collocation': 'орудий таблицах', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'орудие таблица', 'llinked': [], 'id': 0},
                             {'collocation': 'пехоты противника', 'wordcount': 2, 'freq': 2, 'pnormal_form': 'пехота противник', 'llinked': [], 'id': 0},
                             {'collocation': 'пехоты противника танков', 'wordcount': 3, 'freq': 1, 'pnormal_form': 'пехота противник танк', 'llinked': [], 'id': 0},
                             {'collocation': 'противника танков', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'противник танк', 'llinked': [], 'id': 0},
                             {'collocation': 'система огня', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'система огонь', 'llinked': [], 'id': 0},
                             {'collocation': 'соответствии обеспеченностью', 'wordcount': 2, 'freq': 2, 'pnormal_form': 'соответствие обеспеченность', 'llinked': [], 'id': 0},
                             {'collocation': 'соответствии обеспеченностью боеприпасами', 'wordcount': 3, 'freq': 2, 'pnormal_form': 'соответствие обеспеченность боеприпас', 'llinked': [], 'id': 0},
                             {'collocation': 'условиях задымления', 'wordcount': 2, 'freq': 2, 'pnormal_form': 'условие задымление', 'llinked': [], 'id': 0},
                             {'collocation': 'участки огни', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'участок огонь', 'llinked': [], 'id': 0},
                             {'collocation': 'участки огни артиллерии', 'wordcount': 3, 'freq': 1, 'pnormal_form': 'участок огонь артиллерия', 'llinked': [], 'id': 0},
                             {'collocation': 'щитах орудий', 'wordcount': 2, 'freq': 1, 'pnormal_form': 'щит орудие', 'llinked': [], 'id': 0},
                             {'collocation': 'щитах орудий таблицах', 'wordcount': 3, 'freq': 1, 'pnormal_form': 'щит орудие таблица', 'llinked': [], 'id': 0}]
        tag_info = [m.tag_collocation(s) for s in sentences]
        tag_cache = dict([(word.word.lower(), word) for s in tag_info for word in s])
        collocations = []

        filter1 = NounPlusLinguisticFilter()
        for t in tag_info:
            fc = filter1.filter(t)
            collocations = collocations + fc

        result = concatenate_similar(tag_cache, collocations)
        linked_result = define_collocation_links(result)
        self.assertEqual(sorted(result, key=itemgetter('collocation')), sorted(expected_results, key=itemgetter('collocation')))
        # self.assertCountEqual()

#  Основная задача его заключается в непосредственной поддержке стрелковых рот и сопровождении их огнем и движением

if __name__ == "__main__":
    unittest.main()
