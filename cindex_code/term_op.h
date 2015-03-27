#ifndef TERM_OP_H__
#define TERM_OP_H__
#include "def.h"

struct meta{
    int *doc_list;
    int *chunk_addr;
    int *doc_off;
    int *freq_off;    
};

struct chunk{
    int doclist[CHUNKSIZE];
    int freq[CHUNKSIZE]; 
};

struct tobj{
    int tindex;
    int fileindex;
    int chunk_s;
    int chunk_e;
    int start_addr;
    int end_addr;
    int doc_num;
    int block_num;

    int cur_block;
    int cur_chunk;
    int cur_chunk_e;
    int cur_meta_l;
    int cur_chunk_freq_saddr;
    int cur_chunk_doc_l;
    int cur_doc;

    int chunk_off;
    int c_blocksize;
    int maxid;

    int flag;

    struct meta meta;
    struct chunk chunk;
};


/* flag */
#define CHUNK_ACCESS    0
#define CHUNK_FREQ      1
#define META            2

extern struct tobj* term_init(int* info);
extern int get_docid(int docid, struct tobj* tobj);
extern int get_freq(struct tobj* tobj);
extern void term_close(struct tobj* tobj);

extern int term_num;

#endif /* term_op.h */
