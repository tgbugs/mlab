import ctypes
import ctypes.wintypes
from tomsDebug import TDB,ploc
import rpdb2
tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict
tdbOff=tdb.tdbOff
tdbOff()

def Listener(charBuffer,keyHandler,modestate=None,cleanup=lambda:0): #FIXME
        #http://techtonik.rainforce.org
        STD_INPUT_HANDLE = -10
        # Constant for infinite timeout in WaitForMultipleObjects()
        INFINITE = -1

        # --- processing input structures -------------------------
        # INPUT_RECORD structure
        #  events:
        EVENTIDS = dict(
          FOCUS_EVENT = 0x0010,
          KEY_EVENT = 0x0001,      # only key event is handled
          MENU_EVENT = 0x0008,
          MOUSE_EVENT = 0x0002,
          WINDOW_BUFFER_SIZE_EVENT = 0x0004)
        EVENTS = dict(zip(EVENTIDS.values(), EVENTIDS.keys()))
        #  records:
        class _uChar(ctypes.Union):
          _fields_ = [('UnicodeChar', ctypes.wintypes.WCHAR),
                      ('AsciiChar', ctypes.wintypes.CHAR)]
        class KEY_EVENT_RECORD(ctypes.Structure):
          _fields_ = [
            ('keyDown', ctypes.wintypes.BOOL),
            ('repeatCount', ctypes.wintypes.WORD),
            ('virtualKeyCode', ctypes.wintypes.WORD),
            ('virtualScanCode', ctypes.wintypes.WORD),
            ('char', _uChar),
            ('controlKeyState', ctypes.wintypes.DWORD)]
        class _Event(ctypes.Union):
          _fields_ = [('keyEvent', KEY_EVENT_RECORD)]
          #  MOUSE_EVENT_RECORD        MouseEvent;
          #  WINDOW_BUFFER_SIZE_RECORD WindowBufferSizeEvent;
          #  MENU_EVENT_RECORD         MenuEvent;
          #  FOCUS_EVENT_RECORD        FocusEvent;
        class INPUT_RECORD(ctypes.Structure):
          _fields_ = [
            ('eventType', ctypes.wintypes.WORD),
            ('event', _Event)]
        # --- /processing input structures ------------------------

        # OpenProcess returns handle that can be used in wait functions
        # params: desiredAccess, inheritHandle, processId

        ch = ctypes.windll.kernel32.GetStdHandle(STD_INPUT_HANDLE)

        handle=ctypes.wintypes.HANDLE(ch)

        ctypes.windll.kernel32.FlushConsoleInputBuffer(ch)
        eventnum = ctypes.wintypes.DWORD()
        eventread = ctypes.wintypes.DWORD()
        inbuf = (INPUT_RECORD * 1)()

        WAIT_OBJECT=0x00000000 #needed to match the return type for ret

        #main loop
        stopflag=0
        #rpdb2.setbreak()
        while not stopflag:
            # params: handle, milliseconds
            ret = ctypes.windll.kernel32.WaitForSingleObject(handle, INFINITE)
            #print('im here in the while loop')
            if ret == WAIT_OBJECT:
                # --- processing input ---------------------------
                ctypes.windll.kernel32.GetNumberOfConsoleInputEvents(ch, ctypes.byref(eventnum))
                for i in range(eventnum.value):
                    # params: handler, buffer, length, eventsnum
                    ctypes.windll.kernel32.ReadConsoleInputW(ch, ctypes.byref(inbuf), 2, ctypes.byref(eventread))
                    if EVENTS[inbuf[0].eventType] != 'KEY_EVENT':
                        #print(EVENTS[inbuf[0].eventType])
                        pass
                    else:
                        keyEvent = inbuf[0].event.keyEvent
                        if not keyEvent.keyDown:
                            continue
                        char = keyEvent.char.UnicodeChar.lower()
                        printD(char)
                        #printD(charBuffer)
                        charBuffer.put_nowait(char) #THIS WORKS because if there is a get() waiting on the stack it will tigger on the first keyHandler call, though, FIXME race conditions be here! somehow I think queue is built for this
                        #sleep(.001) #YEP IT WAS A FUCKING RACE CONDITION .0001 is too fast

                        #keyRet=keyHandler()
                        #if keyRet==2: 
                            #modestate.doneCB()
                            #modestate.cond.acquire()
                            #modestate.cond.notify_all()
                            #modestate.cond.release()

                            #acquire the lock

                        stopflag=not keyHandler() #no buffer, race conditions suck
                        #stopflag=not keyHandler(char) #no buffer, race conditions suck
                        if char == '@': #emergency break
                            stopflag=1 #FIXME! this is a hack, integrate it properly
            else:
                print("Warning: Unknown return value '%s'" % ret)
        ctypes.windll.kernel32.FlushConsoleInputBuffer(ch)
        cleanup()
