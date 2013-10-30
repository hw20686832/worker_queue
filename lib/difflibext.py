#encoding:utf-8
__author__ = 'James Lau'
import difflib

class DocumentCompare(object):
    def __init__(self, rule):
        self.rule = rule
        self.opcodes = dict.fromkeys(["-->".join(k[:2]) for k in rule])
            
    """
    文档相似度比较，每个文档都分别有字段对应比较。每一对参加比较的字段都有相应的权重
    """
    def similarity(self, subject_doc, object_doc):
        """
        比较两个文档。subject_doc为主体文档（相似度参照方），object_doc为客体文档
        rules为比较规格：
        rules = [
            ['document_field1','counterpart_field1',0.5, 'str'],
            ['document_field2','counterpart_field2',0.5, 'num'], 
            ['document_field2','counterpart_field2',0.5, 'abs']
        ]#依次为文档的属性名、与之比较的文档的字段名、相似度权重
        返回相似度float
        
        匹配算法类型：
        str: 字符串相似度
        num: 数字浮动率
        abs: 绝对匹配
        """
        similarity_score = 0
        for r in self.rule:
            if subject_doc.get(r[0]) and object_doc.get(r[1]):
                try:
                    _score = self._compare(subject_doc[r[0]], object_doc[r[1]], target_algorithm = r[3])
                    similarity_score += _score * r[2]
                    self.opcodes['-->'.join(r[:2])] = "%f * %f = %f" % (_score, r[2], _score * r[2])
                except:
                    import traceback
                    traceback.print_exc()
                    print u"Error: %s %s >>> %s" % (r[0], subject_doc[r[0]], object_doc[r[1]])

        return similarity_score

    def _compare(self, tar1, tar2, target_algorithm = 'str'):
        try:
            target = self.__getattribute__("_%s_compare" % target_algorithm)
        except:
            target = self._str_compare

        return target(tar1, tar2)

    def _str_compare(self, tar1, tar2):

        """
        比较字符串，返回相似度float
        """
        __score = difflib.SequenceMatcher(None, unicode(tar1), unicode(tar2)).ratio()
        return __score

    def _num_compare(self, num1, num2):
        """
        数字浮动率
        """
        if not num1:
            num1 = 0
        __score = 1 - abs(float(num1) - float(num2))/float(num2)
        if __score < 0:
            __score = 0

        return __score

    def _abs_compare(self, tar1, tar2):
        """
        绝对匹配，返回1或0
        """
        return int(tar1 == tar2)

    def get_opcodes(self):
        return self.opcodes

    def mostsimilar(self, subject_doc, object_docs):
        """
        一个文档与多个文档进行比较，返回最相似的文档。subject_doc为主体文档（相似度参照方），object_docs为客体文档列表
        rules = [
            ['document_field1','counterpart_field1',0.5, 'str'],
            ['document_field2','counterpart_field2',0.5, 'num']
        ]#依次为文档的属性名、与之比较的文档的字段名、相似度权重
        返回：
        {
            'similarity':0,
            'doc':object_doc
        }
        """
        result = {
            'similarity':0
        }
        for object_doc in object_docs:
            __tmp_score = self.similarity(subject_doc, object_doc)
            if __tmp_score > result['similarity']:
                result['similarity'] = __tmp_score
                result['doc'] = object_doc

        return result


if __name__ == '__main__':
    rules = [
        ['title','title',0.2, 'str'],
        ['description','keyword',0.8, 'str'], 
        ['price', 'purchase_price', 0.2, 'num']
    ]

    doc1 = {
        'title':'abcdefg',
        'description': u'我早已为你种下九百九十九朵玫瑰', 
        'price': 40000
    }

    doc2 = {
        'id':1,
        'title':'kkkkkk',
        'keyword': u'送你九十九朵玫瑰', 
        'purchase_price': 38000
    }

    doc3 = {
        'id':2,
        'title':'anckkk',
        'keyword': u'九百九十朵玫瑰九十九块', 
        'purchase_price': 43000
    }

    dc = DocumentCompare(rules)
    o = dc.mostsimilar(doc1, [doc2, doc3])

    print '%d -> %s' % (o['doc']['id'], o['similarity'])
    print dc.get_opcodes()
