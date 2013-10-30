#encoding:utf-8
'''
Created on 2012-4-16

@author: James
'''

class switch(object):
    '''
    # This class provides the functionality we want. You only need to look at
    # this if you want to know how this works. It only needs to be defined
    # once, no need to muck around with its internals.
    '''
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False
        
def unicoding(str):
    '''
    编码成unicode 16进制
    '''
    result_arr = []
    for x in str:
        result_arr.append("\u%04X"%ord(x))
    result = ''.join(result_arr)
    return result

def enicoding(str):
    '''
    从unicode 16进制解码
    '''
    result_arr = []
    source_arr = str.split('\u')
    for x in source_arr:
        if x!='':
            result_arr.append(unichr(int(x,16)))
    result = ''.join(result_arr)
    return result 

def strQ2B(ustring):  
    """把字符串全角转半角"""  
#    rstring = ""  
#    for uchar in ustring:  
#        inside_code=ord(uchar)  
#        if inside_code==0x3000:  
#            inside_code=0x0020  
#        else:  
#            inside_code-=0xfee0  
#        if inside_code<0x0020 or inside_code>0x7e:      #转完之后不是半角字符则返回原来的字符  
#            rstring += uchar  
#        rstring += unichr(inside_code)  
#    return rstring
    return ''.join(unichr(0x0020 if c == 0x3000 else c-0xfee0 if 0xff00 < c < 0xff80 else c) for c in map(ord, ustring))

def strB2Q(ustring):  
    """把字符串半角转全角"""  
#    rstring = ""  
#    for uchar in ustring:  
#        inside_code=ord(uchar)  
#        if inside_code<0x0020 or inside_code>0x7e:      #不是半角字符则返回原来的字符  
#            rstring += uchar  
#        if inside_code==0x0020: #除了空格其他的全角半角的公式为:半角=全角-0xfee0  
#            inside_code=0x3000  
#        else:  
#            inside_code+=0xfee0  
#        rstring += unichr(inside_code)  
#    return rstring
    return ''.join(unichr(0x3000 if c == 0x0020 else c+0xfee0 if 0x0020 < c < 0x0080 else c) for c in map(ord, ustring))
