import config
import cPickle
import bm25
import lru

lexicon = {}
doc_dic = {}
maxid = 0
method_bm25 = None
lru_cache = None
index_size = []

class filenode:
    def __init__(self, index, term):
        self.count = 1
        self.term = [term]
        self.f = open(config.INVERTEDPATH + str(index), 'rb')

filemanager = {}

def file_open(index, term):
    global filemanager
    if index in filemanager:
        node = filemanager[index]
        node.count += 1
        node.term.append(term)
    else:
        filemanager[index] = filenode(index, term)

def file_close(index, term):
    global filemanager
    if index in filemanager:
        node = filemanager[index]
        if term not in node.term:
            print('this term has not been using the file anymore')
            return 
        node.count -= 1
        node.term.remove(term)
        if node.count == 0:   # no resource using this file anymore remove the node
            node.f.close()
            filemanager.pop(index)
    else:
        print('file',index, 'has closed')

def get_f(index):
    global filemanager
    return filemanager[index].f

def get_lexicon():
    return cPickle.load(open(config.DATAPATH + config.LEXICON, 'rb'))

def get_doc_dic():
    return cPickle.load(open(config.DATAPATH + config.DOCDIC, 'rb'))

""" term : chunkend| chunkstart| fileindex, start_addr, end_addr, doc_num
                  48-----------32--------0
"""
def term_info_parser(data):
    fileindex = data[0] & 0xffffffff
    chunkstart = (data[0] >> 32) & 0xffff
    chunkend = data[0] >> 48
    return [fileindex, chunkstart, chunkend] + data[1:]

""" for chunkwise """
def get_term_info(term):
    global lexicon
    info = lexicon[term]
    return term_info_parser(info)

def get_cache_data(index, start):
    global lru_cache, indexsize
    start = start - (start & (config.C_BLOCKSIZE - 1))  #block start addr
    data = lru_cache.get((index, start))
    if data != -1:   # hit
        return data, start
    f = get_f(index)
    f.seek(start)
    data = f.read(config.C_BLOCKSIZE)
    lru_cache.set((index, start), data)
    return data, start


def get_metadata_bak(index, start, end):
    f = get_f(index)
    """metasize"""
    f.seek(start)
    metasize = f.read(8)
    metasize = int(metasize, 16) & 0x7fffff
    """metadata"""
    f.seek(start + 9)
    metadata = f.read(metasize - 1).split(' ')
    """ fixed me to add file manager """
    return metasize, metadata

def get_chunkdata_bak(index, start, end):
    f = get_f(index)
    f.seek(start)
    data = f.read(end - start)
    return data


def get_metadata(index, start):
    data, off = get_cache_data(index, start)
    """metasize"""
    metasize = data[:8]
    metasize = int(metasize, 16) & 0x7fffff
    """metadata"""
    off = start - off + 9
    metadata = data[off: metasize].split(' ')
    """ fixed me to add file manager """
    return metasize, metadata

def get_chunkdata(index, start, end):
    data, off = get_cache_data(index, start)
    off = start - off
    data = data[off: off + end - start]
    return data

def get_doc_len(docid):
    global doc_dic
    if docid not in doc_dic:
        print('-------', docid)
    return doc_dic[docid][1]

def get_url(docid):
    global doc_dic
    return doc_dic[docid][0]

import os
import cindex

def get_index_size():
    global index_size
    for i in range(config.INDEX_NUM):
        index_size.append(os.path.getsize(config.INVERTEDPATH + str(i)))

def index_init():
    global lexicon, doc_dic, maxid, method_bm25, lru_cache, index_size
    print('index init..............')
    lexicon = get_lexicon()
    doc_dic = get_doc_dic()
    maxid = len(doc_dic)
    if config.CINDEX == 1:
        info = [config.CHUNKSIZE, config.C_BLOCKSIZE, config.TOP_NUM, config.C_BLOCKSIZE, 238, config.CACHE_SIZE, maxid, maxid]
        t = 0;
        for d in doc_dic:
            t += doc_dic[d][1]
        d_avg = t * 1.0 / maxid
        print('doc avg ', d_avg)
        get_index_size()
        cindex.init(info, d_avg, index_size)
    else:
        get_index_size()
        method_bm25 = bm25.BM25(maxid, doc_dic)
        lru_cache = lru.LRU()
    print('index init done')

