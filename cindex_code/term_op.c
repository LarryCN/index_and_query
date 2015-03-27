#include "term_op.h"
#include "index_op.h"
#include "simple9.h"

static uint chunkbuf[128];
int term_num = 0;

static inline void set_chunk_access_flag(struct tobj* tobj){
    tobj->flag |= (1 << CHUNK_ACCESS);
}

static inline void set_chunk_freq_flag(struct tobj* tobj){
    tobj->flag |= (1 << CHUNK_FREQ);
}

static inline void set_meta_flag(struct tobj* tobj){
    tobj->flag |= (1 << META);
}

static inline void clear_chunk_access_flag(struct tobj* tobj){
    tobj->flag &= ~ (1 << CHUNK_ACCESS);
}

static inline void clear_chunk_freq_flag(struct tobj* tobj){
    tobj->flag &= ~ (1 << CHUNK_FREQ);
}

static inline int is_chunk_access(struct tobj* tobj){
    return tobj->flag & (1 << CHUNK_ACCESS);
}

static inline int is_chunk_freq(struct tobj* tobj){
    return tobj->flag & (1 << CHUNK_FREQ);
}

static inline int is_meta_flag(struct tobj* tobj){
    return tobj->flag & (1 << META);
}

inline static uint strhex_to_i(char *input, int l)
{
    char c;
    int off = 0;
    uint v;
    uint ret = 0;
    
    while(off < l){
        c = input[off];
        if(c < 'a'){
            v = atoi(&c);
        }else if(c == 'a'){
            v = 10;
        }else if(c == 'b'){
            v = 11;
        }else if(c == 'c'){
            v =12;
        }else if(c == 'd'){
            v = 13;
        }else if(c == 'e'){
            v = 14;
        }else if(c == 'f'){
            v = 15;
        }
        ret += (v << ((l - 1 - off) * 4));
        off += 1;
    }

    return ret;
}

static int update_metadata(int start_addr, struct tobj* tobj)
{
    int metadata_l = 0;
    int metasize = 0;
    int i;

    int* metadata = NULL;
    struct tobj *t = tobj;
    struct meta *meta= &t->meta;
   
    //printf("update metadata %d \n", start_addr); 
    metadata_l = get_metadata_l(t->fileindex, start_addr);
    if(is_meta_flag(t)){
        free(meta->doc_list);
    }
    metadata = (int *)malloc(metadata_l * sizeof(int));
    if(metadata == NULL)
        return 1;
    set_meta_flag(t);


    metasize = get_metasize();
    //printf("metasize %d \n", metasize);
    t->chunk_off = metasize + 8;
    metadata_l = metadata_l >> 2;
    meta->doc_list = metadata;
    meta->doc_off = (metadata + metadata_l);
    meta->freq_off = (metadata + metadata_l * 2);
    meta->chunk_addr = (metadata + metadata_l * 3);
    metadata = get_metadata();
    for(i = 0; i < metadata_l; i++){
        meta->doc_list[i] = metadata[(i << 2)];
        meta->doc_off[i] = metadata[(i << 2) + 1];
        meta->freq_off[i] = metadata[(i << 2) + 2];
        meta->chunk_addr[i] = metadata[(i << 2) + 3];
        //printf("%d, %d, %d, %d \n", meta->doc_list[i], meta->doc_off[i], meta->freq_off[i], meta->chunk_addr[i]);
    }
    if(t->cur_block + 1 < t->block_num){
        t->cur_chunk_e = metadata_l;
    }else{
        t->cur_chunk_e = t->chunk_e + 1;
        if(t->cur_chunk_e > metadata_l)
            t->cur_chunk_e = metadata_l;
    }
    
    return 0;
}

struct tobj* term_init(int* info)
{
    int ret = 0; 
    struct tobj *t = NULL;

    t = (struct tobj*)malloc(sizeof(struct tobj));
    if(t == NULL)
        return t;
    t->tindex = term_num;
    term_num += 1;
    t->fileindex = info[0];
    t->chunk_s = info[1];
    t->chunk_e = info[2];
    t->start_addr = info[3];
    t->end_addr = info[4];
    t->doc_num = info[5];
    t->block_num = (info[4] - info[3])/config.c_blocksize;
    t->c_blocksize = config.c_blocksize;
    t->cur_block = 0;
    t->cur_chunk = t->chunk_s;
    t->cur_meta_l = 0;
    t->flag = 0;
    t->maxid = config.maxid;

    file_open(t->fileindex);
    /* update metadata */
    ret = update_metadata(t->start_addr, t);
    if(ret){
        printf("update metadata fail \n");
        file_close(t->fileindex);
        return NULL;
    }
    //printf("term init done %d s %d e %d \n", t->tindex, t->chunk_s, t->chunk_e);

    return t;
} 

