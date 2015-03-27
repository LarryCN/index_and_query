Python 2.7.5                        |
inverted index version 1.0 by larry |
___________________________________ |

About this program, it has two part:
One is to build final index, it includes some files in the hw2(with some modifidation), and some additonal files, as we need to 
compress index with simple9 or chunkwise: 
chunkwise_compress.py  manager.py  simple9.py  varbyte.py  config.py  main.py  subindex.py parsermodule.so

The other is to init index, and could be used for querying:
simple9.py  config.py  index_op.py  index_if.py  term_op.py  daat.py  bm25.py  lru.py  test_index.py
For querying also in include some c module to improve efficiency like cSimple9module.so
But for daat we might choose to use cindex module: cindexmodule.so
To make up cindexmodule.so, we have:
index_op.c  index_if.c  term_op.c  hash.c  lru.c  simple9.c  bm25.c  cindexmodule.c
index_op.h  index_if.h  term_op.h  hash.h  lru.h  simple9.h  bm25.h  def.h 

________________________________________
How to run it?
First we need to config config.py 

SIMPLE9 = 1            # 1 use simple9 encode should be 1
CHUNKWISE = 1          # 1 use chunkwise compression, enable chunk wise compression, must also enable simple9 should be 1
CHUNKSIZE = 128        # each chunk max diff docids
C_BLOCKSIZE = 64 * 1024        # chunkwise block size  here we use 64KB
INDEXSIZE = 64 * 1024 * 1024   # inverted index block size
BLOCKSIZE = 200 * 1024 * 1024  # tempory block size  manager use
LEXICON = 'lexicon'
DOCDIC = 'doc_dic'
SOURCEDATA_PATH = '/Users/larry/Code/wsn/index/sourcedata/nz2_merged/'  #nz2 source
INDEXFILELIST = 'indexfile_list.txt'
SOURCEDATA_PATH_NZ10 = "/Users/larry/Courses/web search engine/hw2/data/4c/tux-4/polybot/gzipped_sorted_nz/" #nz10
#nz 
DATAPATH = "/Users/larry/Code/wsn/index/test/block/"  # store lexicon doc_dic temporary block
INVERTEDPATH = "/Users/larry/Code/wsn/index/test/block/inverted_index_"
NZ10 = 0                                              # 1 run nz10 0 run nz2
TMEP_COMPRESS = 0                                     # 1, temporary block compress with simple9 
TOP_NUM = 10                                          # query return result
SOURCEDATA_PATH_NZ = '/Users/larry/Courses/web search engine/nz/NZ Total/data/'
NZ = 0                                                # 1 run nz data if this is 1 nz10 and nz2 would run
CACHE_BLOCK = C_BLOCKSIZE                             # cache min unit size, should be the same as the inverted index block size
CACHE_SIZE = 128 * 1024 * 1024                        # totally cache size
#INDEX_NUM = 37 # nz10                                # the num of index files 
INDEX_NUM = 238 #nz
#INDEX_NUM = 6 #nz2
CINDEX = 1                                            # 1 means we use cindexmodule.so

We should keep most of the parameters as the same. DATAPATH and INVERTEDPATH should be set depend on the sourcedata path.
If we do not use nz, we should also change the INDEX_NUM depend on the reality index file number.
If we use CINDEX, we might also config the def.h and recompile cindexmodule.so:

#define FETCHSIZE 2 * 1024 * 1024          // we have tested this fetch function, as the code actually does not run paralelly, we do not use fetch
#define CHUNKSIZE 128                      // should the same with config.py
#define INDEX_NUM   238                    // change only if the max index files numbers bigger than this
#define FILEPATH_LEN  256                  
//#define FILEPATH "/Users/larry/Code/wsn/index/test/block/nz10_this_is_real/inverted_index_"  // file path should be the same as config.INVERTEDPATH
#define FILEPATH "/Users/larry/Code/wsn/index/test/block/inverted_index_"
//#define FILEPATH "/Users/larry/Code/wsn/index/test/block/nz10/inverted_index_"

After config def.h, we could recompile:
gcc -c -fpic -I/usr/include/python2.7/ bm25.c index_if.c index_op.c term_op.c simple9.c hash.c lru.c cindexmodule.c
gcc -shared -lpython bm25.o index_if.o index_op.o term_op.o simple9.o hash.o lru.o cindexmodule.o -o cindexmodule.so
Then we get a new cindexmodule.so

