try:
    #for windows
    import ctypes.wintypes
    import ctypes
except: #FIXME this is not accurate...
    #for linux
    print('out not import ctypes.wintypes assuming linux')
    import sys
    import select
    import tty
    import termios

from debug import TDB,ploc
try:
    import rpdb2
except:
    pass

tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict
tdb.off()

def kl_lin(charBuffer,keyHandler,keyLock,termInfoSet):
    #FIXME does not work properly with ipython :/
    #FIXME still has problems with c-ctrl
    old_settings = termios.tcgetattr(sys.stdin)

    #functions to pass to the callback for managing ipython
    off=lambda:termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    on=lambda:tty.setcbreak(sys.stdin.fileno())
    termInfoSet(off,on)

    try:
        tty.setcbreak(sys.stdin.fileno())
        poll = select.poll()
        poll.register(sys.stdin, select.POLLIN)
        stopflag=0
        while not stopflag:
            try:
                keyLock.acquire() #XXX lock acquire
                poll.poll()
                peek=sys.stdin.buffer.peek()
                char = sys.stdin.read(1) #FIXME this may be too short for escape sequences...
                if char == '\x1b':
                    if len(peek) == 3: #escape sequences
                        char=sys.stdin.read(2) #ignore the escape since esc has its own
                    elif len(peek) == 4: #delete key
                        char=sys.stdin.read(3)
                    elif len(peek) == 5: #all the <F> keys
                        char=sys.stdin.read(4)
                    elif len(peek) > 5:
                        sys.stdin.read(len(peek)-1) #this is to catch the weird erros where <F> keys land in stdin faster than poll can loop through
                        char='esc'
                    else:
                        char='esc' #FIXME
                printD(char.encode())
                charBuffer.put_nowait(char)
                keyLock.release() #XXX lock release
                stopflag = not keyHandler()
                if char == '@':
                    stopflag=1
            except: #FIXME???
                keyLock.release()
    except KeyboardInterrupt:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def kl_win(charBuffer,keyHandler,keyLock): #FIXME
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
      WINDOW_BUFFER_SIZE_EVENT = 0x0004,
    )
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

    keyCodeDict={ #make the windows match the linux
        #None:'shift', #TODO modifier keys do exist for these
        #None:'ctrl',
        #13:'\n', #enter
        38:'[A', #up
        40:'[B', #down
        39:'[C', #right
        37:'[D', #left
        46:'[3~', #delete
        36:'[7~', #home
        35:'[8~', #end
        #8:'\x7f', #backspace FIXME on windows this is \x08 wtf
    }

    #main loop
    stopflag=0
    #rpdb2.setbreak()
    while not stopflag:
        try:
            keyLock.acquire() #XXX lock acquire
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
                        printD(keyEvent.virtualKeyCode)
                        if char == '\x00':
                            try:
                                char=keyCodeDict[keyEvent.virtualKeyCode]
                            except:
                                continue
                        elif char == '\x1b': #rebind for esc keys and linux compat
                            char = 'esc'
                        elif char == '\x08':
                            char = '\x7f' #make windows and linux match 
                        elif char == '\r': #make things consistent between windows and linux
                            char = '\n'
                        printD(char.encode())
                        charBuffer.put_nowait(char) #THIS WORKS because if there is a get() waiting on the stack it will tigger on the first keyHandler call, though, FIXME race conditions be here! somehow I think queue is built for this
                        #sleep(.001) #YEP IT WAS A FUCKING RACE CONDITION .0001 is too fast
                        keyLock.release() #XXX lock release
                        stopflag = not keyHandler()
                        if char == '@': #emergency break
                            stopflag=1 #FIXME! this is a hack, integrate it properly
            else:
                print("Warning: Unknown return value '%s'" % ret)
        except:
            keyLock.release() #FIXME
        ctypes.windll.kernel32.FlushConsoleInputBuffer(ch)

def keyListener(charBuffer,keyHandler,keyLock=None,termInfoSet=lambda off,on:None,cleanup=lambda:0): #FIXME
    if keyLock == None: 
        from threading import RLock
        keyLock=Rlock()
    try:
        if globals().get('ctypes'):
            termInfoSet(lambda:None,lambda:None)
            kl_win(charBuffer,keyHandler,keyLock)
        else:
            kl_lin(charBuffer,keyHandler,keyLock,termInfoSet)
    finally:
        cleanup()

def main():
    from queue import Queue
    keyListener(Queue(),lambda: 1) #this still randomly causes crashes in windows sometimes during rapid key input

if __name__ == '__main__':
    main()
