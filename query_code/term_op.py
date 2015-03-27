# by larry Mar 19th, 2015
import index_op
import config
import simple9
from cSimple9 import decode as cdecode

class termobj:
    """ when init new termobj should try
        as there might be no such term in the lexicon
    """
    def __init__(self, term):
        info = index_op.get_term_info(term)

        self.name = term
        self.fileindex = info[0]    # index block num
        self.chunk_s = info[1]      # start chunk num related to the first block
        self.chunk_e = info[2]      # end chunk num related to the last block
        self.start_addr = info[3]   # file`s start address   start block
        self.end_addr = info[4]     # file`s end address     end block
        self.doc_num = info[5]      # the number of documents include term
        self.block_num = (info[4] - info[3]) / config.C_BLOCKSIZE # cross number of blocks
        self.cur_block = 0            # current access block
        self.cur_chunk = self.chunk_s # current access chunk
        self.cur_meta_l = 0           # current metadata list length (doc id, address)

        index_op.file_open(self.fileindex, self.name) # register file 
        self.update_metadata(self.start_addr) # get metadata
        
        self.chunk_access_flag = 0    # 0 means not update chunkdata doc
        self.chunk_freq_flag = 0      # 0 means not update freq chunkdata

    """ update current point to term`s postings metadata
    """
    def update_metadata(self, start_addr):
        #print('update metadata', start_addr)
        metasize, metadata = index_op.get_metadata(self.fileindex, start_addr)
        self.chunkoff = metasize + 8
        self.meta_doc_list = []
        self.meta_chunk_addr = []
        self.meta_doc_off = []
        self.meta_freq_off = []
        for i in xrange(len(metadata) >> 2):
            self.meta_chunk_addr.append(int(metadata[i * 4 + 3]))
            self.meta_doc_off.append(int(metadata[i * 4 + 1]))
            self.meta_freq_off.append(int(metadata[i * 4 + 2]))
            self.meta_doc_list.append(int(metadata[i * 4]))
        """check whether or not cross block, set metadata end chunk"""
        if self.cur_block + 1 < self.block_num: self.cur_chunk_e = len(self.meta_doc_list)
        else: 
            self.cur_chunk_e = self.chunk_e + 1
            if self.cur_chunk_e > len(self.meta_doc_list):
                self.cur_chunk_e = len(self.meta_doc_list)
    
    """ start_addr should be metadata`s chunk start address
        end_addr ..
    """
    def update_chunkdata_doc(self, start_addr, end_addr, lastid):
        #print('update chunkdata', start_addr, end_addr, lastid)
        seek_addr = self.start_addr + self.cur_block * config.C_BLOCKSIZE + self.chunkoff
        self.cur_chunk_freq_saddr = seek_addr + end_addr
        chunkdata = index_op.get_chunkdata(self.fileindex, seek_addr + start_addr, seek_addr + end_addr)
        #chunkdata = simple9.simple9_decode_strhex(chunkdata)
        a = []
        l = len(chunkdata)
        off = 0
        while off < l:
            a.append(int(chunkdata[off:off + 8], 16))
            off += 8
        chunkdata = cdecode(a)
        """ chunk doc list """
        d = [chunkdata[0]]
        if chunkdata[0] != lastid:
            for i in xrange(1, len(chunkdata)):
                docid = d[-1] + chunkdata[i]   # as the first store docid , the following stored diff
                d.append(docid)
                if docid == lastid:
                    break
        self.c_doclist = d
        self.cur_chunk_doc_l = len(d)
        """
        l = len(self.c_doclist)
        self.c_freq = chunkdata[l: 2 * l]
        self.c_pos = []
        off = 2 * l
        self.cur_chunk_l = l    # chunk doc nums should be CHUNKSIZE
        for i in self.c_freq:
            self.c_pos.append(chunkdata[off: off + i * 2])
            off += i * 2
        """
        self.cur_doc = 0        # current access docoment
        self.chunk_access_flag = 1 # have chunk data
        self.chunk_freq_flag = 0
    
    def update_chunkdata_freq(self, start_addr, end_addr):
        chunkdata = index_op.get_chunkdata(self.fileindex, start_addr, start_addr + end_addr)
        """ chunk freq list """
        a = []
        l = len(chunkdata)
        off = 0
        while off < l:
            a.append(int(chunkdata[off:off + 8], 16))
            off += 8
        #self.c_freq = simple9.simple9_decode_strhex(chunkdata)
        self.c_freq = cdecode(a)
        self.chunk_freq_flag = 1 # have chunk freq data
    
    def init_chunkdata(self):
        #print('init chunkdata')
        cur = self.cur_chunk
        if cur ==  0: start = 0
        else: start = self.meta_chunk_addr[cur - 1]
        self.update_chunkdata_doc(start, start + self.meta_doc_off[cur], self.meta_doc_list[cur])

    """ docid in chunk
    """
    def get_chunk_docid(self, t_docid):
        for i in xrange(self.cur_doc, self.cur_chunk_doc_l):
            if self.c_doclist[i] >= t_docid:
                self.cur_doc = i
                return self.c_doclist[i]
   
    """ check docid whether or in cur metadata range
    """
    def check_meta_docid(self, t_docid):
        #print('check meta docid')
        l = self.meta_doc_list
        for i in xrange(self.cur_chunk, self.cur_chunk_e):
            if l[i] >= t_docid:
                if self.cur_chunk == i: 
                    if not self.chunk_access_flag:   # in case not init chunkdata
                        self.init_chunkdata()   
                else:                                # can not be 0
                    #self.update_chunkdata_doc(self.meta_chunk_addr[i - 1], self.meta_chunk_addr[i], self.meta_doc_list[i])
                    self.update_chunkdata_doc(self.meta_chunk_addr[i - 1], self.meta_chunk_addr[i - 1] + self.meta_doc_off[i], l[i])
                    self.cur_chunk = i
                return self.get_chunk_docid(t_docid)
        return index_op.maxid

    """ t_docid, threshold
        first check metadata
        then chunk
    """
    def get_docid(self, t_docid):
        while self.cur_block + 1 <= self.block_num:
            ret = self.check_meta_docid(t_docid)
            if ret != index_op.maxid:
                return ret
            self.cur_block += 1 # cross block =.=!
            if self.cur_block + 1 > self.block_num:
                break
            self.update_metadata(self.start_addr + self.cur_block * config.C_BLOCKSIZE) # get metadata
            self.chunk_access_flag = 0 # chunkdata out of date
            self.cur_chunk = 0         # since next metadata, update cur_chunk = 0
        return index_op.maxid
            
    """ return current docid freq
    """
    def get_freq(self):
        if not self.chunk_access_flag:
            self.init_chunkdata()
        if not self.chunk_freq_flag:
            self.update_chunkdata_freq(self.cur_chunk_freq_saddr, self.meta_freq_off[self.cur_chunk])
        return self.c_freq[self.cur_doc]

    def close(self):
        index_op.file_close(self.fileindex, self.name)

