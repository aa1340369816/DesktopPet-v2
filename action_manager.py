import random
from activity_window import ActivityWindow
from performance_window import PerformanceWindow


class ActionManager:
    def __init__(self, pet):
        self.pet = pet

    def do_part_time_job(self, job):
        s = self.pet.state
        if job == "便利店兼职":
            self.pet.anim_manager.play_store_animation()
            duration = 3600
            def effect(state):
                state.gold += 20
                state.gain_exp(5)
                self.pet.anim_manager.switch_to_idle()
        elif job == "咖啡店打工":
            duration = 3600
            def effect(state):
                state.gold += 15
                state.charm += 3
                state.gain_exp(5)
        elif job == "快递分拣":
            duration = 5400
            def effect(state):
                state.gold += 30
                state.stamina = max(0, state.stamina - 15)
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
            state.gain_exp(10)

        self.start_activity(course, cost, duration, effect)

    def street_performance(self):
        s = self.pet.state
        gain = random.randint(1, 5)
        is_vocal = random.random() < 0.5

        def effect(state):
            if is_vocal:
                state.vocal += gain
            else:
                state.dance += gain
            state.charm += 5
            state.gain_exp(5)

        self.start_activity("街头表演", 0, 3600, effect)

    def start_interview(self):
        s = self.pet.state
        total = s.vocal + s.dance + s.charm
        if total >= 90 and s.vocal >= 25 and s.dance >= 25 and s.charm >= 25:
            s.promote(2, "见习练习生 🎓")
            self.pet.ui_manager.show_toast("面试通过！成为见习练习生")
        else:
            self.pet.ui_manager.show_info("面试未通过，继续努力吧")
        s.save()

    def use_inventory_item(self, name, duration, effect_func):
        if self.pet.state.inventory.get(name,0) <= 0:
            self.pet.ui_manager.show_info("背包中没有该物品！")
            return
        self.pet.state.inventory[name] -= 1
        if self.pet.state.inventory[name] == 0:
            del self.pet.state.inventory[name]
        self.pet.ui_manager.show_toast(f"使用 {name}")
        self.start_activity(name, 0, duration, effect_func)

    def start_activity(self, name, price, duration, effect_func):
        s = self.pet.state
        if price > 0 and s.gold < price:
            self.pet.ui_manager.show_info("金币不足！")
            return
        if price > 0:
            s.gold -= price

        self.pet.event_scheduler.set_action(name)

        def on_finish():
            effect_func(s)
            self.pet.ui_manager.show_toast(f"✅ {name}完成")
            s.save()
            self.pet.refresh_status()
            self.pet.event_scheduler.set_action(None)

        def on_cancel():
            if price > 0:
                s.gold += price
            self.pet.ui_manager.show_toast(f"❌ {name}已取消")
            s.save()
            self.pet.event_scheduler.set_action(None)

        self.pet.current_activity = ActivityWindow(self.pet.pet_win, f"{name}中...", duration, on_finish, on_cancel,
                                                   pet_x=self.pet.x, pet_y=self.pet.y,
                                                   pet_w=self.pet.pet_w, pet_h=self.pet.pet_h,
                                                   visible=False)

    def start_train(self, type_):
        ok, msg = self.pet.state.train(type_)
        if not ok:
            self.pet.ui_manager.show_info(msg)
            return
        self.pet.event_scheduler.set_action(f"训练-{type_}")
        self.pet.performance_win = PerformanceWindow(self.pet.pet_win, self.pet.state, "train", type_,
                                                     callback=self.on_activity_end, pet_x=self.pet.x, pet_y=self.pet.y,
                                                     pet_w=self.pet.pet_w, pet_h=self.pet.pet_h,
                                                     visible=False)

    def start_schedule(self):
        ok, msg = self.pet.state.do_schedule()
        if not ok:
            self.pet.ui_manager.show_info(msg)
            return
        self.pet.event_scheduler.set_action("接通告")
        self.pet.performance_win = PerformanceWindow(self.pet.pet_win, self.pet.state, "schedule", "",
                                                     callback=self.on_activity_end, pet_x=self.pet.x, pet_y=self.pet.y,
                                                     pet_w=self.pet.pet_w, pet_h=self.pet.pet_h,
                                                     visible=False)

    def on_activity_end(self, msg=None):
        self.pet.performance_win = None
        if msg:
            self.pet.ui_manager.show_info(msg)
        self.pet.state.save()
        self.pet.refresh_status()
        self.pet.event_scheduler.set_action(None)
