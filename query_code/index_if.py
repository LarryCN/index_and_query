import config
import term_op
import index_op
import cindex

""" open term 
    input term
    output termobj 
"""
def openlist(term):
    if config.CINDEX == 1:
       info = index_op.get_term_info(term)
       return cindex.openlist(info)
    else:
        return term_op.termobj(term)

""" close termobj
"""
def closelist(termobj):
    termobj.close()

""" input termobj, docid
    return next docid >= docid(input)
    if return MAXID means none
"""
def nextGEQ(termobj, docid):
    return termobj.get_docid(docid)

""" return current doc freq
    defualt first
"""
def getFreq(termobj):
    return termobj.get_freq()
