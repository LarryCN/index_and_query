import gzip
import sys
import simple9
import config

TAG_B = 0
TAG_H = 1
TAG_I = 2
TAG_P = 3
TAG_T = 4
TAG_U = 5
TAG_BH = 6
TAG_BI = 7
TAG_BHI = 8
TAG_HI = 9
TAG_HT = 10
TAG_IT = 11
TAG_BT = 12
TAG_BP = 13
TAG_BIT = 14
TAG_BHT = 15
TAG_BHIT = 16
TAG_HIT = 17

class subindex:
    def __init__(self, blocknum, path):
        self.lexicon = {}
        self.blocknum = blocknum
        self.termid = 0
        self.iindex = {}
        self.path = path
        self.orderlist = []

    def datainfo(self):
        print("term id", self.termid, len(self.lexicon), len(self.iindex))
        for t in self.lexicon:
            print(t, self.lexicon[t])
        for i in self.iindex:
            print(i, self.iindex[i])

    def store(self):
        #f = gzip.open(self.path + str(self.blocknum), 'wb')
        f = open(self.path + str(self.blocknum), 'wb')
        l = [s for s in self.lexicon]
        l.sort()
        line = 0
        for t in l:
            tid = self.lexicon[t][0]    # lexicon info
            data = self.iindex[tid]
            if config.TMEP_COMPRESS == 1:
                r = simple9.simple9_encode(data, len(data))
                r = [hex(x)[2:] for x in r]
                data = str(r)[1:-1].replace('\'', '').replace(',', '').replace(' ', '')
            else:
                data = str(data)[1: -1]
            f.write(data + '\n')
            self.lexicon[t][0] = line   # line in the inverted index, doc num
            line += 1
        f.close()
        self.orderlist = l
        self.iindex = {}
        print('done')

    def size(self):
        size = 0
        for t in self.iindex:
            size += sys.getsizeof(self.iindex[t])
        return size

    """ build inverted index in this block return term count
    """
    def indexbuild(self, docid, parsed_data):
        docterm, count = {}, 0    # page lexicon and position count
        parsed_data = parsed_data.split('\n')
        """change tag char to number"""
        tag_short = {'B': TAG_B,
                     'H': TAG_H,
                     'I': TAG_I,
                     'P': TAG_P,
                     'U': TAG_U,
                     'T': TAG_T,
                     'BH': TAG_BH,
                     'BI': TAG_BI,
                     'BHI': TAG_BHI,
                     'HI': TAG_HI,
                     'HT': TAG_HT,
                     'IT': TAG_IT,
                     'BT': TAG_BT,
                     'BP': TAG_BP,
                     'BIT': TAG_BIT,
                     'BHT': TAG_BHT,
                     'BHIT': TAG_BHIT,
                     'HIT': TAG_HIT
                  }
        for t in parsed_data:
            if t:
                count += 1
                s = t.split(' ')
                c = s[1]         # type H P U B I ...
                try:
                    c = tag_short[c]
                except:
                    print('-----not include tag-----------', c)
                s = s[0]         # term
                if len(s) >= 64 or s == 'nbsp':
                    continue
                if s not in docterm:
                    if s not in self.lexicon:
                        self.lexicon[s] = [self.termid, 1]  #for inverted index, doc num
                        tid = self.termid
                        self.termid += 1
                    else:
                        self.lexicon[s][1] += 1
                        tid = self.lexicon[s][0]
                    docterm[s] = [tid, 1, count, c]
                else: 
                    docterm[s][1] += 1
                    docterm[s].append(count)
                    docterm[s].append(c)
        for t in docterm:
            con = docterm[t]               
            tid = con[0]
            if tid not in self.iindex:
                self.iindex[tid] = [docid] + con[1:]        #postings  docid, fre, position(position from 1 not 0)
            else:
                self.iindex[tid].append(docid)
                for i in xrange(1, len(con)):
                    self.iindex[tid].append(con[i])
        return count
