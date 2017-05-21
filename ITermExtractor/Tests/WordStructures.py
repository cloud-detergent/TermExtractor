from ITermExtractor.Structures.WordStructures import Collocation
from copy import deepcopy
import unittest
import pickle


class TestCollocation(unittest.TestCase):
    def test_inheritance(self):
        abc = Collocation("огонь артиллерии", 2, 0, "огонь артиллерия")
        ade = {'collocation': "огонь артиллерии", 'wordcount': 2, 'freq': 0, 'pnormal_form': "огонь артиллерия", 'llinked': list()}
        self.assertTrue(ade == abc)

    def test_key_properties(self):
        abc = Collocation("огонь артиллерии", 2, 0, "огонь артиллерия")
        abc.freq = 1
        self.assertEqual(abc.collocation, abc['collocation'])
        self.assertEqual(abc.freq, abc['freq'])
        self.assertEqual(abc.wordcount, abc['wordcount'])
        self.assertEqual(abc.pnormal_form, abc['pnormal_form'])
        self.assertEqual(abc.llinked, abc['llinked'])
        self.assertEqual(abc.id, abc['id'])

    def test_property_values(self):
        abc = Collocation("огонь артиллерии", 2, 1, "огонь артиллерия", [12, 17], 22)
        self.assertEqual(abc.collocation, 'огонь артиллерии')
        self.assertEqual(abc.wordcount, 2)
        self.assertEqual(abc.freq, 1)
        self.assertEqual(abc.pnormal_form, 'огонь артиллерия')
        self.assertEqual(abc.llinked, [12, 17])
        self.assertEqual(abc.id, 22)

    @unittest.expectedFailure
    def test_key_properties_error(self):
        abc = Collocation("огонь артиллерии", 2, 0, "огонь артиллерия")
        self.assertRaises(KeyError, abc.value)
        self.assertRaises(KeyError, abc.__setattr__('value', 2))

    def test_freq_increment(self):
        abc = Collocation("огонь артиллерии", 2, 0, "огонь артиллерия")
        abc.add_freq()
        self.assertEqual(abc.freq, 1)
        abc.add_freq(5)
        self.assertEqual(abc.freq, 6)

    def test_collocation_wordcount(self):
        abc = Collocation()
        abc.collocation = "огонь артиллерии"
        self.assertEqual(abc.wordcount, 2)
        fer = Collocation(collocation="новый день", freq=3, cid=97, pnormal_form="новый день")
        self.assertEqual(fer.wordcount, 2)

    def test_equality(self):
        abcd = Collocation(collocation="огонь артиллерии")
        efgh = Collocation(collocation="огонь артиллерии", wordcount=2)
        self.assertEqual(abcd, efgh)

        abc = Collocation("исходный корпус", pnormal_form="исходный корпус")
        ade = {'collocation': "исходный корпус", 'wordcount': 2, 'freq': 0, 'pnormal_form': "исходный корпус",
               'llinked': [12, 17]}
        self.assertTrue(ade == abc)

    def test_collocation_deepcopy(self):
        a1 = Collocation(collocation="огонь артиллерии", wordcount=2)
        a1_id = id(a1)
        a1_attr_id = [id(v) for v in a1.values()]

        a2 = deepcopy(a1)
        a2_id = id(a1)
        a2_attr_id = [id(v) for v in a1.values()]
        self.assertEqual(a1.items(), a2.items())
        a1.freq = 3
        a1.pnormal_form = "огонь артиллерия"

        self.assertNotEqual(a1.items(), a2.items())

    def test_collocation_list_deepcopy(self):
        a_list = [Collocation(collocation="огонь артиллерии"), Collocation("исходный корпус")]
        a_list_scopy = list(a_list)
        a_list_copy = deepcopy(a_list)
        self.assertEqual(a_list, a_list_copy)
        self.assertEqual(a_list, a_list_scopy)
        a_list[0].freq = 3
        a_list[0].pnormal_form = "огонь артиллерия"

        self.assertNotEqual(a_list, a_list_copy)
        self.assertEqual(a_list, a_list_scopy)

    def test_pickle_ability(self):
        originals = [Collocation(collocation="огонь артиллерии"), Collocation("исходный корпус")]
        packed = [pickle.dumps(o) for o in originals]
        unpacked = [pickle.loads(p) for p in packed]
        self.assertEqual(originals, unpacked)


if __name__ == "__main__":
    unittest.main()
