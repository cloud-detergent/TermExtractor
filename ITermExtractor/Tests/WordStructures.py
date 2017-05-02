from ITermExtractor.Structures.WordStructures import Collocation
import unittest


class TestCollocation(unittest.TestCase):
    def test_inheritance(self):
        abc = Collocation("огонь артиллерии", 2, 0, "огонь артиллерия")
        ade = {'collocation': "огонь артиллерии", 'wordcount': 2, 'freq': 0, 'pnormal_form': "огонь артиллерия", 'llinked': list()}
        self.assertEqual(ade.items(), abc.items())

    def test_keyproperties(self):
        abc = Collocation("огонь артиллерии", 2, 0, "огонь артиллерия")
        self.assertEqual(abc.collocation, abc['collocation'])
        abc.freq = 1
        self.assertEqual(abc.freq, abc['freq'])

    @unittest.expectedFailure
    def test_keyproperties_error(self):
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


if __name__ == "__main__":
    unittest.main()
