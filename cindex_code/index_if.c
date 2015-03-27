#include "index_if.h"
#include "term_op.h"

/*
 * openlist
 */
struct tobj* openlist(int *info)
{
    struct tobj *t;
    //int info[6];
    //printf("openlist\n");
    t = term_init(info);

    return t;
}

/*
 * close list
 */
void closelist(struct tobj* tobj)
{
    //printf("closelist \n");
    term_close(tobj);
    free(tobj);
    tobj = NULL;
}

/*
 * nextGEQ : get next docid >= input docid
 */
int nextGEQ(struct tobj* tobj, int docid)
{
    //printf("%d, next GEQ\n", docid);
    return get_docid(docid, tobj);
}

/*
 * getFreq: return current frequency
 */
int getFreq(struct tobj* tobj)
{
    //printf("get Freq \n");
    return get_freq(tobj);
}

