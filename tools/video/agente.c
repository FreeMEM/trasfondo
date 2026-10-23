/* agente: lo que el piloto de fuera no puede hacer por el socket de Amiberry, hecho dentro del Amiga.
 * Su buzón es un puerto público llamado "agente" (la lista de puertos no cambia mientras se lee, la de
 * tareas sí); el piloto escribe ahí una orden (WRITE_MEM) y sube "pedida"; el agente la cumple y pone
 * "hecha" igual. Desplazamientos: magia 36, pedida 40, hecha 44, orden 48, a 52, b 56, texto 60.
 *   1 TECLA   a = código raw, b = calificador          (pulsada y soltada)
 *   2 LANZAR  texto = orden del Shell, sin esperar
 *   3 ESCRIBIR texto con el mapa de teclado en uso (MapANSI)
 *   9 SALIR
 * Herramienta para grabar vídeos: no va en ningún paquete. */
#include <exec/types.h>
#include <exec/memory.h>
#include <devices/input.h>
#include <devices/inputevent.h>
#include <dos/dostags.h>
#include <proto/exec.h>
#include <proto/dos.h>
#include <proto/keymap.h>
#include <clib/alib_protos.h>
#include <string.h>

struct Buzon {
    struct MsgPort puerto;      /* 34 bytes */
    UWORD relleno;
    ULONG magia;                /* 'PILO' */
    volatile ULONG pedida, hecha;
    volatile LONG orden, a, b;
    char texto[256];
};

struct Library *KeymapBase;

/* Un gancho de cambio de tarea que no hace nada: los medidores de CPU (Trasfondo, como PM) no tocan ni
 * cuentan una tarea que ya tiene ganchos de otro programa, así que el agente no sale en el vídeo. */
static void nada(void) {}
static struct IOStdReq *io;

static void evento(UWORD code, UWORD qual)
{
    struct InputEvent ie;
    memset(&ie, 0, sizeof(ie));
    ie.ie_Class = IECLASS_RAWKEY;
    ie.ie_Code = code;
    ie.ie_Qualifier = qual;
    io->io_Command = IND_WRITEEVENT;
    io->io_Data = &ie;
    io->io_Length = sizeof(ie);
    DoIO((struct IORequest *)io);
}

static void tecla(UWORD code, UWORD qual)
{
    evento(code, qual);
    Delay(2);
    evento(code | IECODE_UP_PREFIX, qual);
    Delay(2);
}

static void escribir(const char *s)
{
    UBYTE buf[16];
    for (; *s; s++) {
        LONG n = MapANSI((STRPTR)s, 1, (STRPTR)buf, sizeof(buf) / 2, NULL);
        LONG i;
        for (i = 0; i < n; i++) tecla(buf[i * 2], buf[i * 2 + 1]);
        Delay(3);
    }
}

int main(void)
{
    struct MsgPort *port;
    struct Buzon *b;
    struct Task *yo = FindTask(NULL);
    if (!(KeymapBase = OpenLibrary("keymap.library", 37))) return 20;
    if (!(port = CreateMsgPort())) return 20;
    if (!(io = (struct IOStdReq *)CreateIORequest(port, sizeof(struct IOStdReq)))) return 20;
    if (OpenDevice("input.device", 0, (struct IORequest *)io, 0)) return 20;
    if (!(b = AllocVec(sizeof(*b), MEMF_PUBLIC | MEMF_CLEAR))) return 20;
    b->magia = 0x50494C4F;
    b->puerto.mp_Node.ln_Name = "agente";
    b->puerto.mp_Node.ln_Type = NT_MSGPORT;
    b->puerto.mp_Flags = PA_IGNORE;
    NewList(&b->puerto.mp_MsgList);
    AddPort(&b->puerto);
    yo->tc_UserData = b;
    Forbid();
    yo->tc_Switch = (APTR)nada;
    yo->tc_Flags |= TF_SWITCH;
    Permit();
    for (;;) {
        if (SetSignal(0, 0) & SIGBREAKF_CTRL_C) break;
        if (b->pedida != b->hecha) {
            b->texto[sizeof(b->texto) - 1] = 0;
            if (b->orden == 1) tecla((UWORD)b->a, (UWORD)b->b);
            else if (b->orden == 2) {
                BPTR nil = Open("NIL:", MODE_NEWFILE);
                if (SystemTags((STRPTR)b->texto, SYS_Input, nil, SYS_Output, NULL, SYS_Asynch, TRUE, TAG_DONE) == -1)
                    Close(nil);
            } else if (b->orden == 3) escribir(b->texto);
            else if (b->orden == 9) { b->hecha = b->pedida; break; }
            b->hecha = b->pedida;
        }
        Delay(1);
    }
    yo->tc_UserData = NULL;
    Forbid();
    yo->tc_Flags &= ~TF_SWITCH;
    Permit();
    RemPort(&b->puerto);
    Delay(10);
    FreeVec(b);
    CloseDevice((struct IORequest *)io);
    DeleteIORequest((struct IORequest *)io);
    DeleteMsgPort(port);
    CloseLibrary(KeymapBase);
    return 0;
}
