#include <stdio.h>
#include <stdlib.h>


unsigned char CRCMaker(unsigned char b_input, unsigned char b_crc) {
    long w,c;
    int i;
    //unsigned char c;
    w=b_input + (b_crc << 8);
    for (i=0;i<8;i++) {
        c=w & 0x8000;
        w=w << 1;
        if (c != 0) {
            w=w ^ 0x6900;
        }
    }
    return w >> 8;
}

int main(int argc, char *argv[]) {
    unsigned char res,i,a;
    res=0;

    for (i=1;i<argc;i++) {
        a=(unsigned char)strtol(argv[i],NULL,16);
        res=CRCMaker(a,res);
    }
    //printf("%d\n",CRCMaker(0x00, CRCMaker(0xC3, CRCMaker(0x01, 0))));
    printf("%x\n",res);
    return 0;
}