static void update_chunkdata_doc(int start_addr, int end_addr, struct tobj *tobj)
{
    char *chunkdata = NULL;

    int doclist_l = 0;
    int off = 0;
    int count = 0;
    int len = end_addr - start_addr;
    int i;
    struct tobj *t = tobj;
    int* c_doclist = t->chunk.doclist;
    int seek_addr = t->start_addr + t->cur_block * t->c_blocksize + t->chunk_off;

    //printf("update chunkdata doc  %d, %d \n", start_addr, end_addr);
    t->cur_chunk_freq_saddr = seek_addr + end_addr;
    //printf("get chunkdata %d\n", seek_addr + start_addr);
    chunkdata = get_chunkdata(t->fileindex, seek_addr + start_addr, len);
    //printf("get chunkdata done, %d\n", len);
    while(off < len){
        chunkbuf[count] = (uint)strhex_to_i((chunkdata + off), 8);
        count += 1;
        off += 8;
    }
    //printf("---- count %d \n", count);
    len = simple9_decode(chunkbuf, c_doclist, count);
    t->cur_chunk_doc_l = len;
    for(i = 1; i < len; i++){
        c_doclist[i] += c_doclist[i - 1];
    }
    
    t->cur_doc = 0;
    set_chunk_access_flag(t);
    clear_chunk_freq_flag(t);
}

static inline void update_chunkdata_freq(int start_addr, int len, struct tobj *tobj)
{
    int off = 0;
    int count = 0;

    struct tobj* t = tobj;
    char *chunkdata = NULL;
    int *c_freq = t->chunk.freq;

    //printf("update chunkdate_freq %d, %d \n", start_addr, len);
    chunkdata = get_chunkdata(t->fileindex, start_addr, len);
    while(off < len){
        chunkbuf[count] = (uint)strhex_to_i((chunkdata + off), 8);
        count += 1;
        off += 8;
    }
    //printf("---- count %d \n", count);
    len = simple9_decode(chunkbuf, c_freq, count);
    set_chunk_freq_flag(t);
}

static void init_chunkdata(struct tobj* tobj)
{
    struct meta* meta = &tobj->meta;
    int cur = tobj->cur_chunk;
    int start = 0;

    //printf("init chunkdata\n");
    if(cur == 0){
        start = 0;
    }else{
        start = meta->chunk_addr[cur - 1];
    }
    update_chunkdata_doc(start, start + meta->doc_off[cur], tobj);
}

static inline int get_chunk_docid(int docid, struct tobj* tobj)
{
    struct tobj *t = tobj;
    int i = 0;
    int l = t->cur_chunk_doc_l;
    int* doclist = t->chunk.doclist;
    //printf("get_chunk docid \n");
    
    for(i = t->cur_doc; i < l; i++){
        if(doclist[i] >= docid){
            t->cur_doc = i;
            break;  
        }
    }
    return doclist[i];
}

static int check_meta_docid(int docid, struct tobj* tobj)
{
    int i = 0;
    struct tobj* t = tobj;
    struct meta* meta = &t->meta;
    int *l = t->meta.doc_list;
    int n = t->cur_chunk_e;

    //printf("check meta docid cur chunk %d end %d\n", t->cur_chunk, n);
    for(i = t->cur_chunk; i < n; i++){
        if(l[i] >= docid){
            if(t->cur_chunk == i){
                if(!is_chunk_access(t)){
                    init_chunkdata(t);
                }
            }else{
                update_chunkdata_doc(meta->chunk_addr[i - 1], meta->chunk_addr[i - 1] + meta->doc_off[i], t);
                t->cur_chunk = i;
            }
            return get_chunk_docid(docid, t);
        }
    }
    return t->maxid;
}

int get_docid(int docid, struct tobj* tobj)
{
    struct tobj* t = tobj;
    int block_num = t->block_num;
    int ret = 0;
    int maxid = t->maxid;
    //printf("get docid\n");

    while((t->cur_block + 1)<= block_num){
        ret = check_meta_docid(docid, t);
        if(ret != maxid)
            return ret;
        t->cur_block += 1;
        if(t->cur_block + 1 > block_num)
            break;
        update_metadata(t->start_addr + t->cur_block * t->c_blocksize, t);
        clear_chunk_access_flag(t);
        t->cur_chunk = 0;
    }
    return maxid;
}

int get_freq(struct tobj* tobj)
{
    struct tobj* t = tobj;
    //printf("get freq\n");
    if(!is_chunk_access(t))
        init_chunkdata(t);
    if(!is_chunk_freq(t))
        update_chunkdata_freq(t->cur_chunk_freq_saddr, t->meta.freq_off[t->cur_chunk], t);
    return t->chunk.freq[t->cur_doc];
}

void term_close(struct tobj* tobj)
{
    file_close(tobj->fileindex);
    free(tobj->meta.doc_list);
    term_num -= 1;
}



