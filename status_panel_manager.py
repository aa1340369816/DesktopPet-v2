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

    def show_tray_status(self, *args):
        if not self.tray_status_win or not self.tray_status_win.winfo_exists():
            self._create_tray_status_win()

        win = self.tray_status_win
        if win.winfo_ismapped():
            win.lift()
            return

        # 获取任务栏位置
        class APPBARDATA(ct.Structure):
            _fields_ = [
                ("cbSize", ct.c_uint),
                ("hWnd", ct.c_void_p),
                ("uCallbackMessage", ct.c_uint),
                ("uEdge", ct.c_uint),
                ("rc", wintypes.RECT),
                ("lParam", ct.c_long),
            ]
        abd = APPBARDATA()
        abd.cbSize = ct.sizeof(APPBARDATA)
        ct.windll.shell32.SHAppBarMessage(4, ct.byref(abd))
        ct.windll.shell32.SHAppBarMessage(5, ct.byref(abd))

        taskbar_left = abd.rc.left
        taskbar_top = abd.rc.top
        taskbar_right = abd.rc.right
        taskbar_bottom = abd.rc.bottom
        screen_w = self.pet.pet_win.winfo_screenwidth()
        screen_h = self.pet.pet_win.winfo_screenheight()

        for widget in win.winfo_children():
            widget.destroy()

        w = 280
        pad = 16
        s = self.pet.state

        tk.Label(win, text="练习生状态", font=("Segoe UI", 12, "bold"),
                 fg="#000000", bg="#FFFFFF").pack(pady=(pad, 0))
        tk.Frame(win, height=1, bg="#E5E5E5").pack(fill="x", padx=pad, pady=(8, 0))

        info_frame = tk.Frame(win, bg="#FFFFFF")
        info_frame.pack(pady=(pad, 0), padx=pad, fill="x")
        lines = [
            f"身份：{s.stage_name}  Lv.{s.level}   💰{s.gold}金币",
            f"❤️健康 {s.health}/100  😫疲劳 {int(s.fatigue)}  {'🤒生病' if s.sick else '😄健康'}",
            f"🍖{int(s.satiety)}  😊{int(s.mood)}  ⚡{int(s.stamina)}  🧹{int(s.hygiene)}"
        ]
        for line in lines:
            tk.Label(info_frame, text=line, font=("Segoe UI", 10),
                     fg="#404040", bg="#FFFFFF", anchor="w", justify="left").pack(fill="x", pady=2)

        activity_name = None
        progress_pct = 0
        progress_text = ""

        if self.pet.current_activity and hasattr(self.pet.current_activity, 'get_progress'):
            activity_name = self.pet.current_activity.title if hasattr(self.pet.current_activity, 'title') else "活动中"
            progress_pct, progress_text = self.pet.current_activity.get_progress()
        elif self.pet.performance_win and hasattr(self.pet.performance_win, 'get_progress'):
            activity_name = "训练/通告中"
            progress_pct, progress_text = self.pet.performance_win.get_progress()

        if activity_name:
            tk.Frame(win, height=1, bg="#E5E5E5").pack(fill="x", padx=pad, pady=(12, 0))
            tk.Label(win, text=f"当前：{activity_name}", font=("Segoe UI", 10, "bold"),
                     fg="#000000", bg="#FFFFFF").pack(pady=(12, 0))
            bar = tk.Canvas(win, width=240, height=3, bg="#E5E5E5", highlightthickness=0)
            bar.pack(pady=(8, 4), padx=pad)
            bar.create_rectangle(0, 0, 240 * progress_pct / 100, 3, fill="#000000", outline="")
            tk.Label(win, text=f"剩余 {progress_text}", font=("Segoe UI", 9),
                     fg="#808080", bg="#FFFFFF").pack()
        else:
            tk.Label(win, text="当前空闲", font=("Segoe UI", 9),
                     fg="#808080", bg="#FFFFFF").pack(pady=(8, 0))

        def hide():
            win.withdraw()

        btn = tk.Button(win, text="关闭", font=("Segoe UI", 10),
                        fg="#000000", bg="#FFFFFF", activebackground="#F5F5F5",
                        bd=1, relief="solid", padx=12, pady=4,
                        command=hide)
        btn.pack(pady=(12, pad))

        win.update_idletasks()
        h = win.winfo_reqheight()
        if h < 180:
            h = 180

        if taskbar_bottom >= screen_h:
            x = taskbar_right - w - 8
            y = taskbar_top - h - 8
        elif taskbar_top <= 0:
            x = taskbar_right - w - 8
            y = taskbar_bottom + 8
        elif taskbar_left <= 0:
            x = taskbar_right + 8
            y = taskbar_bottom - h - 8
        else:
            x = taskbar_left - w - 8
            y = taskbar_bottom - h - 8

        win.geometry(f"{w}x{h}+{x}+{y}")
        win.attributes("-alpha", 1.0)
        win.deiconify()
        win.protocol("WM_DELETE_WINDOW", hide)

    def show_status(self):
        if self.pet.status_win and self.pet.status_win.win.winfo_exists():
            self.pet.status_win.win.lift()
            return
        self.pet.status_win = StatusWindow(self.pet.pet_win, self.pet.state)
        self.pet.status_win.win.geometry(f"+{self.pet.x+self.pet.pet_w+10}+{self.pet.y}")

        def on_close():
            self.pet.status_win.win.destroy()
            self.pet.status_win = None
        self.pet.status_win.win.protocol("WM_DELETE_WINDOW", on_close)

    def show_inventory(self):
        inv = self.pet.state.inventory
        win = tk.Toplevel(self.pet.pet_win)
        win.title("背包")
        win.geometry("300x400")
        tk.Label(win, text="🎒 背包", font=("微软雅黑",14,"bold")).pack(pady=10)
        if not inv:
            tk.Label(win, text="背包空空如也").pack()
        else:
            for name, qty in inv.items():
                tk.Label(win, text=f"{name} x{qty}", font=("微软雅黑",10)).pack(anchor="w", padx=20, pady=2)

    def open_shop(self):
        if self.pet.shop_win and self.pet.shop_win.win.winfo_exists():
            self.pet.shop_win.win.lift()
            return
        self.pet.shop_win = ShopWindow(self.pet.pet_win, self.pet.state)

    def refresh_status(self):
        if self.pet.status_win and self.pet.status_win.win.winfo_exists():
            self.pet.status_win.refresh()
