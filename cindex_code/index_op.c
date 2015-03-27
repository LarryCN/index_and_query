#include "index_op.h"
#include "def.h"
#include "bm25.h"
#include "lru.h"

volatile struct config config;
static char metadata_cbuf[64 * 1024];// 128 * 1024
static int metadata_ibuf[16 * 1024];
static int metasize = 0;
static struct LRU lru;

struct filenode{
    int flag;
    int count;
    int filesize;
    FILE *fp;
};

static struct filenode filemanager[INDEX_NUM];

static void filemanager_init(int *indexsize)
{
    int i;

    for(i = 0; i < config.index_num; i++){
        filemanager[i].flag = 0;
        filemanager[i].count = 0;
        filemanager[i].filesize = indexsize[i];
        filemanager[i].fp = NULL;
    }
}

void file_open(int fileindex)
{
    FILE *fp = NULL;
    char path[FILEPATH_LEN];
    char sindex[32];
    struct filenode *node = &filemanager[fileindex];
    
    if(node->flag){
        node->count += 1;
    }else{
        sprintf(sindex, "%d", fileindex);
        strcpy(path, FILEPATH);
        strcat(path, sindex);
        fp = fopen(path,"rb");
        if(fp == NULL)
            return ;
        node->flag = 1;
        node->count += 1;
        node->fp = fp;
    }
}

static FILE *get_f(int fileindex)
{ 
    struct filenode *node = &filemanager[fileindex];

    if(node->flag){
        return node->fp;
    }
    return NULL;
}

void file_close(int fileindex)
{
    struct filenode *node = &filemanager[fileindex];

    if(node->flag){
        node->count -= 1;
        if(node->count == 0){
            fclose(node->fp);
            node->fp = NULL;
            node->flag = 0;
        }
    }
}

/*
 * TO DO init config
 */
void init_config(int *data, double d_avg, int *indexsize)
{
    printf("init config \n");
    config.chunksize = data[0];
    config.c_blocksize = data[1];
    config.top_k = data[2];
    config.cache_block = data[3];
    config.index_num = data[4];
    config.cache_size = data[5];
    config.maxid = data[6];
    config.fetch_n = FETCHSIZE / config.c_blocksize;

    bm25_init(data[7], d_avg);

    filemanager_init(indexsize);
    lru_init(&lru, config.cache_size, config.c_blocksize);
}

static int parse_metadata(char *input, int *output, int len)
{
    int off = 0;
    int flag = 0;
    int count = 0;
    int c = 0;
    char data[32];
    char* in = input;
    int* out = output;

    while(off < len){
        if(in[off] == ' '){
            if(flag == 1){
                c += 1;
                data[c] = '\0';
                out[count] = atoi(data);
                count += 1;  
                flag = 0;
            }
        }else{       // get data
            if(flag == 1){
                c += 1;
                data[c] = in[off];
            }else{
                data[0] = in[off];
                c = 0;
                flag = 1;
            }
        }
        off += 1;
    }
    if(flag == 1){
        c += 1;
        data[c] = '\0';
        out[count] = atoi(data);
        count += 1;
    }
    return count;
}

inline static ulong strhex_to_i(char *input, int l)
{
    char c;
    int off = 0;
    uint v;
    ulong ret = 0;
    
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

int *get_metadata(void)
{
    return metadata_ibuf;
}

int get_metasize(void)
{
    return metasize;
}

static void cache_fetch(FILE *fp, int fileindex, int start)
{
    int start_key = (fileindex << 16) | (start >> 16);
    int end = (fileindex << 16) | (filemanager[fileindex].filesize);
    int i, n = config.fetch_n;
    int size = config.c_blocksize;
    char *addr = NULL;
    struct LRU *l = &lru;

    for(i = 0; i < n; i ++){
        addr = lru_get(l, start_key);
        if(addr == NULL){
            addr = lru_set(l, start_key);
            fread(addr, size, 1, fp);
        }else{
            fseek(fp, size, SEEK_CUR);
        }
        start_key += 1;
        if(start_key >= end)
            break;
    }
}

char *get_cache_data(int fileindex, int start)
{
    FILE *fp = NULL;
    int key = (fileindex << 16) | (start >> 16);
    struct LRU *l = &lru;
    char *addr = lru_get(l, key);

    if(addr != NULL){
        //printf("hit %d %x %d, %lu\n", fileindex, start, key, (ulong)addr);
        return addr;
    }
    fp = get_f(fileindex);
    fseek(fp, start, SEEK_SET);
    addr = lru_set(l, key);
    fread(addr, config.c_blocksize, 1, fp);
    //cache_fetch(fp, fileindex, start + config.c_blocksize);
    //printf("mis %d %x %d, %lu\n", fileindex, start, key, (ulong)addr);
    return addr;
}

int get_metadata_l(int fileindex, int start)
{
    int metadata_l;
    char *cache = get_cache_data(fileindex, start);
    
    metasize = (int)strhex_to_i(cache + 3, 5);
     
    metadata_l = parse_metadata((cache + 9), metadata_ibuf, metasize);
    //printf("cache %lu  %.*s  metasize %d metadata_l %d \n", (ulong)cache, 8, cache, metasize, metadata_l);
    //printf("%.*s \n", config.c_blocksize, cache);

    return metadata_l;
}

char* get_chunkdata(int fileindex, int start, int len)
{
    char *cache = get_cache_data(fileindex, start);
    
    //printf("cache %lu  start %d \n", (ulong)cache, start);
    start = start & (config.c_blocksize - 1); 
    //printf("cache %lu  start %d \n", (ulong)cache, start);

    return (cache + start);
}

int get_metadata_l_bak(int fileindex, int start)
{
    FILE *fp = get_f(fileindex);
    int i;
    int metadata_l;
    char smetasize[8];

    fseek(fp, start + 2, SEEK_SET);
    fread(smetasize, 6, 1, fp);
    metasize = (int)strhex_to_i(smetasize + 1, 5);
    fread(metadata_cbuf, metasize, 1, fp);
    
    metadata_l = parse_metadata(metadata_cbuf, metadata_ibuf, metasize);

    return metadata_l;
}

char* get_chunkdata_bak(int fileindex, int start, int len)
{
    FILE *fp = get_f(fileindex);

    fseek(fp, start, SEEK_SET);
    fread(metadata_cbuf, len, 1, fp);

    return metadata_cbuf;
}

