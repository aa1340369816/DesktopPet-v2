import tkinter as tk
import time

class StatusWindow:
    def __init__(self, parent, pet_state):
        self.win = tk.Toplevel(parent)
        self.win.title("练习生状态")
        self.win.geometry("300x500")
        self.pet_state = pet_state
        self.build()

    def build(self):
        for w in self.win.winfo_children():
            w.destroy()
        s = self.pet_state
        now = time.localtime()
        weekday_map = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        real_time_str = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d} {weekday_map[now.tm_wday]} {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        tk.Label(self.win, text=f"🕒 {real_time_str}", font=("微软雅黑", 10, "bold")).pack(pady=5)
        tk.Label(self.win, text=s.game_time.get_time_str(), font=("微软雅黑", 9), fg="gray").pack()
        tk.Label(self.win, text=f"身份：{s.stage_name} (路线{'公开' if s.route==1 else '未公开' if s.route==2 else '未定'})",
                 font=("微软雅黑", 10)).pack()
        tk.Label(self.win, text=f"⭐等级 {s.level}   💰金币 {s.gold}", font=("微软雅黑", 10)).pack()
        play_sec = int(s.total_playtime)
        play_str = f"{play_sec // 3600}小时{(play_sec % 3600) // 60}分钟"
        tk.Label(self.win, text=f"⏱️ 陪伴时长：{play_str}", font=("微软雅黑", 10)).pack()
        tk.Label(self.win, text=f"❤️ 健康度：{s.health}/100", font=("微软雅黑", 10)).pack()
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
            tk.Label(self.win, text=attr, font=("微软雅黑", 10)).pack(anchor="w", padx=10)

    def refresh(self):
        """重新绘制面板内容，保留窗口位置"""
        if self.win.winfo_exists():
            self.build()
