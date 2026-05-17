import tkinter as tk
import ctypes as ct
from ctypes import wintypes
from status_window import StatusWindow
from shop_window import ShopWindow


class StatusPanelManager:
    def __init__(self, pet):
        self.pet = pet
        self.tray_status_win = None
        self._create_tray_status_win()

    def _create_tray_status_win(self):
        win = tk.Toplevel(self.pet.pet_win)
        win.overrideredirect(True)
        win.wm_attributes("-topmost", True)
        win.configure(bg="#FFFFFF")
        win.attributes("-alpha", 0.0)
        win.geometry("1x1+-200+-200")
        win.withdraw()
        self.tray_status_win = win

    # ... 其他方法保持不变 ...

    def show_status(self):
        """打开状态窗口（智能定位 + 跟随移动）"""
        if self.pet.status_win and self.pet.status_win.win.winfo_exists():
            self.pet.status_win.win.lift()
            return

        self.pet.status_win = StatusWindow(self.pet.pet_win, self.pet.state)
        win = self.pet.status_win.win
        win.update_idletasks()
        win_w = win.winfo_reqwidth()
        win_h = win.winfo_reqheight()

        # 跟随移动 + 智能定位的函数
        def update_position():
            if not win.winfo_exists():
                return
            pet_x = self.pet.x
            pet_y = self.pet.y
            pet_w = self.pet.pet_w
            pet_h = self.pet.pet_h
            screen_w = self.pet.pet_win.winfo_screenwidth()
            screen_h = self.pet.pet_win.winfo_screenheight()

            # 水平方向：默认在宠物右侧，空间不够则放左侧
            if pet_x + pet_w + win_w + 10 <= screen_w:
                x = pet_x + pet_w + 10
            else:
                x = pet_x - win_w - 10

            # 垂直方向：居中于宠物，但不超出屏幕
            y = pet_y + (pet_h - win_h) // 2
            if y < 0:
                y = 0
            elif y + win_h > screen_h:
                y = screen_h - win_h

            win.geometry(f"+{x}+{y}")
            # 持续跟随
            win.after(200, update_position)

        update_position()

        # 关闭时清理引用
        def on_close():
            self.pet.status_win.win.destroy()
            self.pet.status_win = None

        win.protocol("WM_DELETE_WINDOW", on_close)

    # 以下方法保持不变（show_inventory, open_shop, refresh_status 等）
    # ... 保持原样即可 ...
