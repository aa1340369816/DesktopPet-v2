import time
import random
from activity_monitor import ActivityMonitor


class CompanionManager:
    def __init__(self, pet):
        self.pet = pet

    def companion_loop(self):
        s = self.pet.state
        now = time.time()
        idle = ActivityMonitor.get_idle_seconds()
        s.idle_time = idle
        s.total_playtime += 1
        if s.focus_mode and now > s.focus_end_time:
            s.focus_mode = False
            self.pet.ui_manager.show_toast("🍅 专注时间结束！", 3000)
        if not s.focus_mode and not s.resting:
            if idle > s.idle_threshold:
                self.pet.ui_manager.show_toast("💺 坐太久啦，起来活动一下！")
                s.idle_time = 0
            if now - s.last_water_reminder > s.water_interval:
                self.pet.ui_manager.show_toast("💧 喝点水吧～")
                s.last_water_reminder = now
            if now - s.last_eye_reminder > s.eye_interval:
                self.pet.ui_manager.show_toast("👀 休息一下眼睛哦")
                s.last_eye_reminder = now
        if not s.focus_mode and now - s.last_danmu_time > s.danmu_interval:
            self.pet.danmaku_manager.show_danmu()
            s.last_danmu_time = now
            s.danmu_interval = random.randint(120, 300)
        self.check_daytime_greeting(now)

        self.pet.event_scheduler.update(self.pet.pet_win)
        self.pet.root.after(1000, self.companion_loop)

    def check_daytime_greeting(self, now):
        s = self.pet.state
        local = time.localtime(now)
        hour = local.tm_hour
        if not hasattr(s, '_last_greeting_day'):
            s._last_greeting_day = 0
            s._greeted_morning = False
            s._greeted_night = False
        if s._last_greeting_day != local.tm_yday:
            s._last_greeting_day = local.tm_yday
            s._greeted_morning = False
            s._greeted_night = False
        if not s._greeted_morning and 6 <= hour <= 9:
            self.pet.ui_manager.show_toast("☀️ 早上好！今天也要加油哦！", 3000)
            s._greeted_morning = True
        elif not s._greeted_night and 22 <= hour <= 23:
            self.pet.ui_manager.show_toast("🌙 晚安，早点休息～", 3000)
            s._greeted_night = True
        elif not s._greeted_night and hour >= 2:
            self.pet.ui_manager.show_toast("😟 还不休息吗？", 3000)
            s._greeted_night = True
