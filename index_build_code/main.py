import gzip
import time
import cPickle
import parser
import sys
import manager
import subindex
import config

PENDING = 0
RUNNING = 1
CHECKING = 2

doc_dic = {}
docid = 0
url_dic = {}

mgr = manager.manager()

COUNTNUM = 12000
COUNTNUM_L = 400

def get_file_index():
    f = open(config.SOURCEDATA_PATH + config.INDEXFILELIST, 'rb')
    idx = f.read()
    idx = idx.replace('nz2_merged/', '').split('\n')
    return idx

def blockmanage(docid, parsed_data):
    global mgr
    if mgr.state == PENDING:
        block = subindex.subindex(mgr.blocknum, config.DATAPATH)
        mgr.blocknum += 1
        mgr.block.append(block)
        mgr.count = 0
        mgr.state = RUNNING
        print("init new index block", mgr.blocknum - 1)
        termnum = block.indexbuild(docid, parsed_data)
    elif mgr.state == RUNNING:
        block = mgr.block[mgr.blocknum - 1]
        mgr.count += 1
        termnum = block.indexbuild(docid, parsed_data)
        if mgr.count >= COUNTNUM:
            mgr.count = 0
            mgr.state = CHECKING
    else:
        block = mgr.block[mgr.blocknum - 1]
        mgr.count += 1
        termnum = block.indexbuild(docid, parsed_data)
        if mgr.count > COUNTNUM_L:
            size =  block.size()
            mgr.count = 0
            if size > mgr.blocksize:
                print('checking state', block.size())
                block.store()
                mgr.state = PENDING
    return termnum
    

def parse_index_info(data, info):
    global url_dic, docid
    info = info.split('\n')
    offset = 0
    count = 0
    for i in info:
        count += 1
        page_info = i.split(' ')
        if len(page_info) > 3:
            url = page_info[0]
            size = int(page_info[3])
            page = data[offset:offset + size]
            offset += size
            buf = page + page + "1"
            try:
                #ret = parser.parser(url, page, buf, 2 * len(page) + 1, len(page))
                ret = parser.parser(url, page, buf, 2 * len(page) + 1)
            except Exception as e:
                continue
            if ret[0] > 0:
                if url not in url_dic:
                    url_dic[url] = docid
                    termnum = blockmanage(docid, ret[1])
                    doc_dic[docid] = [url, termnum]    # url, num of terms
                    #if docid == 25153:
                    #    print(ret[1])
                    #    print('-----------------')
                    #    print(page)
                    docid += 1


def storedata():
    print("store")
    cPickle.dump(lexicon, gzip.open('lexicon', 'wb'))
    cPickle.dump(doc_dic, gzip.open('doc_dic', 'wb'))
    print('---------------------- done store')

def source_file_pasrse_NZ(path):
    global doc_dic
    print("source_file parser NZ", time.ctime())
    vol = ['vol_0_99/', 'vol_100_199/', 'vol_200_299/', 'vol_300_399/', 'vol_400_499/', 'vol_500_599/', 'vol_600_699/', 'vol_700_799/', 'vol_800_899/', 'vol_900_999/', 
           'vol_1000_1099/', 'vol_1100_1199/', 'vol_1200_1299/', 'vol_1300_1399/', 'vol_1400_1499/', 'vol_1500_1599/', 'vol_1600_1699/', 'vol_1700_1799/', 'vol_1800_1899/', 'vol_1900_1999/', 
           'vol_2000_2099/', 'vol_2100_2199/', 'vol_2200_2299/', 'vol_2300_2399/', 'vol_2400_2499/', 'vol_2500_2599/', 'vol_2600_2699/', 'vol_2700_2799/', 'vol_2800_2899/', 'vol_2900_2999/', 
           'vol_3000_3099/', 'vol_3100_3199/', 'vol_3200_3299/', 'vol_3300_3399/', 'vol_3400_3499/', 'vol_3500_3599/', 'vol_3600_3699/', 'vol_3700_3799/', 'vol_3800_3899/', 'vol_3900_3999/',
           'vol_4000_4099/', 'vol_4100_4199/']
    for i in range(4200):
        num = i / 100
        fpath = path + vol[num] + str(i)

        print(fpath)
        
        try:
            findex = gzip.open(fpath + '_index', 'rb')
            info = findex.read()
            findex.close()
            fdata = gzip.open(fpath + '_data', 'rb')
            data = fdata.read()
            fdata.close()
        except Exception as e:
            print(e)
            continue
        try:
            parse_index_info(data, info)
        except Exception as e:
            print('=================')
            print(e)
            continue
    print("------- done ", time.ctime())
    """-----------close all the index block---------"""
    block = mgr.block[mgr.blocknum - 1]
    print('checking state', block.size())
    block.store()
    mgr.state = PENDING
    manager.mergesort(mgr)

    manager.structrestore(doc_dic, 'doc_dic')
    mgr.__init__()
    #storedata()
    print("------- done ", time.ctime())

