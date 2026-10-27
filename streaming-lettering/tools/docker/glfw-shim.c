// Preloaded into Flathub's Bambu Studio so its command line can render plate thumbnails:
//  - it asks for an OpenGL context whose version is GLFW's own version number; Flathub's
//    GLFW is 3.5 and there is no OpenGL 3.5, so report 3.3;
//  - on Linux it asks for an OSMesa context, but its GLEW looks functions up through GLX,
//    which an OSMesa context lacks: ask for the native (GLX) context instead.
#define _GNU_SOURCE
#include <dlfcn.h>

#define GLFW_CONTEXT_CREATION_API 0x0002200B
#define GLFW_NATIVE_CONTEXT_API 0x00036001

void glfwGetVersion(int *major, int *minor, int *rev)
{
    if (major) *major = 3;
    if (minor) *minor = 3;
    if (rev) *rev = 0;
}

void glfwWindowHint(int hint, int value)
{
    static void (*real)(int, int);
    if (!real) real = (void (*)(int, int))dlsym(RTLD_NEXT, "glfwWindowHint");
    if (hint == GLFW_CONTEXT_CREATION_API) value = GLFW_NATIVE_CONTEXT_API;
    real(hint, value);
}
