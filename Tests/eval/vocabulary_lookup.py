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

    def test_similarity(self):
        test_cases = [
            ('подавление экспрессия гена', 'экспрессия гена', 0.67),
            ('стволовая нервная клетка', 'стволовая клетка', 0.67),
            ('центральная нервная система', 'вегетативная нервная система', 0.5),
            ('центральная нервная система', 'центральная нервная система', 1.0),
            ('подавление экспрессия гена мишени', 'экспрессия гена', 0.5),
            ('институт химической биологии', 'институт химической биологии и фундаментальной медицины', 0.5),
            ('действие естественный отбор', 'естественный отбор', 0.67),
            ('полимеразная цепная реакция', 'полимеразная цепная реакция', 1.0),
            ('полимеразная цепная реакция', 'обратная полимеразная цепная реакция', 0.75),
            ('российская академия наук', 'российская академия медицинских наук', 0.75),
            ('генетическая дифференциация популяции', 'генетическая структура популяции', 0.5),
            ('фенотип множественная лекарственная устойчивость', 'множественная устойчивость к лекарственная препаратам', 0.5)
        ]
        for case in test_cases:
            sim = calc_similarity(case[0], case[1])
            self.assertAlmostEqual(sim, case[2], delta=0.01)

    def test_has_similar(self):
        test_cases = [
            'подавление экспрессия гена',
            'стволовая нервная клетка',
            'центральная нервная система',
            'подавление экспрессии гена мишени',
            'институт химической биологии',
            'действие естественного отбора',
            'полимеразная цепная реакция',
            'полимеразная цепная реакция',
            'российская академия наук',
            'генетическая дифференциация популяции',
            'фенотип множественной лекарственной устойчивости'
        ]
        self.assertTrue(has_similar('экспрессия гена', test_cases))
        self.assertTrue(has_similar('стволовая клетка', test_cases))
        self.assertTrue(has_similar('центральная нервная система', test_cases))
        self.assertFalse(has_similar('система общения между пользователями', test_cases))

if __name__ == "__main__":
    unittest.main()
