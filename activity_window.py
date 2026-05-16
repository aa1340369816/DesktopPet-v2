import tkinter as tk

class ActivityWindow:
    def __init__(self, parent, title, duration, on_finish, on_cancel=None,
                 pet_x=0, pet_y=0, pet_w=160, pet_h=220):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        self.win.wm_attributes("-transparentcolor", "#F0F0F0")
        self.win.configure(bg="#F0F0F0")
        bw, bh = 280, 80
        self.pos_x = pet_x + (pet_w - bw) // 2
        self.pos_y = pet_y + pet_h + 10
        self.win.geometry(f"{bw}x{bh}+{self.pos_x}+{self.pos_y}")
        tk.Label(self.win, text=title, font=("微软雅黑", 10, "bold"),
                 fg="black", bg="#F0F0F0").pack()
        self.bar = tk.Canvas(self.win, width=200, height=15, bg="white",
                             highlightthickness=0)
        self.bar.pack(pady=5)
        btn_frame = tk.Frame(self.win, bg="#F0F0F0")
        btn_frame.pack()
        tk.Button(btn_frame, text="中止", command=self.cancel, bg="#ff4d4d",
                  fg="white", font=("微软雅黑", 8)).pack(side=tk.LEFT, padx=5)
        self.on_finish = on_finish
        self.on_cancel = on_cancel
        self.duration = duration
        self.elapsed = 0
        self.step = 0.1
        self.cancelled = False
        self.update()

    def update(self):
        if not self.win.winfo_exists():
            return
        if self.cancelled:
            return
        if self.elapsed >= self.duration:
            self.finish()
            return
        self.elapsed += self.step
        pct = min(100, self.elapsed / self.duration * 100)
        self.bar.delete("all")
        self.bar.create_rectangle(0, 0, 200 * pct / 100, 15,
                                  fill="#4CAF50", outline="")
        self.win.after(100, self.update)

    def cancel(self):
        self.cancelled = True
        self.win.destroy()
        if self.on_cancel:
            self.on_cancel()

    def finish(self):
        if self.cancelled:
            return
        self.win.destroy()
        if self.on_finish:
            self.on_finish()