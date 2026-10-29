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
#if defined(_WIN32) && defined(GUI_FIXTURE)
static LRESULT CALLBACK controlled_window(HWND window, UINT message, WPARAM wp, LPARAM lp) {
    if (message == WM_CLOSE) {
        FILE *f = fopen("orvex-test-close-request.txt", "w");
        if (f) { fputs("WM_CLOSE received\n", f); fclose(f); }
        DestroyWindow(window);
        return 0;
    }
    if (message == WM_DESTROY) { PostQuitMessage(0); return 0; }
    return DefWindowProcW(window, message, wp, lp);
}
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
#ifdef WAIT_FOR_RELEASE
    /* Test-only handshake: keep the process alive until UI checks finish. */
    int released = 0;
    for (int i = 0; i < 200; ++i) {
        FILE *release = fopen("orvex-test-release.txt", "r");
        if (release) { fclose(release); released = 1; break; }
#ifdef _WIN32
        Sleep(50);
#else
        usleep(50000);
#endif
    }
    if (!released) return 92;
#endif
#if defined(_WIN32) && defined(GUI_FIXTURE)
    WNDCLASSW wc = {0};
    wc.lpfnWndProc = controlled_window;
    wc.hInstance = GetModuleHandleW(NULL);
    wc.lpszClassName = L"OrvexOwnedFixture";
    if (!RegisterClassW(&wc)) return 93;
    HWND window = CreateWindowW(wc.lpszClassName, L"ORVEX controlled native window", WS_OVERLAPPEDWINDOW,
        40, 40, 640, 400, NULL, NULL, wc.hInstance, NULL);
    if (!window) return 94;
    ShowWindow(window, SW_SHOW);
    MSG message;
    while (GetMessageW(&message, NULL, 0, 0) > 0) {
        TranslateMessage(&message); DispatchMessageW(&message);
    }
#endif
    return EXIT_CODE;
}
