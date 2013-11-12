#coding: utf-8
from collections import defaultdict

from jieba.posseg import cut

def split(words):
    result = defaultdict(set)
    rs = cut(words)
    for r in rs:
        if r.flag in ('cb', 'cf'):
            result[r.flag].add(r.word)

    return result
            
def splitting(words):
    seg_result = cut(words)
    result = []
    for w in seg_result:
        result.append([w.word, [w.flag]])
        
    return result