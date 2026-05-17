import tkinter as tk
import time

class StatusWindow:
    def __init__(self, parent, pet_state):
        self.win = tk.Toplevel(parent)
        self.win.title("练习生状态")
        self.win.geometry("320x560")
        self.win.configure(bg="#FFFFFF")
        self.pet_state = pet_state
        self.build()

    def build(self):
        for w in self.win.winfo_children():
            w.destroy()
        s = self.pet_state
        now = time.localtime()
        weekday_map = ["周一","周二","周三","周四","周五","周六","周日"]
        real_time_str = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {weekday_map[now.tm_wday]} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"

        # 标题
        tk.Label(self.win, text="练习生状态", font=("Segoe UI", 14, "bold"),
                 fg="#000000", bg="#FFFFFF").pack(pady=(24,0))
        # 分隔线
        tk.Frame(self.win, height=1, bg="#E5E5E5").pack(fill="x", padx=24, pady=(16,0))

        # 信息区
        info_frame = tk.Frame(self.win, bg="#FFFFFF")
        info_frame.pack(pady=16, padx=24, fill="x")

        # 现实时间
        tk.Label(info_frame, text=f"🕒 {real_time_str}", font=("Segoe UI", 10),
                 fg="#404040", bg="#FFFFFF", anchor="w").pack(fill="x", pady=2)

        # 身份 / 等级 / 金币
        tk.Label(info_frame, text=f"身份：{s.stage_name} (路线{'公开' if s.route==1 else '未公开' if s.route==2 else '未定'})",
                 font=("Segoe UI", 12), fg="#404040", bg="#FFFFFF", anchor="w").pack(fill="x", pady=4)
        tk.Label(info_frame, text=f"⭐等级 {s.level}   💰金币 {s.gold}",
                 font=("Segoe UI", 12), fg="#404040", bg="#FFFFFF", anchor="w").pack(fill="x", pady=4)

        # 健康
        tk.Label(info_frame, text=f"❤️ 健康度：{s.health}/100",
                 font=("Segoe UI", 12), fg="#404040", bg="#FFFFFF", anchor="w").pack(fill="x", pady=4)

        # 其他属性
        attrs = [
            f"🍖饱食 {int(s.satiety)}/100     😊心情 {int(s.mood)}/100",
            f"⚡体力 {int(s.stamina)}/100     🧹清洁 {int(s.hygiene)}/100",
            f"😫疲劳 {int(s.fatigue)}     🏥 {'🤒生病' if s.sick else '😄健康'}",
            f"🎤唱功 {int(s.vocal)}     💃舞蹈 {int(s.dance)}",
            f"🎭演技 {int(s.acting)}     🎪综艺 {int(s.variety)}",
            f"✨魅力 {int(s.charm)}     📈人气 {int(s.popularity)}",
            f"👥粉丝 {int(s.fans)}"
        ]
        for attr in attrs:
            tk.Label(info_frame, text=attr, font=("Segoe UI", 12),
                     fg="#404040", bg="#FFFFFF", anchor="w", justify="left").pack(fill="x", pady=4)

    def refresh(self):
        if self.win.winfo_exists():
            self.build()
            self.win.update_idletasks()
