// Auto-generated by ayasin's gen-kernel.py version 0.3 invoked with:
//  (align=6, instruction=['NOP', 'test %rax,%rax', 'jle Lbl_end'], mode='basicblock', num=1, offset=0) .
// Do not modify!
//
#include <stdio.h>
#include <stdlib.h>
int main(int argc, const char* argv[])
{
    long i,n;
    if (argc<2) {
        printf("%s: missing <num-iterations> arg!\n", argv[0]);
        exit(-1);
    }
    n= atol(argv[1]);
    asm("	PAUSE");
    asm("       mov $10,%rax");
        asm(".align 64");
    for (i=0; i<n; i++) {
        asm("	NOP");
        asm("	test %rax,%rax");
        asm("	jle Lbl_end");
    }
    asm(".align 512; Lbl_end:");

    return 0;
}
