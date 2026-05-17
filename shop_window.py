import tkinter as tk
from tkinter import ttk

class ShopWindow:
    def __init__(self, parent, pet_state, buy_callback=None):
        self.win = tk.Toplevel(parent)
        self.win.title("练习生百货")
        self.win.geometry("480x640")
        self.win.configure(bg="#FFFFFF")
        self.pet_state = pet_state
        self.buy_callback = buy_callback

        # 顶栏
        header = tk.Frame(self.win, bg="#FFFFFF")
        header.pack(fill="x", padx=24, pady=(24,0))
        tk.Label(header, text="练习生百货", font=("Segoe UI", 14, "bold"),
                 fg="#000000", bg="#FFFFFF").pack(side="left")
        self.gold_label = tk.Label(header, text=f"💰 {self.pet_state.gold}金币",
                                   font=("Segoe UI", 12), fg="#404040", bg="#FFFFFF")
        self.gold_label.pack(side="right")
        tk.Frame(self.win, height=1, bg="#E5E5E5").pack(fill="x", padx=24, pady=(16,0))

        self.notebook = ttk.Notebook(self.win)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)
        cats = ["🍽️ 能量补给", "✨ 洁护管理", "📚 自我提升", "👗 造型衣橱", "🎁 社交礼物", "⚡ 便捷服务"]
        for i, cat in enumerate(cats):
            frame = tk.Frame(self.notebook, bg="#FFFFFF")
            self.notebook.add(frame, text=cat)
            self.build_category(frame, i)

    def build_category(self, parent, cat_idx):
        canvas = tk.Canvas(parent, width=440, height=460, bg="#FFFFFF", highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#FFFFFF")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        items = self.get_items(cat_idx)
        # 直接铺开，不再分子组
        for i, (display_name, price, eff, desc) in enumerate(items):
            card = tk.Frame(scroll_frame, bg="#FFFFFF", bd=1, relief="solid",
                            highlightbackground="#E5E5E5", highlightthickness=1)
            card.pack(fill="x", pady=4, padx=4)
            tk.Label(card, text=display_name, font=("Segoe UI", 12, "bold"),
                     fg="#1A1A1A", bg="#FFFFFF").pack(anchor="w", padx=16, pady=(12,0))
            if eff:
                tk.Label(card, text=eff, font=("Segoe UI", 10), fg="#404040", bg="#FFFFFF").pack(anchor="w", padx=16)
            if desc:
                tk.Label(card, text=desc, font=("Segoe UI", 10), fg="#808080", bg="#FFFFFF",
                         wraplength=300).pack(anchor="w", padx=16)
            btn_frame = tk.Frame(card, bg="#FFFFFF")
            btn_frame.pack(anchor="e", padx=16, pady=(4,12))
            if price == 0:
                btn = tk.Button(btn_frame, text="免费", font=("Segoe UI", 12),
                                fg="#000000", bg="#FFFFFF", bd=1, relief="solid",
                                activebackground="#F5F5F5",
                                command=lambda d=display_name,p=price: self.buy(d,p))
            else:
                btn = tk.Button(btn_frame, text=f"购买 {price}G", font=("Segoe UI", 12),
                                fg="#000000", bg="#FFFFFF", bd=1, relief="solid",
                                activebackground="#F5F5F5",
                                command=lambda d=display_name,p=price: self.buy(d,p))
            btn.pack(side=tk.RIGHT)

    def buy(self, display_name, price):
        s = self.pet_state
        clean_name = display_name.split(' ', 1)[1] if ' ' in display_name else display_name
        if price > 0 and s.gold < price:
            self.show_error("金币不足！")
            return
        if price > 0:
            s.gold -= price
        s.inventory[clean_name] = s.inventory.get(clean_name, 0) + 1
        self.refresh_gold()
        if self.buy_callback:
            self.buy_callback(clean_name, price)
        self.show_info(f"已购买 {clean_name}")

    def refresh_gold(self):
        self.gold_label.config(text=f"💰 {self.pet_state.gold}金币")

    def show_error(self, msg):
        top = tk.Toplevel(self.win)
        top.title("提示")
        top.configure(bg="#FFFFFF")
        tk.Label(top, text=msg, font=("Segoe UI", 12), fg="#FF0000", bg="#FFFFFF").pack(padx=24, pady=16)
        tk.Button(top, text="确定", font=("Segoe UI", 12), fg="#000000", bg="#FFFFFF",
                  bd=1, relief="solid", activebackground="#F5F5F5", command=top.destroy).pack(pady=8)

    def show_info(self, msg):
        top = tk.Toplevel(self.win)
        top.title("提示")
        top.configure(bg="#FFFFFF")
        tk.Label(top, text=msg, font=("Segoe UI", 12), fg="#1A1A1A", bg="#FFFFFF").pack(padx=24, pady=16)
        tk.Button(top, text="确定", font=("Segoe UI", 12), fg="#000000", bg="#FFFFFF",
                  bd=1, relief="solid", activebackground="#F5F5F5", command=top.destroy).pack(pady=8)

    def get_items(self, idx):
        # 数据与原版完全一致，这里只展示结构，内容保持不变
        # 你原有的 items 列表直接保留
        if idx == 0:
            return [
                ("🥑 超级食物碗", 12, "🍖+30 ⚡+5 20s", "羽衣甘蓝打底，奇亚籽点缀。"),
                # ... 其余物品
            ]
        # ... 其他分类
        return []
