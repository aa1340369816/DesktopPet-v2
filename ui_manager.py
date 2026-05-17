import tkinter as tk


class UIManager:
    def __init__(self, pet):
        self.pet = pet

    def show_narrative_window(self, text, title=""):
        win = tk.Toplevel(self.pet.pet_win)
        win.overrideredirect(True)
        win.wm_attributes("-topmost", True)
        win.configure(bg="#FFFFFF")
        win.attributes("-alpha", 1.0)

        w = 340
        temp_label = tk.Label(win, text=text, font=("Segoe UI", 10),
                              fg="#404040", bg="#FFFFFF", wraplength=300, justify="left")
        win.update_idletasks()
        req_height = temp_label.winfo_reqheight()
        temp_label.destroy()

        title_height = 32 if title else 0
        btn_height = 42
        pad_total = 56
        h = req_height + title_height + btn_height + pad_total
        if h < 160:
            h = 160
        if h > 420:
            h = 420

        # 位置更新函数（实时跟随用）
        def update_position():
            if win.winfo_exists():
                x = self.pet.x + (self.pet.pet_w - w) // 2
                y = self.pet.y - h - 12
                if y < 0:
                    y = self.pet.y + self.pet.pet_h + 12
                win.geometry(f"{w}x{h}+{x}+{y}")

        # 初始定位
        update_position()

        if title:
            title_label = tk.Label(win, text=title, font=("Segoe UI", 12, "bold"),
                                   fg="#000000", bg="#FFFFFF")
            title_label.pack(pady=(20, 0))
            sep = tk.Frame(win, height=1, bg="#E5E5E5")
            sep.pack(fill="x", padx=20, pady=(12, 0))

        desc_label = tk.Label(win, text=text, font=("Segoe UI", 10),
                              fg="#404040", bg="#FFFFFF", wraplength=300, justify="left")
        desc_label.pack(pady=(16, 0), padx=20)

        # 关闭窗口时取消注册
        def on_close():
            self.pet.unregister_follow_window(win)
            win.destroy()

        close_btn = tk.Button(win, text="我知道了", font=("Segoe UI", 10),
                              fg="#000000", bg="#FFFFFF", activebackground="#F5F5F5",
                              bd=1, relief="solid",
                              padx=12, pady=6,
                              command=on_close)
        close_btn.pack(pady=16)

        auto_close_ms = int(max(3000, min(12000, len(text) * 250)))
        def auto_close():
            if win.winfo_exists():
                on_close()
        win.after(auto_close_ms, auto_close)

        # 注册实时跟随
        self.pet.register_follow_window(win, update_position)

    def show_toast(self, msg, duration=1500):
        if hasattr(self, 'toast_win') and self.toast_win and self.toast_win.winfo_exists():
            self.toast_win.destroy()
        self.pet.pet_win.update_idletasks()
        toast = tk.Toplevel(self.pet.root)
        toast.overrideredirect(True)
        toast.wm_attributes("-topmost", True)
        toast.configure(bg="#FFFFFF", highlightbackground="#CCCCCC", highlightthickness=1)
        tk.Label(toast, text=msg, fg="#1A1A1A", bg="#FFFFFF",
                 font=("Segoe UI", 12), padx=16, pady=8).pack()
        toast.update_idletasks()

        def update_position():
            if toast.winfo_exists():
                x = self.pet.x + self.pet.pet_w + 16
                y = self.pet.y + 16
                toast.geometry(f"+{x}+{y}")

        update_position()
        self.pet.active_notifications.append(toast)
        self.pet.register_follow_window(toast, update_position)

        def destroy_toast():
            if toast.winfo_exists():
                self.pet.unregister_follow_window(toast)
                if toast in self.pet.active_notifications:
                    self.pet.active_notifications.remove(toast)
                toast.destroy()
        toast.after(duration, destroy_toast)
        self.toast_win = toast

    def show_float_text(self, texts):
        base_x = self.pet.x + self.pet.pet_w // 2
        base_y = self.pet.y - 24
        for i, text in enumerate(texts):
            offset_x = (i % 3 - 1) * 48
            offset_y = -(i // 3) * 32
            win = tk.Toplevel(self.pet.pet_win)
            win.overrideredirect(True)
            win.wm_attributes("-topmost", True)
            win.wm_attributes("-transparentcolor", "#F0F0F0")
            win.configure(bg="#F0F0F0")
            label = tk.Label(win, text=text, font=("Segoe UI", 16, "normal"),
                             fg="#0066FF", bg="#F0F0F0")
            label.pack()
            win.geometry(f"+{base_x + offset_x}+{base_y + offset_y}")
            self._animate_float(win, 0)

    def _animate_float(self, win, step):
        if not win.winfo_exists():
            return
        if step >= 40:
            win.destroy()
            return
        x = win.winfo_x()
        y = win.winfo_y() - 1
        alpha = 1.0 - step / 40
        win.wm_attributes("-alpha", alpha)
        win.geometry(f"+{x}+{y}")
        self.pet.root.after(50, lambda: self._animate_float(win, step + 1))

    def show_info(self, msg):
        self.pet.pet_win.update_idletasks()
        popup = tk.Toplevel(self.pet.root)
        popup.overrideredirect(True)
        popup.wm_attributes("-topmost", True)
        popup.configure(bg="#FFFFFF", highlightbackground="#CCCCCC", highlightthickness=1)
        tk.Label(popup, text=msg, fg="#1A1A1A", bg="#FFFFFF",
                 font=("Segoe UI", 12), padx=24, pady=16).pack()
        popup.update_idletasks()

        def update_position():
            if popup.winfo_exists():
                x = self.pet.x + self.pet.pet_w + 16
                y = self.pet.y + 16
                popup.geometry(f"+{x}+{y}")

        update_position()
        self.pet.active_notifications.append(popup)
        self.pet.register_follow_window(popup, update_position)

        def destroy_popup():
            if popup.winfo_exists():
                self.pet.unregister_follow_window(popup)
                if popup in self.pet.active_notifications:
                    self.pet.active_notifications.remove(popup)
                popup.destroy()
        popup.after(2000, destroy_popup)
