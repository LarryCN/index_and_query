SIMPLE9 = 1            # 1 use simple9 encode
CHUNKWISE = 1          # 1 use chunkwise compression, enable chunk wise compression, must also enable simple9
CHUNKSIZE = 128
C_BLOCKSIZE = 64 * 1024 # chunkwise block size
#C_BLOCKSIZE = 128 * 1024 # chunkwise block size
INDEXSIZE = 64 * 1024 * 1024   # inverted index block size
BLOCKSIZE = 200 * 1024 * 1024  # tempory block size  manager use
#INDEXSIZE = 4 * 1024 * 1024   # inverted index block size
#BLOCKSIZE = 10 * 1024 * 1024  # tempory block size  manager use
LEXICON = 'lexicon'
DOCDIC = 'doc_dic'
SOURCEDATA_PATH = '/Users/larry/Code/wsn/index/sourcedata/nz2_merged/'  #nz2 source
INDEXFILELIST = 'indexfile_list.txt'
SOURCEDATA_PATH_NZ10 = "/Users/larry/Courses/web search engine/hw2/data/4c/tux-4/polybot/gzipped_sorted_nz/" #nz10


#nz 
DATAPATH = "/Users/larry/Code/wsn/index/test/block/"  # store lexicon doc_dic temporary block
INVERTEDPATH = "/Users/larry/Code/wsn/index/test/block/inverted_index_"

"""
#nz2
DATAPATH = "/Users/larry/Code/wsn/index/test/block/nz10/"  # store lexicon doc_dic temporary block
INVERTEDPATH = "/Users/larry/Code/wsn/index/test/block/nz10/inverted_index_"
"""

"""
# nz10
DATAPATH = "/Users/larry/Code/wsn/index/test/block/nz10_this_is_real/"  # store lexicon doc_dic temporary block
INVERTEDPATH = "/Users/larry/Code/wsn/index/test/block/nz10_this_is_real/inverted_index_"
"""
NZ10 = 0   # 1 run nz10 0 run nz2
TMEP_COMPRESS = 0 # 1, temporary block compress with simple9 
TOP_NUM = 10      # query return result

SOURCEDATA_PATH_NZ = '/Users/larry/Courses/web search engine/nz/NZ Total/data/'
NZ = 0    # 1 run nz data if this is 1 nz10 and nz2 would run

CACHE_BLOCK = C_BLOCKSIZE
CACHE_SIZE = 128 * 1024 * 1024
#CACHE_SIZE = 1024 * 1024
#INDEX_NUM = 37 # nz10
INDEX_NUM = 238 #nz
#INDEX_NUM = 6 #nz2

CINDEX = 1


