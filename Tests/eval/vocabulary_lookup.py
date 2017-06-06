from eval.vocabulary_lookup import *
import unittest
import random, string


class TestVocabularyLookup(unittest.TestCase):
    def test_random_selection(self):
        random.seed()
        pseudo_term_list = [' '.join(
            ''.join([random.choice(string.ascii_lowercase) for l in range(random.randint(5, 10))])
            for word_count in range(1, random.randint(2, 6)))
            for i in range(300, random.randint(301, 1000))]

        requirements = {
            1: random.randint(10, 50),
            2: random.randint(10, 50),
            3: random.randint(10, 50),
            4: random.randint(10, 50),
            5: random.randint(10, 50)
        }
        excerpt = select_random_excerpt([(t, 0) for t in pseudo_term_list], requirements)
        check_list = [len([t for t, misc in excerpt if len(t.split()) == k ]) == v for k,v in requirements.items()]
        self.assertEqual(len(excerpt), sum(requirements.values()))
        self.assertTrue(all(check_list))

if __name__ == "__main__":
    unittest.main()
