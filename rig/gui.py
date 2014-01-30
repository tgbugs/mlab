#uses win32gui to controler recalcitrant API-less datasources >_<
#XXX broken due to inability to focus window

from time import sleep

try:
    import win32gui as wig
    import win32ui as wui
    import win32con as wic
    from win32api import SetCursorPos, mouse_event


    def get_windows(): #XXX depricated
        toplist=[]
        winlist=[]

        def enum_callback(hwnd, results):
            winlist.append((hwnd,wig.GetWindowText(hwnd)))

        wig.EnumWindows(enum_callback, toplist)
        return winlist

    def getLeftBottom(window):
        return window.GetWindowRect()[0::3] #left,top,right,bottom

    def clickMouse(x,y,slp=0): #FIXME need a way to change focus back to the original window!
        """click ye mouse"""
        mX,mY=wig.GetCursorPos() #save the position so we can return to it
        SetCursorPos((x,y))
        mouse_event(wic.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        sleep(slp)
        mouse_event(wic.MOUSEEVENTF_LEFTUP,x,y,0,0)
        SetCursorPos((mX,mY))
        


    #offsets always reported in x,y
    SNAPSHOT_OFFSET_LB=120,35



    def takeScreenCap():
        #wintv=wig.FindWindow(None,"WinTV7")
        wintv=wui.FindWindow(None,"WinTV7")
        if not wintv:
            raise IOError('WinTV7 not found! Is it on!?')
        lb=getLeftBottom(wintv)
        lo=SNAPSHOT_OFFSET_LB[0]
        bo=SNAPSHOT_OFFSET_LB[1]
        x=lb[0]+lo
        y=lb[1]+bo
        clickMouse(x,y,.001) #MAKE SURE THE WINDOW IS NOT COVERED!

except ImportError:
    def clickMouse(x,y,slp=0):
        print('click click, oh wait we don\'t need that here!')
    def takeScreenCap():
        print('LOL STUPID WINDOWS NOT HAVING REAL APIS. LINUX FOREVAR!')

def main():
    takeScreenCap()

if __name__ == '__main__':
    main()


