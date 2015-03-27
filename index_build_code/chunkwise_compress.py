# by larry Mar 17th, 2015
import simple9
import config

""" docid compress by increasing diff
    like 51, 59, 69, 80 -> 51, 8, 10, 11
    input docid list
    return transfer list
"""
def docid_compress_by_inc(docid):
    r = [docid[0]]
    for i in xrange(1, len(docid)):
        r.append(docid[i] - docid[i - 1])
    return r
   
""" pos is a list of postions
    here just change the value by inc
"""
def position_compress_by_inc(pos, n):
    for i in reversed(range(1, n)):
       # pos[2 * i] = pos[2 * i] - pos[2 * (i - 1)]
        pos[i] = pos[i] - pos[i - 1]
    return pos

""" term ---> inverted index | block | block | block | ...
    block -->  metadata |doc id| freq | pos | ...                           
    list chunk ->  128 doc ids| 128 freqs | 128 docs` positions | ...  

    metadata : metadata size, last doc id, chunk size
                              last doc id, chunk size
                              ...
"""

class iblock:
    def __init__(self):
        self.metadata = ''         
        self.chunkdata = ''        # encode with simple9
        self.size = 0              # final size
        self.off = 0               # metadata size
        self.chunk_num = 0         # chunk num

    """ pack metadata info
    """
    def metadata_pack(self):
        #s = ''
        #for i in self.metadata:
        #    s += ' ' + str(i)
        #print(len(self.metadata), len(s), len(s) * 1.0 / len(self.metadata))
        #self.metadata = s     # change to encoded data
        l = self.off + 8 + self.size
        self.off = hex(self.off | (1 << 23))
        """ pack 0 until size to 64KB """
        if l > config.C_BLOCKSIZE:
            print('---------------------- ', l, self.off, self.size)
        for i in xrange(config.C_BLOCKSIZE - l):
            self.chunkdata += ' '