To run query, we could enter(in code file path in the terminal): python daat.py    
After about 1min init.... some log like:
larry------
index init..............
('doc avg ', 587.3272379092365)
init config 
 LRU init cache size 134217728, block size 65536 
mbuf 5990035456, point 140602540818432, buf 140602540818432 
 LRU init done max cache block 2048 
index init done
('init done', 64.44370794296265)
Then would appear: "Please enter here(return to query): "
then could enter the context to query(here max 128 diff terms, and we filter out terms whose length bigger than 64 and 'nbsp')
Something like:
Please enter here(return to query): computer science
query computer science
results: 
URL science.moria.co.nz/article2.htmlbm25 value: 5.16194338069
URL www2.vuw.ac.nz/international/planning/science/computer_science.htmlbm25 value: 5.12602653468
URL www.otago.ac.nz/subjects/comp.htmlbm25 value: 5.1251756129
URL www.cs.auckland.ac.nz/~alan/informat/ugsections.htmlbm25 value: 5.0986130938
URL www.mcs.vuw.ac.nz/comp/publications/admin-of-trs/mailing-listbm25 value: 5.09030758598
URL www.cs.waikato.ac.nz/csanz/bm25 value: 5.08727007765
URL www.kiwicareers.govt.nz/lists/courses/subject/s10e01.htmbm25 value: 5.08087046706
URL www.kiwicareers.co.nz/lists/courses/subject/s10e01.htmbm25 value: 5.08087046706
URL www.cosc.canterbury.ac.nz/people/bm25 value: 5.0641738082
URL www.cosc.canterbury.ac.nz/people/index.htmlbm25 value: 5.0636133227

Time cost: 0.0716619491577s total 49720 query results

we could show out top 10 results and bm25 values, also total runtime and total query results.
repeatly


To build index, set config.py parameters, then run python main.py
_______________________________________
How it works:
About the first part, build index, almost the same as hw2.
Read source data -> build subindex -> mergesort -> build final index -> store data
Here we do some change:
1. In hw2 the type of postings info use 'H', 'I'... now we change it to number like 1, 2, .... in order to save space and used for compression
2. We add simple9 compression to final index, but we not use it to the temporary block(however, I have added to code to compress and decompress
for the temporary block, if you wanna try, could change config.TEMP_COMPRESS to 1), because the temporary postings usually contian less data for
one term, so the compression ratio is low(hardly notice it changed too much), so in order to save time, here we do not use
3. We add chunk wise compression. One inverted index block -> blocks(128KB) -> metadata + chunkdata -> chunkdata(d d d.. f f f ..p p p.. t t t..)
4. We change the lexicon data struct as we need to record more info to support chunk.  term: end_chunk| start_chunk|fileindex, start_block_addr, 
end_block_addr, doc_num

About the second part, init index, then could query for top urls.
init index -> query -> daat -> parser chunkdata -> bm25 -> results
What we do here:
1. init index, just load lexicon, doc_dic, to init maxid, some bm25 parameters
2. user input query, it`s a list of terms, here we use DAAT to get conjuction pages
3. in index_if we have common lib interfaces like mentioned in the slides, openlist, closelist, nextGEQ, getFreq, DAAT could use these interfaces
4. about how to realize the above interfaces, main code in the term_op.py, we first get first metadata, if necessery to load particular chunk,
chunk has doc chunk, freq chunk and postion and type chunks, we first only load doc chunk, until we need freq(ft) we load freq chunk. In this way
we could skip some chunks and same decompression time. In the term_op and index_op we use some current infomation and flag to avoid duplicated operations
5. bm25 is computed the same as it descripted excepted to compute log val, so we multiply all the values


------
Running time:
build index

nz10: temporary inverted index block roughly less than 100MB (0~35)
      final inverted index block 24MB (0~37)  roughly 900MB
      lexicon diff: 615069    size 49MB
      doc_dic : 295689        size 24MB
      start time: 14:44:18 2015
      end time: 14:56:07 2015   
      total time = 11 mins 49s = 709s 
('source_file parser NZ10', 'Fri Mar 20 15:06:25 2015')
after parser('------- done ', 'Fri Mar 20 15:17:48 2015')  temporary files (0 ~ 35)               --- 11 min 23s
('write ', '/Users/larry/Code/wsn/index/test/block/lexicon', 'Fri Mar 20 15:44:24 2015')          --- 26 min 36s
Fri Mar 20 15:44:29 2015
('write ', '/Users/larry/Code/wsn/index/test/block/doc_dic', 'Fri Mar 20 15:44:30 2015')
Fri Mar 20 15:44:31 2015
('------- done ', 'Fri Mar 20 15:44:33 2015')                                                     --- 11s

nz  : temporary inverted index block roughly less than 120MB (0~164)
      final inverted index block 26MB (0~237)  roughly 6.04GB  (however, some files are bigger than 64MB I think it`s becuase the compression.)
      lexicon diff: 2922500     size 222MB
      doc_dic : 2472073         size 222MB
      start time: 00:48:07 2015
      end time: 05:17:28 2015   
      total time = 4 h 29 mins 21s = 16161s
