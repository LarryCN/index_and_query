#include <stdio.h>
#include <stdlib.h>
#include "hash.h"
#include "def.h"

void hash_init(struct hash *h)
{
    int i;

    for(i = 0; i < MODNUM; i++){
        h->slot[i] = NULL;
    }
}

struct lnode* hash_look_up(struct hash *h, int k)
{
    int index = k % MODNUM;
    struct lnode* node = h->slot[index];

    while(node != NULL && node->key != k){
        node = node->next;
    }
    return node;
}

struct lnode* hash_insert(struct hash *h, int k, char* addr, struct dnode *dnode)
{
    int index = k % MODNUM;
    struct lnode* node = h->slot[index];
    struct lnode* new = (struct lnode *)malloc(sizeof(struct lnode));

    new->key = k;
    new->addr = addr;
    new->next = NULL;
    new->dnode = dnode;
    
    if(node == NULL){
        h->slot[index] = new;
    }else{
        while(node->next != NULL){
            node = node->next;
        }
        node->next = new;
    }
    return new;
}

char* hash_delete(struct hash *h, int k)
{
    int index = k % MODNUM;
    struct lnode *node = h->slot[index];
    struct lnode *pre;
    char *addr = NULL;
    if(node != NULL){
        if(node->key == k){
            h->slot[index] = node->next;
            addr = node->addr;
            free(node);
            return addr; // TODO
        }
        pre = node;
        node = node->next;
        while(node != NULL && node->key != k){
            node = node->next;
            pre = pre->next;
        }
        if(node != NULL){
            pre->next = node->next;
            addr = node->addr;
            free(node);
        }
    }
    return addr;
}



