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
        # 外层容器使用 Frame 来管理 Canvas 和 Scrollbar
        outer = tk.Frame(parent, bg="#FFFFFF")
        outer.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(outer, bg="#FFFFFF", highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#FFFFFF")

        # 关键：让 scroll_frame 自动扩展宽度，并更新滚动区域
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        items = self.get_items(cat_idx)
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
        # 数据保持不变，你原有物品列表完整复制到各个分类
        if idx == 0:
            return [
                ("🥑 超级食物碗", 12, "🍖+30 ⚡+5 20s", "羽衣甘蓝打底，奇亚籽点缀。"),
                ("🍣 波奇饭便当", 22, "🍖+40 ⚡+8 😊+5 25s", "三文鱼+牛油果，偷偷带进练习室。"),
                ("🥤 绿色排毒果汁", 15, "🍖+15 消除水肿 15s", "一口下去感觉自己变轻了。"),
                ("🥩 牛肉沙拉碗", 28, "🍖+55 ⚡+10 😊+8 35s", "高蛋白低碳水，练完舞来一碗刚好。"),
                ("🍲 泡菜豆腐锅", 20, "🍖+50 ⚡+5 😊+10 40s", "热乎乎辣得刚好，吃完出汗感觉排毒。"),
                ("🍜 荞麦冷面", 18, "🍖+45 ⚡+5 😊+5 30s", "夏天练习室没空调时的救赎。"),
                ("☕ 冰美式", 15, "🍖+5 ⚡+15 消除困倦 15s", "不喝冰美式的练习生不是合格打工人。"),
                ("🍵 抹茶燕麦拿铁", 25, "🍖+10 ⚡+5 😊+20 20s", "魅力+3(半天)，无糖也能喝出高级感。"),
                ("🧋 燕麦拿铁", 22, "🍖+15 ⚡+8 😊+25 20s", "植物奶替代，无糖但心里甜。"),
                ("🫧 气泡冷萃", 20, "🍖+5 ⚡+20 😊+10 15s", "咖啡因+气泡，提神醒脑双重暴击。"),
                ("🍙 三角饭团", 8, "🍖+25 ⚡+3 10s", "便利店的最后救赎，便宜管饱。"),
                ("🍌 能量香蕉", 5, "🍖+15 ⚡+8 8s", "最快充能，没有之一。"),
            ]
        elif idx == 1:
            return [
                ("💄 唇膜", 8, "✨+5 😊+8 15s", ""),
                ("👁️ 眼膜", 10, "✨+6 消除疲惫 20s", ""),
                ("🧖 清洁泥膜", 12, "🧹+30 ✨+8 25s", ""),
                ("💧 补水面膜", 15, "✨+10 😊+8 30s", ""),
                ("🌿 面部刮痧", 18, "✨+12 😊+5 消除水肿 35s", ""),
                ("🧴 精华导入", 25, "🧹+10 ✨+15 40s", ""),
                ("✨ 一键精致护理", 40, "🧹+40 ✨+20 😊+15 60s", "泥膜→面膜→精华，省12金币"),
                ("🧖 汗蒸排毒", 22, "🧹+70 😊+10 ✨+8 45s", ""),
                ("💆 全身按摩", 35, "⚡+40 😊+30 50s", ""),
                ("🕯️ 香薰水疗", 45, "🧹+100 ⚡+10 😊+40 ✨+12 60s", ""),
            ]
        elif idx == 2:
            return [
                ("🎧 降噪耳机", 60, "声乐训练+25%", "隔绝世界，只听自己的声音。"),
                ("👟 联名舞鞋", 60, "舞蹈训练+25%", "穿上感觉能多转三圈。"),
                ("🎬 演技拆解课", 60, "表演训练+25%", "教你读懂镜头的语言。"),
                ("🧘 正念冥想课", 55, "😊+50 消除焦虑", "呼吸，然后继续发光。"),
                ("📱 直拍复盘", 250, "随机才华+100", "逐帧分析，连表情管理都不放过。"),
                ("📖 《偶像的品格》", 500, "✨+20 人气获取+5%", "写给想认真做偶像的人。"),
                ("🤖 AI舞蹈评分", 120, "舞蹈训练+35%", "科技赋能，每个角度都被审视。"),
            ]
        elif idx == 3:
            return [
                ("👕 OVERSIZE卫衣", 80, "✨+3 心情消耗-10%", "偷懒穿搭也是时尚。"),
                ("🧥 长款风衣", 120, "✨+5 雨天额外+8", "氛围感拿捏住了。"),
                ("🎽 复古运动套装", 130, "舞蹈+5% 体力消耗-5%", "90年代复古回潮。"),
                ("🩰 芭蕾核训练服", 150, "舞蹈+3% ✨+5", "把杆上的优雅。"),
                ("✨ 打歌舞台定制装", 400, "✨+15 人气获取+10%", "灯光下的C位。"),
                ("🖤 暗黑概念装", 350, "✨+12 综艺感+8", "概念消化力就是表现力。"),
                ("👑 颁奖典礼高定", 500, "✨+25 全属性+5", "红毯即战场。"),
                ("🎭 周年限定皮肤", 500, "✨+20 特殊互动动画", "感谢你陪我走过。"),
            ]
        elif idx == 4:
            return [
                ("💐 手写应援信", 30, "好感+15", "一笔一画都是真心。"),
                ("🎂 应援咖啡车", 120, "好感+40", "给队友的生日惊喜。"),
                ("🕶️ 前辈同款墨镜", 100, "好感+30", "致敬前辈。"),
                ("🍷 手酿梅子酒", 80, "好感+35", "给制作人的心意。"),
                ("🎫 演唱会VIP席", 200, "好感+50", "共享高光时刻。"),
                ("📸 双人合照集", 250, "好感+60", "记录我们的瞬间。"),
            ]
        elif idx == 5:
            return [
                ("🎫 行程加速卡", 30, "训练/通告耗时减半", "时间管理大师。"),
                ("🔄 考核重置券", 80, "周考核可重来一次", "再来一次的机会。"),
                ("📋 自动排程助手", 50, "本周自动最优排课", "AI帮你安排。"),
                ("🌟 幸运符", 60, "当天随机事件偏向正面", "转运神器。"),
            ]
        return []
