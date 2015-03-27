# by larry Mar 14th, 2015

class BM25:
    def __init__(self, N, doc_dic):
        self.k1 = 1.2
        self.b = 0.75
        self.N = N
        tlen = 0
        for d in doc_dic:
            tlen += doc_dic[d][1]
        self.d_avg = tlen * 1.0 / len(doc_dic)

        self.Ka = self.k1 *(1 - self.b)    # K = self.Ka + self.Kb * dlen
        self.Kb = self.k1 * self.b / self.d_avg
        self.vk1 = 1 + self.k1

    """BM25(q, d) = sum(log((N - ft + 0.5)/(ft + 0.5) * (k1 + 1)fdt / (K + fdt)))
       for t in q
       K = k1 * ((1 - b) + b * |d| / |d|avg)
       N: total number documents    ft: number of documents contain term t
       fdt: frequency of term t in document t          |d|: len d
       k1 = 1.2   b = 0.75
    """
    """
    def cal_one(self, ft, fdt, dlen):
        K = self.k1 * ((1 - self.b) + self.b * dlen / self.d_avg)
        val = (self.N - ft + 0.5) / (ft + 0.5) * (self.k1 + 1) * fdt / (K + fdt)
        return val
    """
    """ freq is a list of fdt 
    """
    def cal(self, ft, fdt, dlen):
        product = 1
        #K = self.k1 * ((1 - self.b) + self.b * dlen / self.d_avg)
        K = self.Ka + self.Kb * dlen
        for i in range(len(ft)):
            #val = self.cal_one(ft[i], fdt[i], dlen)
            val = math.log10((self.N - ft[i] + 0.5) / (ft[i] + 0.5)) * self.vk1 * fdt[i] / (K + fdt[i])
            product *= val
        return product

