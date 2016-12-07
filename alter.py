import os
import ast
import ITermExtractor.stat.cvalue as cval

cache = os.path.join('data', 'обработанное за полчаса 15 ноя.txt')
terms = {}
with open(cache, mode='r', encoding='utf-8') as f:
    contents = f.read()
    terms = ast.literal_eval(contents)


term_candidates_list = [cval.collocation_tuple(collocation=k, freq=v, wordcount=len(k.split())) for k, v in terms.items()]
term_candidates_list.sort(key=lambda x: x.wordcount, reverse=True)
highest_wcount = term_candidates_list[0].wordcount

terms_list = cval.calculate(term_candidates_list, highest_wcount)

print('fin')