def source_file_parse(path, file_index):
    global doc_dic
    print("source_file parser  ", time.ctime())
    for idx in file_index:
        if idx:
        #if idx and int(idx) < 10:
            print(idx)
            try:
                fpath = path + idx
                findex = gzip.open(fpath + '_index', 'rb')
                info = findex.read()
                findex.close()
                try:
                    fdata = gzip.open(fpath + '_data', 'rb')
                    data = fdata.read()
                    fdata.close()
                except Exception as e:
                    print(e)
                    continue
                try:
                    parse_index_info(data, info)
                except Exception as e:
                    print('=================')
                    print(e)
                    continue
            except Exception as e:
                print(e)
                continue
    print("------- done ", time.ctime())
    """-----------close all the index block---------"""
    block = mgr.block[mgr.blocknum - 1]
    print('checking state', block.size())
    block.store()
    mgr.state = PENDING
    manager.mergesort(mgr)

    manager.structrestore(doc_dic, 'doc_dic')
    mgr.__init__()
    #storedata()
    print("------- done ", time.ctime())
    """
    try:
        datainfo()
    except Exception as e:
        print('error', e)
        while 1: pass
    """
    while 1: pass
            
def source_file_pasrse_NZ10(path):
    global doc_dic
    print("source_file parser NZ10", time.ctime())
    vol = ['vol_0_99/', 'vol_100_199/', 'vol_200_299/', 'vol_300_399/', 'vol_400_419/']
    for i in range(420):
        if i < 100: fpath = path + vol[0] + str(i)
        elif i < 200: fpath = path + vol[1] + str(i)
        elif i < 300: fpath = path + vol[2] + str(i)
        elif i < 400: fpath = path + vol[3] + str(i)
        else: fpath = path + vol[4] + str(i)

        print(fpath)

        findex = gzip.open(fpath + '_index', 'rb')
        info = findex.read()
        findex.close()
        fdata = gzip.open(fpath + '_data', 'rb')
        data = fdata.read()
        fdata.close()
        try:
            parse_index_info(data, info)
        except Exception as e:
            print('=================')
            print(e)
            continue
    print("------- done ", time.ctime())
    """-----------close all the index block---------"""
    block = mgr.block[mgr.blocknum - 1]
    print('checking state', block.size())
    block.store()
    mgr.state = PENDING
    manager.mergesort(mgr)

    manager.structrestore(doc_dic, 'doc_dic')
    mgr.__init__()
    #storedata()
    print("------- done ", time.ctime())
    """
    try:
        datainfo()
    except Exception as e:
        print('error', e)
        while 1: pass
    """
    #while 1: pass           

if __name__ == '__main__':
    print("index ...... larry")
    if config.NZ == 1:
        source_file_pasrse_NZ(config.SOURCEDATA_PATH_NZ)
    elif config.NZ10 == 1:  #NZ10
        source_file_pasrse_NZ10(config.SOURCEDATA_PATH_NZ10)
    else:          #NZ2
        file_index = get_file_index()
        source_file_parse(config.SOURCEDATA_PATH, file_index)
