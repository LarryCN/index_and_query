#include "simple9.h" 

#define SIMPLE_9  9
#define SIMPLE_8  8
#define SIMPLE_7  7
#define SIMPLE_6  6
#define SIMPLE_5  5
#define SIMPLE_4  4
#define SIMPLE_3  3
#define SIMPLE_2  2
#define SIMPLE_1  1
/*  first 4 bits  1: 1; 2: 2; 3: 3; 4: 4; 5: 5; 6: 7; 7: 9; 8: 14; 9: 28; others not simple9 encode
    -1  28bit 0 ~ 268435455       -7  4bit 0 ~ 15     
    -2  14bit 0 ~ 16383           -9  3bit 0 ~ 7
    -3  9bit  0 ~ 511             -14 2bit 0 ~ 3
    -4  7bit  0 ~ 127             -28 1bit 0 ~ 1
    -5  5bit  0 ~ 31

    0000  ... 3 2 1
    4bit    data
*/

static unsigned int de_simple[9][3] = {
    28,      0x1, 1,     
    14,      0x3, 2,
    9,       0x7, 3,
    7,       0xf, 4,
    5,      0x1f, 5,
    4,      0x7f, 7,
    3,     0x1ff, 9,
    2,    0x3fff,14,
    1, 0xfffffff,28
};

int simple9_decode(uint *input, int *output, int len)
{
    uint *in = input;
    int *out = output;
    int off = 0;
    int count = 0;
    int i;
    unsigned int data = 0;
    unsigned int code = 0;
    uint *de;
    
    count = 0;
    while (off < len){ 
        data = in[off];
        code =((data & 0xf0000000) >> 28);
        data = data & 0xfffffff;
        de = de_simple[9 - code];
        off += 1;
        for(i = 0; i < de[0]; i++){
            out[count] = (int)(data & de[1]);
            data >>= de[2];
            count += 1;
        }
    }
    return count;
}

