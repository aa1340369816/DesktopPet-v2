import tkinter as tk
from tkinter import messagebox
import time
import random


class AdventureStageWindow:
    """奇遇叙事窗口（极简白底黑字，分页显示，选项在最后，高度固定）"""
    def __init__(self, parent, adventure_name, stage_text, options, callback, pet_x, pet_y, pet_w, pet_h, is_trigger=False):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        bg_color = "#FFF8E1" if is_trigger else "#FFFFFF"
        self.win.configure(bg=bg_color)
        self.win.attributes("-alpha", 1.0)

        self.w = 400
        self.pad = 20
        self.callback = callback
        self.options = options
        self.current_page = 0

        # 按 \n 分割原始文本，每 6 个非空段落为一页
        raw_paragraphs = stage_text.split('\n')
        paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]
        if not paragraphs:
            paragraphs = ["（剧情缺失）"]

        self.text_pages = []
        for i in range(0, len(paragraphs), 6):
            self.text_pages.append(paragraphs[i:i+6])

        self.has_options = bool(options)
        self.total_pages = len(self.text_pages) + (1 if self.has_options else 0)

        # 标题
        tk.Label(self.win, text=adventure_name, font=("Segoe UI", 12, "bold"),
                 fg="#000000", bg=bg_color).pack(pady=(self.pad, 0))
        tk.Frame(self.win, height=1, bg="#E5E5E5").pack(fill="x", padx=self.pad, pady=(8, 0))

        # 内容区域
        self.content_frame = tk.Frame(self.win, bg=bg_color)
        self.content_frame.pack(pady=(12, 0), padx=self.pad, fill="x")
        self.content_widgets = []

        # 按钮区域
        self.btn_frame = tk.Frame(self.win, bg=bg_color)
        self.btn_frame.pack(pady=12, padx=self.pad, fill="x")

        self.pet_x = pet_x
        self.pet_y = pet_y
        self.pet_w = pet_w
        self.pet_h = pet_h

        # 固定窗口高度，杜绝按钮挤压
        self.fixed_h = 420
        self._show_page(0)
        x = pet_x + (pet_w - self.w) // 2
        y = pet_y - self.fixed_h - 12
        if y < 0:
            y = pet_y + pet_h + 12
        self.win.geometry(f"{self.w}x{self.fixed_h}+{x}+{y}")
        self._follow()

    def _show_page(self, page_idx):
        for w in self.content_widgets:
            w.destroy()
        self.content_widgets.clear()
        for w in self.btn_frame.winfo_children():
            w.destroy()

        if page_idx < len(self.text_pages):
            # 文本页
            for paragraph in self.text_pages[page_idx]:
                lbl = tk.Label(self.content_frame, text=paragraph, font=("Segoe UI", 10),
                               fg="#404040", bg=self.win.cget("bg"),
                               anchor="w", justify="left", wraplength=360)
                lbl.pack(fill="x", pady=2)
                self.content_widgets.append(lbl)

            if page_idx < self.total_pages - 1:
                next_text = "继续 ▶"
                next_cmd = self._next_page
            else:
                next_text = "结束"
                next_cmd = self.win.destroy

            tk.Button(self.btn_frame, text=next_text, font=("Segoe UI", 12),
                      fg="#000000", bg="#FFFFFF", activebackground="#F5F5F5",
                      bd=1, relief="solid", padx=12, pady=14,
                      command=next_cmd).pack(side="left", padx=4)

            tk.Button(self.btn_frame, text="关闭", font=("Segoe UI", 12),
                      fg="#808080", bg="#FFFFFF", activebackground="#F5F5F5",
                      bd=1, relief="solid", padx=12, pady=14,
                      command=self.win.destroy).pack(side="right", padx=4)

        else:
            # 选项页
            tk.Label(self.content_frame, text="请做出你的选择：", font=("Segoe UI", 10, "bold"),
                     fg="#000000", bg=self.win.cget("bg")).pack(anchor="w", pady=(0, 8))
            self.content_widgets.append(self.content_frame.winfo_children()[-1])

            for i, opt in enumerate(self.options):
                tk.Button(self.btn_frame, text=opt["text"], font=("Segoe UI", 12),
                          fg="#000000", bg="#FFFFFF", activebackground="#F5F5F5",
                          bd=1, relief="solid", padx=12, pady=14,
                          command=lambda idx=i: self._choose(idx)).pack(fill="x", pady=4)

            tk.Button(self.btn_frame, text="取消", font=("Segoe UI", 12),
                      fg="#808080", bg="#FFFFFF", activebackground="#F5F5F5",
                      bd=1, relief="solid", padx=12, pady=14,
                      command=self.win.destroy).pack(pady=(8, 0))

        self.current_page = page_idx

    def _next_page(self):
        if self.current_page < self.total_pages - 1:
            self._show_page(self.current_page + 1)
        else:
            self.win.destroy()

    def _choose(self, idx):
        result_text = self.options[idx].get("result", "") if isinstance(self.options[idx], dict) else ""
        if result_text:
            for w in self.content_widgets:
                w.destroy()
            self.content_widgets.clear()
            for w in self.btn_frame.winfo_children():
                w.destroy()
            tk.Label(self.content_frame, text=result_text, font=("Segoe UI", 10),
                     fg="#404040", bg=self.win.cget("bg"),
                     anchor="w", justify="left", wraplength=360).pack(fill="x", pady=2)
            tk.Button(self.btn_frame, text="继续", font=("Segoe UI", 12),
                      fg="#000000", bg="#FFFFFF", activebackground="#F5F5F5",
                      bd=1, relief="solid", padx=12, pady=8,
                      command=lambda: self._finish_choice(idx)).pack(side="right", padx=4)
        else:
            self._finish_choice(idx)

    def _finish_choice(self, idx):
        self.win.destroy()
        if self.callback:
            self.callback(idx)

    def _follow(self):
        if self.win.winfo_exists():
            nx = self.pet_x + (self.pet_w - 400) // 2
            ny = self.pet_y - self.fixed_h - 12
            if ny < 0:
                ny = self.pet_y + self.pet_h + 12
            self.win.geometry(f"+{nx}+{ny}")
            self.win.after(200, self._follow)


class AdventureManager:
    # ... 以下 AdventureManager 类保持不变，和你现有的完全相同，此处省略以节省篇幅 ...
    # 请确保你现有的 AdventureManager 类内容不变，只需替换上面的 AdventureStageWindow 即可。
