# by larry Mar 17th, 2015

""" 0   < 128       --> 0XXXXXXX
    128 < 128 * 128 --> 1XXXXXXX 0XXXXXXX
    ...
"""
def varbyte_encode(a):
    result = []
    for i in a:
        if i >= 128:
            t = i & 0x7f
            i = i >> 7
            count = 1
            while i >= 128:
                t |= ((i & 0x7f | 0x80) << 8 * count)
                count += 1
                i = i >> 7
            t |= ((i & 0x7f | 0x80) << 8 * count)
        else:
            t = i
        result.append(t)
    return result

def varbyte_decode(a):
    result = []
    for i in a:
        t = 0
        count = 0
        while i > 128:
            t |= ((i & 0x7f) << count * 7)
            i >>= 8
            count += 1
        t |= (i & 0x7f) << count * 7
        result.append(t)
    return result


