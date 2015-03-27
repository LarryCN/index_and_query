#include "def.h"
#include "bm25.h"
#include <math.h>

struct BM25 bm25;

void bm25_init(int N, int d_avg)
{
    bm25.k1 = 1.2;
    bm25.b = 0.75;
    bm25.N = N;
    bm25.d_avg = d_avg;
    bm25.Ka = bm25.k1 * (1 - bm25.b);
    bm25.Kb = bm25.k1 * bm25.b / bm25.d_avg;
    bm25.vk1 = 1 + bm25.k1; 
}

double bm25_cal(int *ft, int *fdt, int dlen, int len)
{
    int i;
    struct BM25 *bm = &bm25;
    double product = 1;
    double val;
    double K = bm->Ka + bm->Kb * dlen;

    for(i = 0; i < len; i++){
        val = log10((double)(bm->N - ft[i] + 0.5)/(double)(ft[i] + 0.5)) * bm->vk1 * (double)fdt[i]/(K + fdt[i]);
        product += val;
    }

    return product;
}
