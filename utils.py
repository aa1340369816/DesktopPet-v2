import sys
import os
import winreg
import ctypes

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_save_path():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'save.json')

SAVE_FILE = get_save_path()

def get_startup_status():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, "DesktopPet")
        winreg.CloseKey(key)
        return value == sys.executable
    except:
        return False

def set_startup(enable):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Run",
                         0, winreg.KEY_SET_VALUE)
    if enable:
        winreg.SetValueEx(key, "DesktopPet", 0, winreg.REG_SZ, sys.executable)
    else:
        try:
            winreg.DeleteValue(key, "DesktopPet")
        except:
            pass
    winreg.CloseKey(key)

def check_single_instance():
    try:
        mutex = ctypes.windll.kernel32.CreateMutexW(None, True, "DesktopPet_Mutex")
        if ctypes.windll.kernel32.GetLastError() == 183:
            return False
        return True
    except:
        return True