import tkinter as tk
import random

class PerformanceWindow:
    def __init__(self, parent, pet_state, act_type, act_sub, callback,
                 pet_x, pet_y, pet_w=160, pet_h=220):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        self.win.wm_attributes("-transparentcolor", "#F0F0F0")
        self.win.configure(bg="#F0F0F0")
        bw, bh = 300, 80
        self.pet_w = pet_w
        self.pet_h = pet_h
        self.pos_x = pet_x + (pet_w - bw) // 2
        self.pos_y = pet_y + pet_h + 16
        self.win.geometry(f"{bw}x{bh}+{self.pos_x}+{self.pos_y}")
        titles = {("train","voice"):"🎤 声乐课", ("train","fitness"):"💃 舞蹈集训",
                  ("train","expression"):"🎭 表演工作坊", ("train","shape"):"🏋️ 形体管理",
                  ("schedule",""):"📺 通告"}
        title = titles.get((act_type,act_sub),"活动中")
        tk.Label(self.win, text=title, font=("Segoe UI", 12, "bold"),
                 fg="#1A1A1A", bg="#F0F0F0").pack(pady=(8,0))

        self.bar = tk.Canvas(self.win, width=250, height=4, bg="#E5E5E5", highlightthickness=0)
        self.bar.pack(pady=8)
        self.time_label = tk.Label(self.win, text="", font=("Segoe UI", 10),
                                   fg="#808080", bg="#F0F0F0")
        self.time_label.pack()

        self.pet_state = pet_state
        self.act_type = act_type
        self.act_sub = act_sub
        self.callback = callback
        if act_type=="train":
            base = random.randint(45*60,60*60) if act_sub!="shape" else 40*60
            base += random.randint(-5*60,5*60)
            self.duration = max(10,base)
            self.game_hours = random.randint(3,4) if act_sub!="shape" else 2.5
        else:
            base = random.randint(60*60,90*60)
            base += random.randint(-5*60,5*60)
            self.duration = max(10,base)
            self.game_hours = random.randint(4,6)
        self.elapsed=0; self.step=1; self.event_triggered=False
        self.event_modifier=1.0; self.event_msg=""; self.extra_dur=0
        self.update()

    def update(self):
        if not self.win.winfo_exists():
            return
        if self.elapsed >= self.duration+self.extra_dur:
            self.finish()
            return
        if not self.event_triggered and self.elapsed >= self.duration//2:
            self.event_triggered = True
            r = random.random()
            if self.act_type=="train":
                if r<0.2:
                    self.extra_dur=-random.randint(5*60,15*60); self.event_modifier=1.1; self.event_msg="提前下课！"
                elif r<0.4:
                    self.extra_dur=random.randint(10*60,20*60); self.event_modifier=0.9; self.event_msg="加练……"
            else:
                if r<0.2:
                    self.extra_dur=-random.randint(10*60,20*60); self.event_modifier=1.1; self.event_msg="提前收工！"
                elif r<0.4:
                    self.extra_dur=random.randint(15*60,30*60); self.event_modifier=0.9; self.event_msg="加戏……"
            if self.event_msg:
                self.time_label.config(text=self.time_label.cget("text")+f" ({self.event_msg})")
        self.elapsed += self.step
        total = self.duration+self.extra_dur
        pct = min(100, self.elapsed/total*100)
        self.bar.delete("all")
        self.bar.create_rectangle(0,0,250*pct/100,4,fill="#000000",outline="")
        rem = max(0, total-self.elapsed)
        self.time_label.config(text=f"剩余 {rem//60:02d}:{rem%60:02d}")
        self.win.after(1000, self.update)

    def finish(self):
        self.pet_state.game_time.advance_hours(self.game_hours)
        if self.act_type=="train":
            msg = self.pet_state.apply_train_result(self.act_sub, modifier=self.event_modifier, extra_msg=self.event_msg)
        else:
            msg = self.pet_state.apply_schedule_result(modifier=self.event_modifier, extra_msg=self.event_msg)
        self.win.destroy()
        if self.callback:
            self.callback(msg)

    def move_to(self, x, y):
        self.pos_x = x + (self.pet_w-300)//2
        self.pos_y = y + self.pet_h + 16
        self.win.geometry(f"+{self.pos_x}+{self.pos_y}")
