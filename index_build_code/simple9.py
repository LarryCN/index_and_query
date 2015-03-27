# by larry Mar 15th, 2015
SIMPLE_9 = 0x90000000
SIMPLE_8 = 0x80000000
SIMPLE_7 = 0x70000000
SIMPLE_6 = 0x60000000
SIMPLE_5 = 0x50000000
SIMPLE_4 = 0x40000000
SIMPLE_3 = 0x30000000
SIMPLE_2 = 0x20000000
SIMPLE_1 = 0x10000000
#       n:num  max:threshold code    shift
en_simple = [[28,         1, SIMPLE_9, 1],     
             [14,         3, SIMPLE_8, 2],
             [ 9,         7, SIMPLE_7, 3],
             [ 7,        15, SIMPLE_6, 4],
             [ 5,        31, SIMPLE_5, 5],
             [ 4,       127, SIMPLE_4, 7],
             [ 3,       511, SIMPLE_3, 9],
             [ 2,     16383, SIMPLE_2,14],
             [ 1, 268435455, SIMPLE_1,28]
           ]
""" first 4 bits  1: 1; 2: 2; 3: 3; 4: 4; 5: 5; 6: 7; 7: 9; 8: 14; 9: 28; others not simple9 encode
    -1  28bit 0 ~ 268435455       -7  4bit 0 ~ 15     
    -2  14bit 0 ~ 16383           -9  3bit 0 ~ 7
    -3  9bit  0 ~ 511             -14 2bit 0 ~ 3
    -4  7bit  0 ~ 127             -28 1bit 0 ~ 1
    -5  5bit  0 ~ 31

    0000  ... 3 2 1
    4bit    data
"""
""" input a: int list
    length: len(a)
"""
def simple9_encode(a, length):
    global en_simple
    off = 0        # count encode length
    result = []
    while off < length:
        for t in en_simple:
            n, threshold, code, shift = t[0], t[1], t[2], t[3]
            if off + n <= length and max(a[off:off + n]) <= t[1]:
                tmp = a[off]
                for i in xrange(1, n): 
                    tmp |= (a[off + i] << (shift * i))
                result.append(tmp | t[2])
                off += n
                break
    return result

de_simple = {SIMPLE_9: [28,      0x1, 1],     
             SIMPLE_8: [14,      0x3, 2],
             SIMPLE_7: [9,       0x7, 3],
             SIMPLE_6: [7,       0xf, 4],
             SIMPLE_5: [5,      0x1f, 5],
             SIMPLE_4: [4,      0x7f, 7],
             SIMPLE_3: [3,     0x1ff, 9],
             SIMPLE_2: [2,    0x3fff,14],
             SIMPLE_1: [1, 0xfffffff,28]
           }
""" try:
        r = simple9_decode(a)
    except:
        print('not encode in simple9')
    input a: 32bit int
    output result: int list
"""
def simple9_decode(a):
    global de_simple
    result = []
    for t in a:
        code = t & 0xf0000000
        data = t & 0xfffffff
        info = de_simple[code]
        n, bit, shift = info[0], info[1], info[2]
        for i in range(n):
            result.append(data & bit)
            data >>= shift
    return result
"""
def simple9_decode_strhex(s):
    a = []
    off = 0
    l = len(s)
    while off < l:
        a.append(int(s[off:off + 8], 16))
        off += 8
    return simple9_decode(a)
"""
def simple9_decode_strhex(s):
    global de_simple
    result = []
    off = 0
    l = len(s)
    while off < l:
        t = int(s[off:off + 8], 16)
        off += 8
        code = t & 0xf0000000
        data = t & 0xfffffff
        info = de_simple[code]
        n, bit, shift = info[0], info[1], info[2]
        for i in range(n):
            result.append(data & bit)
            data >>= shift
    return result
