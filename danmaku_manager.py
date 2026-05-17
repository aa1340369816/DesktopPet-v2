import random
import tkinter as tk


class DanmakuManager:
    def __init__(self, pet):
        self.pet = pet

    def show_danmu(self):
        s = self.pet.state
        pool = []
        if s.stage >= 3:
            pool += ["昨天梦到拿一位了…","记得给妈妈打电话","舞台上的灯光好美"]
        if s.mood > 70:
            pool += ["今天心情真好！","感觉状态超级棒！"]
        elif s.mood < 30:
            pool += ["好难过…","不想训练…"]
        if s.fatigue > 60:
            pool += ["好累…","今晚一定要早点睡"]
        if s.satiety < 30:
            pool += ["好饿…","想吃炸鸡"]
        pool += ["想喝奶茶…","今天状态不错！","再练一遍","我会出道的吧？","想家了…"]
        text = random.choice(pool) if pool else "加油！"
        if self.pet.danmu_win and self.pet.danmu_win.winfo_exists():
            self.pet.danmu_win.destroy()
        danmu = tk.Toplevel(self.pet.pet_win)
        danmu.overrideredirect(True)
        danmu.wm_attributes("-topmost", True)
        danmu.wm_attributes("-alpha", 0.8)
        danmu.configure(bg="black")
        danmu.geometry(f"+{self.pet.x}+{self.pet.y}")
        tk.Label(danmu, text=text, fg="white", bg="black", font=("微软雅黑", 9), padx=5, pady=2).pack()
        self.pet.danmu_win = danmu
        self.animate_danmu(0)

    def animate_danmu(self, step=0):
        if step > 40 or not self.pet.danmu_win or not self.pet.danmu_win.winfo_exists():
            if self.pet.danmu_win:
                self.pet.danmu_win.destroy()
                self.pet.danmu_win = None
            return
        base_x = self.pet.x + self.pet.pet_w // 2
        base_y = self.pet.y - 10
        offset_x = step * 2
        offset_y = step * 1
        x = base_x - offset_x
        y = base_y - offset_y
        self.pet.danmu_win.geometry(f"+{x}+{y}")
        if step > 20:
            alpha = max(0.2, 0.8 - (step - 20) * 0.03)
        else:
            alpha = 0.8
        self.pet.danmu_win.wm_attributes("-alpha", alpha)
        self.pet.root.after(100, lambda: self.animate_danmu(step + 1))
