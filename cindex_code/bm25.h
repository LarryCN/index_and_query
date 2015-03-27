#ifndef BM25_H__
#define BM25_H__

struct BM25{
    double k1;
    double b;
    double d_avg;
    double Ka;
    double Kb;
    double vk1;
    int N;
};

extern void bm25_init(int N, int d_avg);
extern double bm25_cal(int *ft, int *fdt, int dlen, int len);

extern struct BM25 bm25;

#endif /* bm25.h */
