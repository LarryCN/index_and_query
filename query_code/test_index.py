import gzip
import cPickle
import config

def get_lexicon():
    #return cPickle.load(gzip.open(DATAPATH + LEXICON, 'rb'))
    return cPickle.load(open(config.DATAPATH + config.LEXICON, 'rb'))

def get_doc_dic():
    #return cPickle.load(gzip.open(DATAPATH + DOCDIC, 'rb'))
    return cPickle.load(open(config.DATAPATH + config.DOCDIC, 'rb'))

def lexiconinfo(data):
    print('length ', len(data))
    for i in data:
        print(i, data[i])

def docinfo(data):
    print('length ', len(data))
    for i in data:
        print(i, data[i])

import simple9

# term:file, start, end, doc_num
def get_postings(term, lexicon):
    t = lexicon[term]
    print(t)
    filename = config.INDEXPATH + str(t[0])
    #f = gzip.open(filename, 'rb')
    f = open(filename, 'rb')
    f.seek(t[1])
    data = f.read(t[2] - t[1])
    f.close()
    if config.SIMPLE9 == 1:
        a = []
        off = 0
        l = len(data)
        while off < l:
            a.append(int(data[off:off + 8], 16))
            off += 8
        print(a)
        print(len(a))
        data = simple9.simple9_decode(a)
    return data

"""--- for chunk wise ---"""
def term_info_parser(data):
    fileindex = data[0] & 0xffffffff
    chunkstart = (data[0] >> 32) & 0xffff
    chunkend = data[0] >> 48
    return [fileindex, chunkstart, chunkend] + data[1:]

def get_term_info(term, lexicon):
    info = lexicon[term]
    return term_info_parser(info)

def get_block(index, start, end):
    filename = config.INVERTEDPATH + str(index)
    f = open(filename, 'rb')
    f.seek(start)
    data = f.read(end - start)
    f.close()
    return data

def get_block_byinfo(info):
    return get_block(info[0], info[3], info[4])

def block_parser(data):
    metasize = data[0:8]
    metasize = int(metasize, 16) & 0x7fffff
    metadata = data[9:8 + metasize].split(' ')
    return metasize, [int(x) for x in metadata]

def get_chunkdata(cs, ce, data):
    off, doc_add = block_parser(data)
    off += 8
    print(doc_add, off)
    if not cs:
        start = 0
    else:
        start = doc_add[cs * 4 - 1]
    s = ''
    while cs <= ce:
        end = doc_add[4 * cs + 1]
        print(start + off, end + start + off)
        s += data[off + start: off + end + start]
        start = end
        cs += 1
    return s





