#ifndef INDEX_OP_H__
#define INDEX_OP_H__
struct config{
    int chunksize;
    int c_blocksize;
    int top_k;
    int cache_block;
    int index_num;
    int cache_size;
    int maxid;
    int fetch_n;
};

extern volatile struct config config;
extern int *get_metadata(void);
extern int get_metasize(void);
extern int get_metadata_l(int fileindex, int start);
extern char *get_chunkdata(int fileindex, int start, int len);
extern void init_config(int *data, double d_avg, int *indexsize);
extern void file_open(int fileindex);
extern void file_close(int fileindex);

#endif /* index_op.h */