('source_file parser NZ', 'Tue Mar 24 00:48:07 2015')
('------- done ', 'Tue Mar 24 02:13:13 2015')                                                     --- 85 min 06s
('chunk wise write ', '/Users/larry/Code/wsn/index/test/block/inverted_index_237')
('write ', '/Users/larry/Code/wsn/index/test/block/lexicon', 'Tue Mar 24 05:16:35 2015')          --- 183min 22s
Tue Mar 24 05:16:53 2015
('write ', '/Users/larry/Code/wsn/index/test/block/doc_dic', 'Tue Mar 24 05:16:56 2015')
Tue Mar 24 05:17:17 2015
('------- done ', 'Tue Mar 24 05:17:28 2015')                                                     --- 53s

_________________________________________
files
_________________________________________
---------index build part ---------------
most are the same as HW2

main.py
Add nz files build choice.

chunkwise_compress.py  
This is the file to support chunkwise compression. The whole ideal is like following:

term ---> inverted index | block | block | block | ...
block -->  metadata |doc id| freq | pos | ...                           
list chunk ->  128 doc ids| 128 freqs | 128 docs` positions | 128 types|

metadata : metadata size, last doc id, chunk addr, doc_chunk_off, fre_chunk_off
                          last doc id, chunk addr, doc_chunk_off, fre_chunk_off
                              ...
for each chunk we have max 128 postings, and we seperate docid, fre, positions and types, as well as get diff for docid and positions.
Like, docid: 1223, 1227, 1239.... --> docid: 1223, 4, 12, ....  the same is for position
To do this is to improve simple9 compression ratio.
For metadata, we keep string, as we find both vartype and simple9 do not have much effect, we in order to save decompress time, here we keep string
And for chunk data we use simple9. 
We also add two record information in the metadata, doc_chunk_off, fre_chunk_off, it is becuase, most time we first need to get docid, then we only
extract doc chunk, we only extract fre chunk when we need to get freq.
About metadata size we use |(1 << 23)|metadata size|, so the chunk addr start with off: 8 + metadatasize

As each block is 64KB, we check the chunk size before we put them in the block. if 128 postings bigger then 64KB, we might try 64 postings, then 32, 16, iterately.
For each block, if its size does not get into 64KB, we pack " " in the tail until it gets into 64KB.

manager.py  
Add simple9 and chunkwise compress interface.

simple9.py  
Have simple9 compress and decompress code, detials algorithms in the file.
For simple9 the smaller the data, the better compression ratio we would get.
For simple9 + chunkwise we roughly have 1:3 compression ratio.

varbyte.py  
var-byte compression and decompression code, it`s only used to test, but the result is 
not good, consider time and compression ratio, here we do not use it.

config.py   
To get *.py config variables in the file to convience config

subindex.py
filt words, which length is bigger than 64, and word 'nbsp' 

parsermodule.so 
no change


--------- cindexmolude.so ---------------
index_op.c  
This is the file to handle cindexmodule init and data transfer.
First it inits LRU, BM25, filemanager, and some config information from the up code.
About filemanager, we use a filenode struct to record whether or not the file has been opened, 
and for each term object we count for 1, only close file when its count reduce to 0.
In this way we could save the multi times in open and close files.

get_metadata_l and get_chunkdata are two mainly operations to deal with data transfer to file and term operations
Here we use cache, and we also have the version do not use cahce, the name is get_metadata_bak and get_chunkdata_bak.


index_if.c  
This is the public interface, openlist, closelist, nextGEQ, getFreq 

term_op.c  
This is the file the handle term operation(open, close, get docid, get freq) and chunkwise decompression
The main idea is:
For each term_init -> update_metadata
when oper get docid, we check whecher or not update_metadata ->(not) update metadata
                                               |        |--->(yes) check metadata docid
                                               |->(if metadata no docid) change to next block or return maxdocid

