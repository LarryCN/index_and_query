#ifndef INDEX_IF_H__
#define INDEX_IF_H__

#include "term_op.h"

extern struct tobj *openlist(int *info);
extern void closelist(struct tobj* tobj);
extern int nextGEQ(struct tobj* tobj, int docid);
extern int getFreq(struct tobj* tobj);

#endif /* index_if.h */
