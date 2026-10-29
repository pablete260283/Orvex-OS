/* ORVEX-owned native validation fixture. Built only in a temporary directory. */
#include <stdio.h>
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif
#ifndef EXIT_CODE
#define EXIT_CODE 0
#endif
int main(int argc, char **argv) {
    FILE *f = fopen("orvex-test-ran.txt", "w");
    if (!f) return 90;
    fputs("Controlled ORVEX validation only\n", f);
    fclose(f);
    FILE *args = fopen("orvex-test-args.txt", "w");
    if (!args) return 91;
    for (int i = 1; i < argc; ++i) fprintf(args, "%s\n", argv[i]);
    fclose(args);
#ifdef _WIN32
    Sleep(250);
#else
    usleep(250000);
#endif
    return EXIT_CODE;
}
