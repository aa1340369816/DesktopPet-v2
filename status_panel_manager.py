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
        # 如果窗口已显示，只需提到最前，但也要刷新内容（可能已过时）
        # 为了确保进度条动态更新，我们将重建内容并启动定时刷新
        # 因此不再简单 return，而是强制重建并开始刷新循环

        # 先停止旧的刷新循环（如果有）
        if hasattr(self, '_refresh_job') and self._refresh_job:
            win.after_cancel(self._refresh_job)
            self._refresh_job = None

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

        # 清空窗口原有内容
        for widget in win.winfo_children():
            widget.destroy()

        w = 280
        pad = 16
        s = self.pet.state

        # 标题
        tk.Label(win, text="练习生状态", font=("Segoe UI", 12, "bold"),
                 fg="#000000", bg="#FFFFFF").pack(pady=(pad, 0))
        tk.Frame(win, height=1, bg="#E5E5E5").pack(fill="x", padx=pad, pady=(8, 0))

        import time as time_module
        now = time_module.localtime()
        weekday_map = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        time_str = f"{now.tm_year}/{now.tm_mon:02d}/{now.tm_mday:02d} {weekday_map[now.tm_wday]} {now.tm_hour:02d}:{now.tm_min:02d}"

        info_frame = tk.Frame(win, bg="#FFFFFF")
        info_frame.pack(pady=(pad, 0), padx=pad, fill="x")
        lines = [
            f"🕒 {time_str}",
            f"身份：{s.stage_name}  Lv.{s.level}   💰{s.gold}金币",
            f"❤️健康 {s.health}/100  😫疲劳 {int(s.fatigue)}  {'🤒生病' if s.sick else '😄健康'}",
            f"🍖{int(s.satiety)}  😊{int(s.mood)}  ⚡{int(s.stamina)}  🧹{int(s.hygiene)}"
        ]
        for line in lines:
            tk.Label(info_frame, text=line, font=("Segoe UI", 10),
                     fg="#404040", bg="#FFFFFF", anchor="w", justify="left").pack(fill="x", pady=2)

        # ---------- 活动进度动态区域 ----------
        # 用于存储需要动态更新的控件
        self._dynamic_widgets = []

        activity_name = self.pet.current_activity_name
        progress_pct = 0
        progress_text = ""
        total_pct = 0

        if activity_name:
            # 尝试获取当前进度
            if self.pet.current_activity and hasattr(self.pet.current_activity, 'get_progress'):
                progress_pct, progress_text = self.pet.current_activity.get_progress()
                if hasattr(self.pet.current_activity, 'get_total_progress'):
                    total_pct = self.pet.current_activity.get_total_progress()
            elif self.pet.performance_win and hasattr(self.pet.performance_win, 'get_progress'):
                progress_pct, progress_text = self.pet.performance_win.get_progress()

        if activity_name:
            # 分隔线
            tk.Frame(win, height=1, bg="#E5E5E5").pack(fill="x", padx=pad, pady=(12, 0))
            # 活动名称
            name_label = tk.Label(win, text=f"当前：{activity_name}", font=("Segoe UI", 10, "bold"),
                                  fg="#000000", bg="#FFFFFF")
            name_label.pack(pady=(12, 0))
            self._dynamic_widgets.append(name_label)

            # 阶段进度条
            stage_bar = tk.Canvas(win, width=240, height=3, bg="#E5E5E5", highlightthickness=0)
            stage_bar.pack(pady=(8, 4), padx=pad)
            self._dynamic_widgets.append(stage_bar)

            # 剩余时间文字
            remain_label = tk.Label(win, text=f"剩余 {progress_text}", font=("Segoe UI", 9),
                                    fg="#808080", bg="#FFFFFF")
            remain_label.pack()
            self._dynamic_widgets.append(remain_label)

            # 总时长进度条（如果有）
            if hasattr(self.pet.current_activity, 'get_total_progress'):
                total_bar = tk.Canvas(win, width=240, height=2, bg="#E5E5E5", highlightthickness=0)
                total_bar.pack(pady=(8, 4), padx=pad)
                self._dynamic_widgets.append(total_bar)
                total_label = tk.Label(win, text=f"总进度 {total_pct}%", font=("Segoe UI", 8),
                                       fg="#808080", bg="#FFFFFF")
                total_label.pack()
                self._dynamic_widgets.append(total_label)

            # 中止按钮
            def cancel_activity():
                self.pet.action_manager.cancel_current_activity()
                hide()

            cancel_btn = tk.Button(win, text="中止活动", font=("Segoe UI", 10),
                                   fg="#FF0000", bg="#FFFFFF", activebackground="#F5F5F5",
                                   bd=1, relief="solid", padx=12, pady=4,
                                   command=cancel_activity)
            cancel_btn.pack(pady=(4, 0))
        else:
            tk.Label(win, text="当前空闲", font=("Segoe UI", 9),
                     fg="#808080", bg="#FFFFFF").pack(pady=(8, 0))

        # 关闭按钮
        def hide():
            win.withdraw()
            # 停止刷新循环
            if hasattr(self, '_refresh_job') and self._refresh_job:
                win.after_cancel(self._refresh_job)
                self._refresh_job = None

        btn = tk.Button(win, text="关闭", font=("Segoe UI", 10),
                        fg="#000000", bg="#FFFFFF", activebackground="#F5F5F5",
                        bd=1, relief="solid", padx=12, pady=4,
                        command=hide)
        btn.pack(pady=(12, pad))

        # 定位
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

        # 绑定窗口关闭事件
        win.protocol("WM_DELETE_WINDOW", hide)

        # 启动动态刷新
        def refresh_loop():
            if not win.winfo_exists():
                return
            if not win.winfo_ismapped():
                # 窗口已被隐藏，停止刷新
                self._refresh_job = None
                return

            # 检查活动是否还存在
            act_name = self.pet.current_activity_name
            if not act_name:
                # 活动已结束，关闭面板或刷新显示空闲
                self.show_tray_status()
                return

            # 更新阶段进度
            new_pct = 0
            new_text = ""
            if self.pet.current_activity and hasattr(self.pet.current_activity, 'get_progress'):
                new_pct, new_text = self.pet.current_activity.get_progress()
            elif self.pet.performance_win and hasattr(self.pet.performance_win, 'get_progress'):
                new_pct, new_text = self.pet.performance_win.get_progress()

            # 更新总进度
            new_total = 0
            if self.pet.current_activity and hasattr(self.pet.current_activity, 'get_total_progress'):
                new_total = self.pet.current_activity.get_total_progress()

            # 找到对应的控件并更新
            if hasattr(self, '_dynamic_widgets'):
                # 名称 label 是第0个，阶段进度条第1个，剩余文字第2个，总进度条可能第3，总文字可能第4
                # 根据实际添加的顺序更新
                widgets = self._dynamic_widgets
                # 更新阶段进度条
                if len(widgets) >= 2:
                    stage_canvas = widgets[1]
                    stage_canvas.delete("all")
                    stage_canvas.create_rectangle(0, 0, 240 * new_pct / 100, 3, fill="#000000", outline="")
                # 更新剩余文字
                if len(widgets) >= 3:
                    remain_label = widgets[2]
                    remain_label.config(text=f"剩余 {new_text}")
                # 更新总进度条和文字
                if len(widgets) >= 5:
                    total_canvas = widgets[3]
                    total_canvas.delete("all")
                    total_canvas.create_rectangle(0, 0, 240 * new_total / 100, 2, fill="#CCCCCC", outline="")
                    total_text_label = widgets[4]
                    total_text_label.config(text=f"总进度 {new_total}%")

            # 继续循环
            self._refresh_job = win.after(1000, refresh_loop)

        # 只有在有活动时才启动刷新
        if activity_name:
            self._refresh_job = win.after(1000, refresh_loop)

    def refresh_tray_status_if_open(self):
        """如果托盘状态窗口正在显示，则刷新内容"""
        if self.tray_status_win and self.tray_status_win.winfo_ismapped():
            self.show_tray_status()

    def show_status(self):
        if self.pet.status_win and self.pet.status_win.win.winfo_exists():
            self.pet.status_win.win.lift()
            return

        self.pet.status_win = StatusWindow(self.pet.pet_win, self.pet.state)
        win = self.pet.status_win.win
        win.update_idletasks()
        win_w = win.winfo_reqwidth()
        win_h = win.winfo_reqheight()

        def update_position():
            if not win.winfo_exists():
                return
            pet_x = self.pet.x
            pet_y = self.pet.y
            pet_w = self.pet.pet_w
            pet_h = self.pet.pet_h
            screen_w = self.pet.pet_win.winfo_screenwidth()
            screen_h = self.pet.pet_win.winfo_screenheight()

            if pet_x + pet_w + win_w + 10 <= screen_w:
                x = pet_x + pet_w + 10
            else:
                x = pet_x - win_w - 10

            y = pet_y + (pet_h - win_h) // 2
            if y < 0:
                y = 0
            elif y + win_h > screen_h:
                y = screen_h - win_h

            win.geometry(f"+{x}+{y}")

        update_position()
        self.pet.register_follow_window(win, update_position)

        def on_close():
            self.pet.unregister_follow_window(win)
            self.pet.status_win.win.destroy()
            self.pet.status_win = None

        win.protocol("WM_DELETE_WINDOW", on_close)

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
