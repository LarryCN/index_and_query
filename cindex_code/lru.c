#include "lru.h"
#include "def.h"
#include "hash.h"

static struct hash hash;

void lru_init(struct LRU *lru, int cachesize, int blocksize)
{
    struct LRU *l = lru;
    char *mbuf = NULL;
    char **point = NULL;
    int i;

    printf(" LRU init cache size %d, block size %d \n", cachesize, blocksize);
    l->blocksize = blocksize;
    l->cachesize = cachesize;
    l->count = 0;
    l->max = cachesize / blocksize;
    l->head.key = -1;
    l->head.pre = NULL;
    l->head.next = &l->tail;
    l->tail.key = -2;
    l->tail.pre = &l->head;
    l->tail.next = NULL;
    
    mbuf = (char *)malloc(sizeof(char) * cachesize);
    if(mbuf == NULL){
        printf("no memory to allocate cache\n");
    }
    point = (char **)malloc(sizeof(char *) * l->max);
    for(i = 0; i < l->max; i++){
        point[i] = (mbuf + blocksize * i);
        //printf("--- %lu \n", (ulong)point[i]);
    }
    l->buf = point;
    
    l->hash = &hash;
    hash_init(l->hash);    
    printf("mbuf %lu, point %lu, buf %lu \n", (ulong)mbuf, (ulong)point, (ulong)l->buf);
    printf(" LRU init done max cache block %d \n", l->max);
}

char* lru_get(struct LRU *lru, int k)
{
    struct LRU *l = lru;
    struct lnode *node = hash_look_up(l->hash, k);
    struct dnode *d = NULL;

    if(node != NULL){
        d = node->dnode;
        d->next->pre = d->pre;
        d->pre->next = d->next;
        l->head.next->pre = d;
        d->next = l->head.next;
        l->head.next = d;
        d->pre = &l->head;
        return node->addr;
    }
    return NULL;
}

char* lru_set(struct LRU *lru, int k)
{
    struct LRU *l = lru;
    struct dnode *d = NULL;
    struct lnode *node = NULL;
    char *addr = NULL;

    if(l->count < l->max){
        d = (struct dnode *)malloc(sizeof(struct dnode));
        d->key = k;
        d->next = l->head.next;
        d->next->pre = d;
        d->pre = &l->head;
        l->head.next = d;
        node = hash_insert(l->hash, k, l->buf[l->count], d);
        l->count += 1;
        addr = node->addr;
        //printf("lru set new %d %lu\n", k, (ulong)addr);
    }else{
        d = l->tail.pre;
        l->tail.pre = d->pre;
        d->pre->next = &l->tail;
        addr = hash_delete(l->hash, d->key);
        //printf("lru delete  %d %lu\n", d->key, (ulong)addr);
        d->key = k;
        node = hash_insert(l->hash, k, addr, d);
        d->next = l->head.next;
        d->next->pre = d;
        d->pre = &l->head;
        l->head.next = d;
        //printf("lru set new %d %lu\n", k, (ulong)addr);
    }
    return addr;
}


