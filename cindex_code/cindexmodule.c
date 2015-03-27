/* "cSimple9" module */
#include <Python.h>
#include "index_op.h"
#include "term_op.h"
#include "index_if.h"
#include "bm25.h"

#define MAX_TERM 32

static struct tobj *tlist[MAX_TERM];

static int get_min(double *v, int l)
{
    int i;
    int p = 0;
    double min = v[0];

    for(i = 1; i < l; i++){
        if(v[i] < min){
            min = v[i];
            p = i;
        }
    }
    return p;
}

static PyObject* csub_daat(PyObject *lplist, PyObject *doc_dic)
{
    int i, nterm;
    int docid = 0, maxid = config.maxid;
    int dmax = 0, dtmp, count = 0;
    int dlen;
    int n;
    unsigned long data = 0;
    struct tobj **t = tlist;
    struct tobj *t1 = t[0];
    int ft[MAX_TERM];
    int fdt[MAX_TERM];

    int topsize = 0; 
    int topdoc[10];
    double vbm;
    double min;
    double topk[10];
    PyObject *item;
    PyObject *key;
 
    /* get tobj pointers */
    nterm = PyList_Size(lplist);
    for(i = 0; i < nterm; i++){
        ft[i] = t[i]->doc_num;        // ft
    }
    //printf("csub_daat %d\n", nterm); 

    while(docid < maxid){
        docid = nextGEQ(t1, docid);
        //printf("docid %d \n", docid);
        if(docid >= maxid)
            break;
        
        /* check others whether or not have docid */
        dmax = docid;
        for(i = 1; i < nterm; i++){
            dtmp = nextGEQ(t[i], docid);
            if(dtmp > dmax)
                dmax = dtmp;
        }

        if(dmax != docid){
            docid = dmax;
        }else{
            /* get fdt */
            for(i = 0; i < nterm; i++){
                fdt[i] = getFreq(t[i]);
            }
            key = PyInt_FromLong((long)docid);
            /* get dlen */
            item = PyDict_GetItem(doc_dic, key);
            item = PyList_GetItem(item, 1);
            data = PyInt_AsLong(item);
            dlen = (int)data;
            

            /* compute bm25 */
            vbm = bm25_cal(ft, fdt, dlen, nterm);
            if(topsize < 10){
                topk[topsize] = vbm;
                topdoc[topsize] = docid;
                topsize += 1;
                if(topsize == 10){
                    i = get_min(topk, 10);
                    min = topk[i];
                }
            }else{
                if(vbm > min){
                    i = get_min(topk, 10);
                    topk[i] = vbm;
                    topdoc[i] = docid;
                    i = get_min(topk, 10);
                    min = topk[i];
                }
            }
            docid += 1;
            count += 1;
        }
    }
    /* close */
    for(i = 0; i < nterm; i++){
        closelist(t[i]);
    }

    key = PyList_New(0);
    for(i = 0; i < topsize; i++){
        item = PyInt_FromLong(topdoc[i]);
        PyList_Append(key, item);
        item = PyFloat_FromDouble(topk[i]);
        PyList_Append(key, item);
    }
    item = PyInt_FromLong(count);
    PyList_Append(key, item);
    return key;
}

static int indexsize[INDEX_NUM];

static PyObject* init(PyObject *list, double d_avg, PyObject *isize)
{
    int i;
    int l;
    int info[8];
    unsigned long data = 0;
    PyObject *item;
   
    for(i = 0; i < 8; i++){
        item = PyList_GetItem(list, i);
        data = PyInt_AsLong(item);
        info[i] = (int)data;
    }
    l = PyList_Size(isize);
    for(i = 0; i < l; i++){
        item = PyList_GetItem(isize, i);
        data = PyInt_AsLong(item);
        indexsize[i] = (int)data; 
    }
    init_config(info, d_avg, indexsize);
    Py_RETURN_NONE;
}

static int open_term(PyObject *info)
{
    int i;
    int tinfo[6];
    unsigned long data = 0;
    struct tobj *t = NULL;
    PyObject *item;
   
    for(i = 0; i < 6; i++){
        item = PyList_GetItem(info, i);
        data = PyInt_AsLong(item);
        tinfo[i] = (int)data;
    }
    t = term_init(tinfo);
    tlist[term_num - 1] = t;
    return term_num;
}

/*Wrap function*/
static PyObject *
cindex_init(PyObject *self, PyObject *args){
	PyObject *input, *isize;
    double d_avg;

	if(!PyArg_ParseTuple(args, "OdO", &input, &d_avg, &isize))
	{
		return NULL;
	}
    printf("--------------------------------------------------\n");
    init(input, d_avg, isize);

//	return Py_BuildValue("");
    Py_RETURN_NONE;
}

static PyObject *
cindex_openlist(PyObject *self, PyObject *args){
	PyObject *info;
    int ret;

	if(!PyArg_ParseTuple(args, "O", &info))
	{
		return NULL;
	}
    ret = open_term(info);

	return Py_BuildValue("i", ret);
}

static PyObject *
cindex_subdaat(PyObject *self, PyObject *args){
	PyObject *lp, *doc_dic;
    PyObject *ret;

	if(!PyArg_ParseTuple(args, "OO", &lp, &doc_dic))
	{
		return NULL;
	}
    /* TO DO  daat */
    ret = csub_daat(lp, doc_dic);
	return Py_BuildValue("O", ret);
}

static PyMethodDef cindexmethods[]={
	{"init", cindex_init, METH_VARARGS},
	{"openlist", cindex_openlist, METH_VARARGS},
	{"subdaat", cindex_subdaat, METH_VARARGS},
	{NULL, NULL}
};

/* Module initialization function*/
initcindex(void){
	Py_InitModule("cindex", cindexmethods);
}

