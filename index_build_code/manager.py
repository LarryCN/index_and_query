class manager:
    def __init__(self):
        self.blocknum = 0
        self.blocksize = config.BLOCKSIZE
        self.block = []
        self.state = 0
        self.blocklexicon = []
        self.count = 0
        self.lexicon = {}

import heapq
import gzip
import sys
import cPickle
import time
import config

def structrestore(data, name):
    filename = config.DATAPATH + name
    print('write ', filename, time.ctime())
    #cPickle.dump(data, gzip.open(filename, 'wb'))
    cPickle.dump(data, open(filename, 'wb'))
    print(time.ctime())

linelist = []

import simple9

def invertedindex_store(data, filenum, lexicon):
    global linelist 
    filename = config.INVERTEDPATH + str(filenum)
    print("write ", filename)
    #f = gzip.open(filename, 'wb')
    f = open(filename, 'wb')
    offset = 0
    s = ''
    for k in xrange(len(data)):
        d = data[k]
        term = linelist[k]
        num = lexicon[term][2]
        lexicon[term].append(num)
        if config.SIMPLE9 == 1:
            dd = []
            for i in xrange(len(d)):
                dd += d[i].split(',')
            a = [int(x) for x in dd]
            r = simple9.simple9_encode(a, len(a))
            r = [hex(x)[2:] for x in r]
            r = str(r)[1:-1].replace('\'', '').replace(',', '').replace(' ', '')
            s += r
        else:
            s += d[0]
            for i in range(1, len(d)):
                s += ',' + d[i]
        lexicon[term][1] = offset
        lexicon[term][2] = len(s)
        offset = len(s) 
    f.write(s)
    f.close()
    linelist = []

import chunkwise_compress

def invertedindex_chunkwise_store(data, filenum, lexicon):
    global linelist 
    filename = config.INVERTEDPATH + str(filenum)
    print("chunk wise write ", filename)
    f = open(filename, 'wb')
    iindex = chunkwise_compress.iindex()     # inverted index block object
    ilexicon = {}
    for k in xrange(len(data)):
        try:
            d = data[k]
            term = linelist[k]
            """ --------- chunk wise store -----------"""
            dd = []
            for i in xrange(len(d)):
                dd += d[i].split(',')
            a = [int(x) for x in dd]
            info = iindex.store(a)
            ilexicon[term] = info       # term: start_block_num, chunk, end_block_num, chunk
        except Exception as e:
            print(e)
            print(term)
        """ --------- chunk wise store end -------"""
    iindex.iindex_done()
    """ store inverted index, and record block postion """
    block_info = []
    off = 0
    s = ''
    for i in range(iindex.n):
        block = iindex.block[i]     # block: size(8bytes: 0x... store block.metadata len), metadata, chunkdata
        s += (block.off + block.metadata + block.chunkdata)
        l = len(s)
        if l - off > 65536:
            print(l - off, block.off, len(block.metadata), len(block.chunkdata))
        block_info.append([off, l])
        off = l
#    while 1:pass
    f.write(s)
    f.close()
    linelist = []
    """---- updata lexicon ----"""
    for t in ilexicon:
        info = ilexicon[t]
        num = lexicon[t][2]
        lexicon[t].append(num)
        lexicon[t][1] = block_info[info[0] - 1][0]   # info[0] start block  block_info[][0] start address 
        lexicon[t][2] = block_info[info[2] - 1][1]   # info[2] end block    block_info[][1] end address
        lexicon[t][0] |= (info[1] << 32 | info[3] << 48) # lexicon : chunknum end|chunknum start|file index, ... 


def mergesort(mgr):
    global linelist
    num = len(mgr.block)
    print('merge sort ', num)
    """ ----------------init----------------------------
    """
    term = []   # sub index orderlist  term list
    f = []      # file
    info = []   # sub index lexicon
    heap = []   # priority queue  
    count, threshold = [], []
    lexicon = {}
    termid = 0
    fileindex = 0
    indexcount = 0
    inverted = []
    size = 0
    for i in range(num):
        try:
            block = mgr.block[i]
            term.append(block.orderlist)
            print(block.blocknum);
            #f.append(gzip.open(block.path + str(block.blocknum), 'rb'))
            f.append(open(block.path + str(block.blocknum), 'rb'))
            info.append(block.lexicon)
            threshold.append(block.termid)
            heapq.heappush(heap, [term[i][0], i])
            count.append(0)
        except Exception as e:
            print(e)

    ''' --------------begin-------------------
    '''
    flag = 0
    while heap:
        s, i = heapq.heappop(heap)             # pop  get term, file index
        count[i] += 1
        """ lexicon and inverted index """
        if s not in lexicon:
            if flag:                           # need to store inverted index
                if config.CHUNKWISE == 1:
                    invertedindex_chunkwise_store(inverted, fileindex, lexicon)
                else:
                    invertedindex_store(inverted, fileindex, lexicon)
                fileindex += 1
                indexcount = 0
                inverted = []
                size = 0
                flag = 0
            lexicon[s] = [fileindex, indexcount, info[i][s][1]]  # token: file, line, doc num
            idx = indexcount
            termid += 1
            indexcount += 1
            inverted.append([])
            linelist.append(s)
        else:
            lexicon[s][2] += info[i][s][1]
            idx = lexicon[s][1]
        dinfo = f[i].readline().rstrip()
        if config.TMEP_COMPRESS == 1:
            r = simple9.simple9_decode_strhex(dinfo)
            dinfo = str(r)[1:-1]
        inverted[idx].append(dinfo)  # postings
        """ push new data into priority queue"""
        if count[i] < threshold[i]:
            heapq.heappush(heap, [term[i][count[i]], i])

        size += len(dinfo)
        if size > config.INDEXSIZE:
            flag = 1
    print('heap done')
    if config.CHUNKWISE == 1:
        invertedindex_chunkwise_store(inverted, fileindex, lexicon)
    else:
        invertedindex_store(inverted, fileindex, lexicon)

    structrestore(lexicon, 'lexicon')
    """
    for i in sorted(lexicon):
        print(i, lexicon[i])

    while 1:pass
    """
