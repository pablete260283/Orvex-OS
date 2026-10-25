/* ORVEX-owned Linux validation fixture. Built only in a temporary directory. */
#include <stdio.h>
#include <unistd.h>
#ifndef EXIT_CODE
#define EXIT_CODE 0
#endif
int main(void) {
    FILE *f = fopen("orvex-test-ran.txt", "w");
    if (!f) return 90;
    fputs("Controlled ORVEX validation only\n", f);
    fclose(f);
    usleep(250000);
    return EXIT_CODE;
}
