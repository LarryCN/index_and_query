import index_op
import time
import config
import heapq

from index_if import openlist as openlist
from index_if import closelist as closelist
from index_if import nextGEQ as nextGEQ
from index_if import getFreq as getFreq


info = 0

def init():
    global info
    info = index_op
    info.index_init()

def sub_daat(tobj):
    doc_dic = index_op.doc_dic
    bm25_cal = index_op.method_bm25.cal
    top_n = config.TOP_NUM
    ldoc = 0
    ret = []
    topmin = 0
    flag = 0
    maxid = index_op.maxid
    ft = [obj[0] for obj in tobj]
    docid = 0
    while docid < maxid:
        docid = nextGEQ(tobj[0][1], docid)  # shortest list
        if docid >= maxid:
            break
        dmax = docid
        for i in xrange(1, len(tobj)):                # check other list whether or not contain docid
            tmp = nextGEQ(tobj[i][1], docid)
            if tmp > dmax: dmax = tmp

        if dmax != docid:   
            docid = dmax                             # not all contain docid
        else:
            fdt = []
            for obj in tobj:
                freq = getFreq(obj[1])
                fdt.append(freq)

            """ cal bm25 """
            vbm25 = bm25_cal(ft, fdt, doc_dic[docid][1])
            if not flag:
                ret.append([vbm25, docid])
                if len(ret) >= top_n:
                    flag = 1
                    topmin = min(ret)[0]
            else:
                if vbm25 > topmin:
                    tmp = min(ret)
                    ret.remove(tmp)
                    ret.append([vbm25, docid])
                    topmin = min(ret)[0]

            docid += 1
            ldoc += 1
    return ret, ldoc

""" input a list of terms, input should not be []
"""
def daat(terms):
    terms = terms.split(' ')
    tobj = []
    """open list"""
    mtime = time.time()
    print(mtime)
    try:
        for t in terms:
            obj = openlist(t)
            tobj.append([obj.doc_num, obj])
    except Exception as e:
        print(e)
        print('there is some terms not in the index, so no result')
        return []

    """ DAAT """
    tobj.sort()  # sort by doc_nums include term
    print(tobj)
    #print('############### DAAT ##################')
    ret, ldoc = sub_daat(tobj)
    """close list"""
    #print('=============close list===============')
    for obj in tobj:
        closelist(obj[1])

    result = []
    count = 0
    for i in ret:
        docid = i[1]
        url = index_op.get_url(docid)
        result.append([url, i[0]])
        count += 1
        if count >= config.TOP_NUM:
            break
    print('done', time.time() - mtime, ldoc)
    return result

import cindex

def cdaat(terms):
    terms = terms.split(' ')
    """open list"""
    #mtime = time.time()
    tobj = []
    try:
        for t in terms:
            tobj.append([index_op.lexicon[t][3], t])
        tobj.sort()  # sort by doc_nums include term
    except Exception as e:
        print(e)
        print('there is some terms not in the index, so no result')
        return []

    """ DAAT """
    tlist = []
    #print(tobj)
    for t in tobj:
        tlist.append(openlist(t[1]))
    #print('############### DAAT ##################')
    ret = cindex.subdaat(tlist, info.doc_dic)
    rdocid = [ret[x * 2] for x in xrange((len(ret) >> 1))]
    result = []
    count = 0
    for i in xrange(len(rdocid)):
        docid = rdocid[i]
        url = index_op.get_url(docid)
        result.append([ret[i * 2 + 1], url])
        count += 1
        if count >= config.TOP_NUM:
            break
    result.sort()
    result.reverse()
    #print(ret[-1], time.time() - mtime)
    return result, ret[-1]


def lexicon_test():
    l = info.lexicon
    """
    for t in sorted(l):
        print(t)
        if t == 'warzones':
            print("------------------------ ")
    """ 
    for t in sorted(l):
        mtime = time.time()
        r , count = cdaat(t)
        c = l[t][3]
        print(t, c, count, time.time() - mtime)
        if c!= count:
            print('----------------------------------->')
    
    print('done')

def test():
    s = ['i like you', 'the out', 'computer science', 'let it go', 'where to go', 'best place', 'war of the world', 'justice and false', 'rich or poor',
        'international law', 'do some math', 'keep zoo', '11 great things', 'u know result', 'sport games', 'stay at home']
    print('begin')
    mtime = time.time()
    for j in range(5):
        for i in s:
            r = cdaat(i)
    print('done', time.time() - mtime)

def query():
    q = raw_input("Please enter here(return to query): ")
    try:
        s = "query " + q
        print(s)
        mtime = time.time()
        r ,count = cdaat(q.rstrip())
        mtime = time.time() - mtime
        print("results: ")
        for i in range(len(r)):
            s = "URL " + r[i][1] + 'bm25 value: ' + str(r[i][0]) 
            print(s)
        print("")
        s = "Time cost: " + str(mtime) + 's' + " total " + str(count) + ' query results'
        print(s)
        print("")
    except Exception as e:
        print(e)
        print("please reenter correctly")

import cProfile
if __name__ == '__main__':
    print('larry------')
    mtime = time.time()
    init()
    print("init done", time.time() - mtime)
    print("")
    print("")
    while 1:
        query()
    #lexicon_test()
    #cProfile.run('print test()')
    #r = daat('out')
