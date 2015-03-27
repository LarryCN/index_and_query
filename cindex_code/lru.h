#ifndef LRU_H__
#define LRU_H__

#include "hash.h"

struct LRU{
    int max;
    int count;
    int blocksize;
    int cachesize;
    char** buf;
    struct dnode head;
    struct dnode tail;
    struct hash* hash;
};

extern void lru_init(struct LRU *lru, int cachesize, int blocksize);
extern char* lru_get(struct LRU *lru, int k);
extern char* lru_set(struct LRU *lru, int k); 

#endif /* lru.h */