class iindex:
    def __init__(self):
        self.block = [iblock()]       # blocks
        self.n = 1                    # block num

    """ seperate inverted index into docic, fre, pos
    """
    def iidex_info_seperate(self, data):
        self.c = [0]
        #docid, fre, pos = [], [], []
        docid, fre, pos, ptype = [], [], [], []
        off, length = 0, len(data)
        count = 0
        pos_c = 0
        while off < length:
            docid.append(data[off])    # doc id
            n = data[off + 1]
            fre.append(n)              # freq
            off += 2
            for i in xrange(2 * n):
                #pos.append(data[off + i])  # postion, type
                if i & 1: ptype.append(data[off + i])  # postion, type
                else: pos.append(data[off + i])
            if n >= 2:
                #pos[-(2 * n):] = position_compress_by_inc(pos[-(2 * n):], n)
                pos[-n:] = position_compress_by_inc(pos[-n:], n)
            off += 2 * n
            #pos_c += 2 * n
            pos_c += n
            self.c.append(pos_c)
        #return docid, fre, pos
        return docid, fre, pos, ptype

    """ index has stored enough data
        deal with the unpack metadata
    """
    def iindex_done(self):
        block = self.block[self.n - 1]
        block.metadata_pack()

    """ store chunck into block
        update metadata info
    """
    def chunk_store(self, last_docid, chunksize, chunkdata, doc_off, fre_off):
        block = self.block[self.n - 1]
        #if block.size + chunksize >= BLOCKSIZE:
        if block.size + chunksize + block.off + 32 + len(str(last_docid)) + len(str(block.size)) + len(str(doc_off)) + len(str(fre_off))>= config.C_BLOCKSIZE:   # 15 is max of last docid + size + _
            block.metadata_pack()    # block full, pack its metadata
            #print(self.n, block.size, len(block.metadata) * 1.0 / 1024, len(block.chunkdata) * 1.0 / 1024, (len(block.metadata) + len(block.chunkdata)) * 1.0 / 1024)
            block = iblock()
            self.block.append(block)
            self.n += 1
        block.chunkdata += chunkdata
        block.size += chunksize
        #block.metadata.append(last_docid)
        #block.metadata.append(block.size)
        block.metadata += ' ' + str(last_docid)
        block.metadata += ' ' + str(doc_off)
        block.metadata += ' ' + str(fre_off)
        block.metadata += ' ' + str(block.size)
        block.off = len(block.metadata)
        if not self.info:
            self.info.append(self.n)
            self.info.append(self.block[self.n - 1].chunk_num)
        block.chunk_num += 1

    """ max 128 per chunk; per chunk <= 128
        input docid, fre, pos list
        return 
    """
    #def chunk_pack(self, docid, fre, pos):
    def chunk_pack(self, docid, fre, pos, ptype):
        off, length = 0, len(docid)
        while off < length:
            if length - off >= config.CHUNKSIZE:
                inc = config.CHUNKSIZE
            else: inc = length - off
            chunksize = config.C_BLOCKSIZE
            while chunksize >= config.C_BLOCKSIZE:
                if inc == 0:
                    print('!!!!!!!!!!!!!!!!!!!!!!', chunksize, docid[off: off + 1], fre[off: off + 1])
                    print(pos[self.c[off]:self.c[off + 1]])
                    print(len(rp), len(rdoc), len(rfre))
                    print(rp)
                    print(rdoc)
                    print(rfre)
                short = docid_compress_by_inc(docid[off: off + inc])           # compress doc id
                #data = short + fre[off: off + inc] + pos[self.c[off]: self.c[off + inc]]       # get encode data
                """
                data = short + fre[off: off + inc] + pos[self.c[off]: self.c[off + inc]] + ptype[self.c[off]: self.c[off + inc]]      # get encode data
                r = simple9.simple9_encode(data, len(data))                    # encode with simple9
                r = [hex(x)[2:] for x in r]                                    
                r = str(r)[1:-1].replace('\'', '').replace(',', '').replace(' ', '')
                chunksize = len(r)
                """
                rdoc = simple9.simple9_encode(short, len(short))                    # encode with simple9
                rdoc = [hex(x)[2:] for x in rdoc]                                    
                rdoc = str(rdoc)[1:-1].replace('\'', '').replace(',', '').replace(' ', '')
                data = fre[off: off + inc]          
                rfre = simple9.simple9_encode(data, len(data))                    # encode with simple9
                rfre = [hex(x)[2:] for x in rfre]                                    
                rfre = str(rfre)[1:-1].replace('\'', '').replace(',', '').replace(' ', '')
                data = pos[self.c[off]: self.c[off + inc]] + ptype[self.c[off]: self.c[off + inc]]
                rp = simple9.simple9_encode(data, len(data))                    # encode with simple9
                rp = [hex(x)[2:] for x in rp]                                    
                rp = str(rp)[1:-1].replace('\'', '').replace(',', '').replace(' ', '')

                r = rdoc + rfre + rp
                chunksize = len(r)
                if chunksize >= config.C_BLOCKSIZE:
                    inc = inc >> 1
                    print('-----', inc)
            self.chunk_store(docid[off + inc - 1], len(r), r, len(rdoc), len(rfre))              # chunk store
            off += inc                                                     # updata off

    """ this is the inferface for outside
        input inverted index, then store by chunk-wise compression  [int, int, ...]  int list
        output store position
    """
    def store(self, data):
        #docid, fre, pos = self.iidex_info_seperate(data)   # seperate docid, fre, pos
        docid, fre, pos, ptype = self.iidex_info_seperate(data)   # seperate docid, fre, pos
        self.info = []
        #ip = self.n
        #info = [p, self.block[p - 1].chunk_num]
        #self.chunk_pack(docid, fre, pos)                   # chunk pack
        self.chunk_pack(docid, fre, pos, ptype)                   # chunk pack
        p = self.n
        self.info.append(p)
        self.info.append(self.block[p - 1].chunk_num - 1)
        return self.info   # start_block_num, start_chunk_num, end_block_num, end_chunk_num

