import tkinter as tk

class ActivityWindow:
    """通用活动进度窗口（可选隐藏）"""
    def __init__(self, parent, title, duration, on_finish, on_cancel=None,
                 pet_x=0, pet_y=0, pet_w=160, pet_h=220, visible=True):
        self.parent = parent
        self.title = title
        self.duration = duration
        self.elapsed = 0
        self.step = 0.1
        self.cancelled = False
        self.on_finish = on_finish
        self.on_cancel = on_cancel
        self.win = None

        if visible:
            self._create_window(pet_x, pet_y, pet_w, pet_h)
        else:
            # 无窗口模式，启动后台计时
            self._start_timer()

    def _create_window(self, pet_x, pet_y, pet_w, pet_h):
        """创建极简进度条窗口（仅在 visible=True 时调用）"""
        self.win = tk.Toplevel(self.parent)
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        self.win.wm_attributes("-transparentcolor", "#F0F0F0")
        self.win.configure(bg="#F0F0F0")
        bw, bh = 300, 80
        self.pos_x = pet_x + (pet_w - bw) // 2
        self.pos_y = pet_y + pet_h + 16
        self.win.geometry(f"{bw}x{bh}+{self.pos_x}+{self.pos_y}")

        tk.Label(self.win, text=self.title, font=("Segoe UI", 12, "bold"),
                 fg="#1A1A1A", bg="#F0F0F0").pack(pady=(8, 0))
        self.bar = tk.Canvas(self.win, width=240, height=4, bg="#E5E5E5", highlightthickness=0)
        self.bar.pack(pady=8)

        btn_frame = tk.Frame(self.win, bg="#F0F0F0")
        btn_frame.pack()
        tk.Button(btn_frame, text="中止", command=self.cancel,
                  font=("Segoe UI", 12), fg="#000000", bg="#FFFFFF",
                  bd=1, relief="solid", activebackground="#F5F5F5").pack(side=tk.LEFT, padx=8)

        # 启动刷新循环
        self._update()

    def _start_timer(self):
        """无窗口模式的后台计时"""
        def tick():
            if self.cancelled:
                return
            if self.elapsed >= self.duration:
                self.finish()
                return
            self.elapsed += self.step
            if self.parent:
                self.parent.after(100, tick)
        if self.parent:
            self.parent.after(100, tick)

    def _update(self):
        if not self.win or not self.win.winfo_exists():
            return
        if self.cancelled:
            return
        if self.elapsed >= self.duration:
            self.finish()
            return
        self.elapsed += self.step
        pct = min(100, self.elapsed / self.duration * 100)
        self.bar.delete("all")
        self.bar.create_rectangle(0, 0, 240 * pct / 100, 4, fill="#000000", outline="")
        self.win.after(100, self._update)

    def cancel(self):
        self.cancelled = True
        if self.win:
            self.win.destroy()
        if self.on_cancel:
            self.on_cancel()

    def finish(self):
        if self.cancelled:
            return
        if self.win:
            self.win.destroy()
        if self.on_finish:
            self.on_finish()

    def get_progress(self):
        """返回进度百分比和剩余时间描述"""
        if self.duration <= 0:
            return 0, "即将完成"
        pct = min(100, int(self.elapsed / self.duration * 100))
        remaining = max(0, self.duration - self.elapsed)
        rem_sec = int(remaining)
        if rem_sec >= 60:
            rem_text = f"{rem_sec // 60}分{rem_sec % 60}秒"
        else:
            rem_text = f"{rem_sec}秒"
        return pct, rem_text

    def move_to(self, x, y):
        """窗口跟随宠物移动（如果窗口存在）"""
        if self.win:
            self.pos_x = x + (self.parent.winfo_width() - 280) // 2
            self.pos_y = y + self.parent.winfo_height() + 10
            self.win.geometry(f"+{self.pos_x}+{self.pos_y}")
