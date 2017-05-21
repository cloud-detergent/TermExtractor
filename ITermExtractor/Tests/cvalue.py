from ITermExtractor.linguistic_filter import NounPlusLinguisticFilter
import ITermExtractor.stat.cvalue_revisited as cvalue
import Runner
import unittest


class TestStatMethod(unittest.TestCase):
    @unittest.skip("not for now")
    def test_threaded_results(self):
        with open("../../data/input_text.txt", mode="rt", encoding="utf-8") as f:
            input_text = f.read()
        tagged_sentence_list = Runner.parse_text(input_text=input_text)
        filter1 = NounPlusLinguisticFilter()
        terms1 = filter1.filter_text(tagged_sentence_list)
        cvalue.threshold = 0.5
        cvalue_res_1 = cvalue.calculate(terms1, is_single_threaded=True)
        cvalue_res_2 = cvalue.calculate(terms1, is_single_threaded=False)
        self.assertEqual(len(cvalue_res_1), len(cvalue_res_2))
        self.assertEqual(cvalue_res_1, cvalue_res_2)

    def test_threshold_property(self):
        cvalue.set_threshold(0)
        self.assertEqual(cvalue.THRESHOLD, 0)

        cvalue.set_threshold(2)
        self.assertEqual(cvalue.THRESHOLD, 2)

        cvalue.set_threshold(-2)
        self.assertEqual(cvalue.THRESHOLD, 0)


if __name__ == "__main__":
    unittest.main()