for check metadata docid we first check docid and last docid list, and this could help us the skip decompress chunk it the docid does not in the chunk
after find the last docid >= finding docid, we check whether or not chunkdata has been updated ->(no)  init chunkdata or update chunkdata
                                                                                    |----------->(yes) check chunk docid

For get frequency, when we need to get frequency we get the freq chunk and get the reuslts. This could save the time to decompress useless frequency chunk.
As each chunk part compressed by simple9, so we use simple9 decompress function to extract data.



hash.c  
Hash here is only adding to support cache LRU, as in the LRU we need a dictionary to look up for keys.
And the key of hash we use MOD number, in the hash.h, we could change the define MODNUM if necessary.
The whole idea of the hash is like:
   modnum                 lnode
  -------
    0  pointer  ->  <--|pre|key|addr|next|-> <- .... -> NULL
  -------
    1  pointer
  -------
   ...
  -------


lru.c  
Here we use the easiest cache LRU, as we do not have much tiem to fullfil cache.
For each key, we store like : |fileindex << 20| && |block_start_addr >> 16|

memory buf(total cache size)    LRU(hash)                    dnode  head                    tail
 ----------------               (key) -> bufaddr ->dnode             |                       |
 addr                           (key) -> bufaddr ->dnode            node ->  node -> ...  <- node
 ----------------               ....                                     <-       <-
 addr + blocksize
 ----------------
 addr + 2blocksize
 ----------------
     ....
 ----------------

We use key to get buf addr, for each key we also use a doubly list node to recode ad a used infomation, if hit
or new input, we put its dnode to the head of the doubly list, every time we need to delete a key(as the key has
reached to the max size of cache), we use tail to find the block has the longest time without using.

Adding a cache , we in fact only transfer an address pointer to the function get the cache context, in this way it
saves time, and we also save the time of file seek operations. so after adding cache, we could improve greatly in 
the docid and freq has a high desity.
For the world "the" in NZ, totally 206w query results, without cache, we need about 2s to get results
However after adding cache, we only need 0.5s. 
And for some combine terms, we only need about half of the original time.

About fetch, here we test a cache fetch function, in the file index_op.c, cache_fetch
But we could not see any imporvement, and might cost more time, that is because fetch and 
other operation are not running parallely, so in fact it saves no other operation. So, 
it has no effects. As a result, here we do not use fetch, but we could erease the '//' in index_op.c to use fetch.



simple9.c  
This is the same as simple9.py, but here we only add simple9 decompress funtion.


bm25.c  
This file to fullfil the function to calculate BM25.
BM25(q, d) = sum(log10((N - ft + 0.5)/(ft + 0.5) * (k1 + 1)fdt / (K + fdt)))
for t in q
K = k1 * ((1 - b) + b * |d| / |d|avg)
N: total number documents    ft: number of documents contain term t
fdt: frequency of term t in document t          |d|: len d
k1 = 1.2   b = 0.75

And for K, we could short for K = Ka + Kb * dlen, then could save some computer time
then Ka = k1 * (1 - b), Kb = k1 * b / d_avg
The same we could previously get vk1 = 1 + k1


cindexmodule.c
This is the cindex module interface to the python code.
It has 3 functions init, openlist, and subdaat
For init, it transfers some parameters from python code, and to pass the index_op.config_init.
For openlist, is a interface to communication with openlist in the index_if.py, the index_openlist pass term, and this underlayer interface pass some
necessay infomation.
For subdaat, it is a c interface to realize most parts of daat
DAAT is that:
We regard a query like a list of terms, and order the terms by their ft.
we use docid = next(t1, docid)   t1 as term1`s lp
Then check whether or not other terms has this docid--> get maxdocid of others terms for finding docid

if not back to docid = next(t1, docid) and this time docid = maxdocid
if yes we get the fdt of each documents and computer bm25

As we only need to get top k results, we use a k array to store top k results, and a min_bm25_value, only next bm25 value > min_bm25_value, we update k array
We could use priority queue here, but consider we only need top10 or top20 and array use save together in L1 cache, check the minvalue is very fast, and if we 
use priority queue, we will waste time to keep data structure, so here it`s no use to operation priority queue.   


--------- query python files ---------------
most are the same functional as c code, so here we do not write details.And we do not guarantee pure python code running correctly.........only guarantee correctly with cindex

index_op.py
here we load lexicon and doc_dic, by cPickle load.
And for chunkwise, we change lexicon a little: term: |chunknum end|chunknum start|file index|, block_start_addr, block_end_addr, ft

daat.py
here is the interface to use cindex_subdaat, and have a lexicon test, to test all the lexicon terms..

