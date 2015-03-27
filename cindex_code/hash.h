#ifndef HASH_H__
#define HASH_H__

//#define MODNUM  11
#define MODNUM  977

struct dnode{
    int key;
    struct dnode *pre;
    struct dnode *next;
};

struct lnode{
    int key;
    char* addr;
    struct dnode *dnode;
    struct lnode *next; 
};

struct hash{
    struct lnode *slot[MODNUM];
};

extern void hash_init(struct hash *h);
extern struct lnode* hash_look_up(struct hash *h, int k);
extern struct lnode* hash_insert(struct hash *h, int k, char* addr, struct dnode *dnode);
extern char* hash_delete(struct hash *h, int k);

#endif /* hash.h */
