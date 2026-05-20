import random
import time
import tkinter as tk
import tkinter.messagebox as messagebox
from activity_window import ActivityWindow
from performance_window import PerformanceWindow


def _random_talent_boost(state):
    if random.random() < 0.5:
        state.vocal += 1
    else:
        state.dance += 1


class ActionManager:
    def __init__(self, pet):
        self.pet = pet

    def cancel_current_activity(self):
        if self.pet.current_activity:
            self.pet.current_activity.cancel()
            self.pet.current_activity = None
        if self.pet.performance_win:
            self.pet.performance_win.cancel()
            self.pet.performance_win = None
        self.pet.current_activity_name = None
        self.pet.anim_manager.switch_to_idle()
        self.pet.event_scheduler.set_action(None)
        self.pet.status_panel_manager.refresh_tray_status_if_open()

    def do_part_time_job(self, job):
        if self.pet.current_activity or self.pet.performance_win:
            if not messagebox.askyesno("活动冲突", "当前有活动正在进行，是否中止并开始打工？"):
                return
            else:
                self.cancel_current_activity()

        if job == "便利店兼职":
            self.pet.anim_manager.play_action_animation("便利店兼职")
            duration = 10                              # 测试用，正常为 3600
            def effect(state):
                state.gold += 20
                state.satiety = max(0, state.satiety - 8)
                state.stamina = max(0, state.stamina - 20)
                state.hygiene = max(0, state.hygiene - 5)
                state.mood = max(0, state.mood - 3)
                state.gain_exp(5)
                self.pet.anim_manager.switch_to_idle()
        elif job == "咖啡店打工":
            self.pet.anim_manager.play_action_animation("咖啡店打工")
            duration = 3600
            def effect(state):
                state.gold += 15
                state.charm += 3
                state.satiety = max(0, state.satiety - 6)
                state.stamina = max(0, state.stamina - 15)
                state.hygiene = max(0, state.hygiene - 5)
                state.mood = max(0, state.mood - 2)
                state.gain_exp(5)
                self.pet.anim_manager.switch_to_idle()
        elif job == "快递分拣":
            duration = 5400
            def effect(state):
                state.gold += 30
                state.stamina = max(0, state.stamina - 30)
                state.satiety = max(0, state.satiety - 12)
                state.hygiene = max(0, state.hygiene - 10)
                state.mood = max(0, state.mood - 5)
                state.gain_exp(5)
        else:
            return

        self.start_activity(job, 0, duration, effect)

    def buy_training(self, course):
        s = self.pet.state
        if "进阶" in course:
            cost = 60
            gain = 15
            duration = 5400
        else:
            cost = 30
            gain = 8
            duration = 3600

        if not messagebox.askyesno("确认报名", f"是否花费 {cost} 金币报名「{course}」？"):
            return

        if s.gold < cost:
            self.pet.ui_manager.show_info("金币不足！")
            return

        if self.pet.current_activity or self.pet.performance_win:
            if not messagebox.askyesno("活动冲突", "当前有活动正在进行，是否中止并开始培训？"):
                return
            else:
                self.cancel_current_activity()

        # 播放对应培训动画（如果有）
        self.pet.anim_manager.play_action_animation(course)

        if "声乐" in course:
            attr = "vocal"
        elif "舞蹈" in course:
            attr = "dance"
        elif "表演" in course:
            attr = "acting"
        else:
            attr = None

        def effect(state):
            if attr:
                setattr(state, attr, getattr(state, attr) + gain)
            # 消耗
            if "进阶" in course:
                if "声乐" in course:
                    state.satiety = max(0, state.satiety - 12)
                    state.stamina = max(0, state.stamina - 22)
                    state.hygiene = max(0, state.hygiene - 8)
                    state.mood = max(0, state.mood - 3)
                elif "舞蹈" in course:
                    state.satiety = max(0, state.satiety - 14)
                    state.stamina = max(0, state.stamina - 28)
                    state.hygiene = max(0, state.hygiene - 12)
                    state.mood = max(0, state.mood - 4)
                else:
                    state.satiety = max(0, state.satiety - 8)
                    state.stamina = max(0, state.stamina - 15)
                    state.hygiene = max(0, state.hygiene - 5)
                    state.mood = max(0, state.mood - 2)
            else:
                if "声乐" in course:
                    state.satiety = max(0, state.satiety - 8)
                    state.stamina = max(0, state.stamina - 15)
                    state.hygiene = max(0, state.hygiene - 5)
                    state.mood = max(0, state.mood - 2)
                elif "舞蹈" in course:
                    state.satiety = max(0, state.satiety - 10)
                    state.stamina = max(0, state.stamina - 20)
                    state.hygiene = max(0, state.hygiene - 10)
                    state.mood = max(0, state.mood - 3)
                elif "表演" in course:
                    state.satiety = max(0, state.satiety - 8)
                    state.stamina = max(0, state.stamina - 15)
                    state.hygiene = max(0, state.hygiene - 5)
                    state.mood = max(0, state.mood - 2)
            state.gain_exp(10)
            # 培训结束切回待机
            self.pet.anim_manager.switch_to_idle()

        self.start_activity(course, cost, duration, effect)

    def street_performance(self):
        if self.pet.current_activity or self.pet.performance_win:
            if not messagebox.askyesno("活动冲突", "当前有活动正在进行，是否中止并开始表演？"):
                return
            else:
                self.cancel_current_activity()

        gain = random.randint(1, 5)
        is_vocal = random.random() < 0.5

        def effect(state):
            if is_vocal:
                state.vocal += gain
            else:
                state.dance += gain
            state.charm += 5
            state.satiety = max(0, state.satiety - 6)
            state.stamina = max(0, state.stamina - 18)
            state.hygiene = max(0, state.hygiene - 5)
            state.mood = min(100, state.mood + 3)
            state.gain_exp(5)

        self.start_activity("街头表演", 0, 3600, effect)

    # ==================== 面试 ====================
    def start_interview(self):
        s = self.pet.state
        if s.gold < 10:
            self.pet.ui_manager.show_info("金币不足10，无法报名面试！")
            return

        if self.pet.current_activity or self.pet.performance_win:
            if not messagebox.askyesno("活动冲突", "当前有活动正在进行，是否中止并准备面试？"):
                return
            else:
                self.cancel_current_activity()

        choice_win = tk.Toplevel(self.pet.pet_win)
        choice_win.overrideredirect(True)
        choice_win.wm_attributes("-topmost", True)
        choice_win.configure(bg="#FFFFFF")
        choice_win.attributes("-alpha", 1.0)

        w = 360
        pad = 20
        tk.Label(choice_win, text="🤔 面试前准备", font=("Segoe UI", 12, "bold"), fg="#000000", bg="#FFFFFF").pack(pady=(pad, 0))
        tk.Frame(choice_win, height=1, bg="#E5E5E5").pack(fill="x", padx=pad, pady=(8, 0))
        tk.Label(choice_win, text="报名费10金币，面试总时长28分钟\n选择一个准备方式：", font=("Segoe UI", 10), fg="#404040", bg="#FFFFFF", justify="left").pack(pady=(12, 0), padx=pad)

        btn_frame = tk.Frame(choice_win, bg="#FFFFFF")
        btn_frame.pack(pady=12, padx=pad, fill="x")

        def select_prep(effect_func, label):
            choice_win.destroy()
            s.gold -= 10
            self.pet.current_activity_name = "面试中"

            self._interview_stages = [
                (f"🤔 面试准备({label})...", 10, False),
                ("⏳ 等待叫号...", 10, False),
                ("🎤 才艺展示...", 10, False),
                ("📸 镜头测试...", 10, False),
                ("🎙️ 即兴问答", 0, True),
                ("📋 结果等候...", 10, False),
                ("📢 结果揭晓...", 10, False),
            ]
            self._interview_effect = effect_func
            self._interview_state = s
            self._interview_start_time = time.time()
            self._interview_total_duration = sum(d for _, d, _ in self._interview_stages)
            self._create_interview_progress_window()
            self._run_interview_stage(0)

        preps = [
            ("🍱 吃饱再去", lambda st: setattr(st, 'stamina', min(100, st.stamina + 15)), "吃饱"),
            ("🧼 精心打扮", lambda st: setattr(st, 'charm', st.charm + 2), "打扮"),
            ("😴 充分休息", lambda st: setattr(st, 'mood', min(100, st.mood + 6)), "休息"),
            ("🎤 临时抱佛脚", _random_talent_boost, "抱佛脚"),
        ]
        for text, func, label in preps:
            btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 10), fg="#000000", bg="#FFFFFF", activebackground="#F5F5F5", bd=1, relief="solid", padx=12, pady=8, command=lambda f=func, l=label: select_prep(f, l))
            btn.pack(fill="x", pady=4)

        tk.Button(choice_win, text="取消", font=("Segoe UI", 10), fg="#808080", bg="#FFFFFF", activebackground="#F5F5F5", bd=1, relief="solid", padx=12, pady=4, command=choice_win.destroy).pack(pady=(0, pad))

        choice_win.update_idletasks()
        h = choice_win.winfo_reqheight()
        x = self.pet.x + (self.pet.pet_w - w) // 2
        y = self.pet.y - h - 12
        if y < 0:
            y = self.pet.y + self.pet.pet_h + 12
        choice_win.geometry(f"{w}x{h}+{x}+{y}")

        def update_position():
            if choice_win.winfo_exists():
                nx = self.pet.x + (self.pet.pet_w - w) // 2
                ny = self.pet.y - h - 12
                if ny < 0:
                    ny = self.pet.y + self.pet.pet_h + 12
                choice_win.geometry(f"+{nx}+{ny}")
                choice_win.after(200, update_position)
        self.pet.register_follow_window(choice_win, update_position)

        def on_close():
            self.pet.unregister_follow_window(choice_win)
            choice_win.destroy()
        choice_win.protocol("WM_DELETE_WINDOW", on_close)

    def _create_interview_progress_window(self):
        win = tk.Toplevel(self.pet.pet_win)
        win.overrideredirect(True)
        win.wm_attributes("-topmost", True)
        win.wm_attributes("-transparentcolor", "#F0F0F0")
        win.configure(bg="#F0F0F0")
        bw, bh = 300, 80
        pos_x = self.pet.x + (self.pet.pet_w - bw) // 2
        pos_y = self.pet.y + self.pet.pet_h + 16
        win.geometry(f"{bw}x{bh}+{pos_x}+{pos_y}")

        title_label = tk.Label(win, text="", font=("Segoe UI", 12, "bold"), fg="#1A1A1A", bg="#F0F0F0")
        title_label.pack(pady=(8, 0))
        bar = tk.Canvas(win, width=240, height=4, bg="#E5E5E5", highlightthickness=0)
        bar.pack(pady=8)

        self._interview_win = win
        self._interview_title = title_label
        self._interview_bar = bar

        # 托盘用假活动对象，增加 total_duration 和 total_elapsed
        self.pet.current_activity = type('obj', (object,), {
            'title': '',
            'elapsed': 0,
            'duration': 1,
            'total_duration': self._interview_total_duration,
            'total_elapsed': 0,
            'get_progress': lambda self_obj: (
                min(100, int(self_obj.elapsed / max(1, self_obj.duration) * 100)),
                f"{max(0, self_obj.duration - self_obj.elapsed):.0f}秒"
            ),
            'get_total_progress': lambda self_obj: min(100, int(self_obj.total_elapsed / max(1, self_obj.total_duration) * 100)),
        })()

        def update_position():
            if win.winfo_exists():
                nx = self.pet.x + (self.pet.pet_w - bw) // 2
                ny = self.pet.y + self.pet.pet_h + 16
                win.geometry(f"+{nx}+{ny}")
                win.after(200, update_position)
        self.pet.register_follow_window(win, update_position)

    def _run_interview_stage(self, index):
        stages = self._interview_stages
        if index >= len(stages):
            self._finish_interview()
            return

        title, duration, is_question = stages[index]
        self._interview_title.config(text=title)
        self._interview_bar.delete("all")
        self._interview_bar.create_rectangle(0, 0, 0, 4, fill="#4CAF50", outline="")

        # 更新托盘显示的名称
        self.pet.current_activity_name = title

        act = self.pet.current_activity
        act.title = title
        act.elapsed = 0
        act.duration = duration

        if is_question:
            self._interview_question()
        else:
            self._start_stage_timer(index, duration)

    def _start_stage_timer(self, index, total_sec):
        start_time = time.time()
        act = self.pet.current_activity

        def update_bar():
            if not self._interview_win or not self._interview_win.winfo_exists():
                return
            elapsed = time.time() - start_time
            act.elapsed = elapsed
            act.total_elapsed = time.time() - self._interview_start_time
            pct = min(100, int(elapsed / total_sec * 100))
            self._interview_bar.delete("all")
            self._interview_bar.create_rectangle(0, 0, 240 * pct / 100, 4, fill="#4CAF50", outline="")
            if elapsed >= total_sec:
                if index == 0 and self._interview_effect:
                    self._interview_effect(self._interview_state)
                self._run_interview_stage(index + 1)
            else:
                self._interview_win.after(100, update_bar)
        update_bar()

    def _interview_question(self):
        q_win = tk.Toplevel(self.pet.pet_win)
        q_win.overrideredirect(True)
        q_win.wm_attributes("-topmost", True)
        q_win.configure(bg="#FFFFFF")
        q_win.attributes("-alpha", 1.0)

        w = 320
        pad = 16
        tk.Label(q_win, text="🎙️ 即兴问答", font=("Segoe UI", 12, "bold"), fg="#000000", bg="#FFFFFF").pack(pady=(pad, 0))
        tk.Frame(q_win, height=1, bg="#E5E5E5").pack(fill="x", padx=pad, pady=(8, 0))
        tk.Label(q_win, text="面试官突然问：\n「你觉得自己最大的优势是什么？」", font=("Segoe UI", 10), fg="#404040", bg="#FFFFFF", justify="left", wraplength=280).pack(pady=(12, 0), padx=pad)

        btn_frame = tk.Frame(q_win, bg="#FFFFFF")
        btn_frame.pack(pady=12, padx=pad, fill="x")

        def answer(attr, val):
            q_win.destroy()
            setattr(self._interview_state, attr, getattr(self._interview_state, attr) + val)
            q_idx = self._interview_stages.index(("🎙️ 即兴问答", 0, True))
            self._run_interview_stage(q_idx + 1)

        answers = [
            ("「我的唱功是最好的」", "vocal", 2),
            ("「我的舞蹈很有感染力」", "dance", 2),
            ("「我的综合实力很强」", "charm", 2),
        ]
        for text, attr, val in answers:
            btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 10), fg="#000000", bg="#FFFFFF", activebackground="#F5F5F5", bd=1, relief="solid", padx=12, pady=8, command=lambda a=attr, v=val: answer(a, v))
            btn.pack(fill="x", pady=4)

        q_win.update_idletasks()
        h = q_win.winfo_reqheight()
        x = self.pet.x + (self.pet.pet_w - w) // 2
        y = self.pet.y - h - 12
        if y < 0:
            y = self.pet.y + self.pet.pet_h + 12
        q_win.geometry(f"{w}x{h}+{x}+{y}")

        def update_position():
            if q_win.winfo_exists():
                nx = self.pet.x + (self.pet.pet_w - w) // 2
                ny = self.pet.y - h - 12
                if ny < 0:
                    ny = self.pet.y + self.pet.pet_h + 12
                q_win.geometry(f"+{nx}+{ny}")
                q_win.after(200, update_position)
        self.pet.register_follow_window(q_win, update_position)

        def on_close():
            self.pet.unregister_follow_window(q_win)
            q_win.destroy()
        q_win.protocol("WM_DELETE_WINDOW", on_close)

    def _finish_interview(self):
        if self._interview_win:
            self._interview_win.destroy()
            self._interview_win = None
        self.pet.current_activity = None
        self.pet.current_activity_name = None

        state = self._interview_state
        general = (state.vocal >= 25 and state.dance >= 25 and state.charm >= 25 and (state.vocal + state.dance + state.charm) >= 95)
        talent = (state.vocal >= 38 or state.dance >= 38)
        visual = (state.charm >= 42)

        if general or talent or visual:
            if general:
                msg = "面试通过！成为见习练习生（综合录取）"
            elif talent:
                msg = "面试通过！成为见习练习生（特长录取）"
            else:
                msg = "面试通过！成为见习练习生（颜值录取）"
            state.promote(2, "见习练习生 🎓")
        else:
            msg = "面试未通过，继续努力吧"

        self.pet.ui_manager.show_toast(msg)
        self.pet.anim_manager.switch_to_idle()
        state.save()
        self.pet.refresh_status()
        self.pet.event_scheduler.set_action(None)
        self.pet.status_panel_manager.refresh_tray_status_if_open()

    # ==================== 通用活动接口 ====================
    def use_inventory_item(self, name, duration, effect_func):
        if self.pet.state.inventory.get(name, 0) <= 0:
            self.pet.ui_manager.show_info("背包中没有该物品！")
            return
        self.pet.state.inventory[name] -= 1
        if self.pet.state.inventory[name] == 0:
            del self.pet.state.inventory[name]
        self.pet.ui_manager.show_toast(f"使用 {name}")
        self.pet.anim_manager.play_action_animation(name)
        self.start_activity(name, 0, duration, effect_func, refund_item=name)

    def start_clean_action(self, name, price, duration, effect_func):
        self.pet.anim_manager.play_action_animation(name)
        self.start_activity(name, price, duration, effect_func)

    def start_activity(self, name, price, duration, effect_func, refund_item=None):
        if self.pet.current_activity or self.pet.performance_win:
            if not messagebox.askyesno("活动冲突", "当前有活动正在进行，是否中止并开始新活动？"):
                return
            else:
                self.cancel_current_activity()

        s = self.pet.state
        if price > 0 and s.gold < price:
            self.pet.ui_manager.show_info("金币不足！")
            return
        if price > 0:
            s.gold -= price

        self.pet.event_scheduler.set_action(name)
        self.pet.current_activity_name = name

        # 统一活动计数（所有通过 start_activity 启动的活动都会累加）
        self.pet.state.activity_counts[name] = self.pet.state.activity_counts.get(name, 0) + 1

        # ... 后续 on_finish、on_cancel 等保持不变

        def on_finish():
            effect_func(s)
            self.pet.anim_manager.switch_to_idle()
            self.pet.ui_manager.show_toast(f"✅ {name}完成")
            self.pet.current_activity = None
            self.pet.current_activity_name = None
            s.save()
            self.pet.refresh_status()
            self.pet.event_scheduler.set_action(None)
            self.pet.status_panel_manager.refresh_tray_status_if_open()

        def on_cancel():
            if price > 0:
                s.gold += price
            if refund_item:
                s.inventory[refund_item] = s.inventory.get(refund_item, 0) + 1
            self.pet.anim_manager.switch_to_idle()
            self.pet.ui_manager.show_toast(f"❌ {name}已取消")
            self.pet.current_activity = None
            self.pet.current_activity_name = None
            s.save()
            self.pet.event_scheduler.set_action(None)
            self.pet.status_panel_manager.refresh_tray_status_if_open()

        self.pet.current_activity = ActivityWindow(self.pet.pet_win, f"{name}中...", duration, on_finish, on_cancel,
                                                   pet_x=self.pet.x, pet_y=self.pet.y,
                                                   pet_w=self.pet.pet_w, pet_h=self.pet.pet_h,
                                                   visible=True)
        self.pet.status_panel_manager.refresh_tray_status_if_open()

    def start_train(self, type_):
        if self.pet.current_activity or self.pet.performance_win:
            if not messagebox.askyesno("活动冲突", "当前有活动正在进行，是否中止并开始训练？"):
                return
            else:
                self.cancel_current_activity()

        ok, msg = self.pet.state.train(type_)
        if not ok:
            self.pet.ui_manager.show_info(msg)
            return
        self.pet.event_scheduler.set_action(f"训练-{type_}")
        self.pet.current_activity_name = f"训练-{type_}"

        self.pet.performance_win = PerformanceWindow(self.pet.pet_win, self.pet.state, "train", type_,
                                                     callback=self.on_activity_end, pet_x=self.pet.x, pet_y=self.pet.y,
                                                     pet_w=self.pet.pet_w, pet_h=self.pet.pet_h,
                                                     visible=True)
        self.pet.status_panel_manager.refresh_tray_status_if_open()

    def start_schedule(self):
        if self.pet.current_activity or self.pet.performance_win:
            if not messagebox.askyesno("活动冲突", "当前有活动正在进行，是否中止并接通告？"):
                return
            else:
                self.cancel_current_activity()

        ok, msg = self.pet.state.do_schedule()
        if not ok:
            self.pet.ui_manager.show_info(msg)
            return
        self.pet.event_scheduler.set_action("接通告")
        self.pet.current_activity_name = "接通告"

        self.pet.performance_win = PerformanceWindow(self.pet.pet_win, self.pet.state, "schedule", "",
                                                     callback=self.on_activity_end, pet_x=self.pet.x, pet_y=self.pet.y,
                                                     pet_w=self.pet.pet_w, pet_h=self.pet.pet_h,
                                                     visible=True)
        self.pet.status_panel_manager.refresh_tray_status_if_open()

    def on_activity_end(self, msg=None):
        self.pet.performance_win = None
        self.pet.current_activity_name = None
        if msg:
            self.pet.ui_manager.show_info(msg)
        self.pet.state.save()
        self.pet.refresh_status()
        self.pet.event_scheduler.set_action(None)
        self.pet.status_panel_manager.refresh_tray_status_if_open()
