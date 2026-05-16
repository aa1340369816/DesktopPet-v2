import time

class GameTime:
    def __init__(self):
        self.day = 1
        self.week = 1
        self.weekday = 1
        self.hour = 8
        self.minute = 0
        self.last_tick = time.time()
        self.weekday_names = ["", "周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    def tick(self):
        if time.time() - self.last_tick >= 3600:
            self.last_tick = time.time()
            self.advance_hours(1)
            return True
        return False

    def advance_day(self):
        self.day += 1
        self.weekday = (self.weekday % 7) + 1
        if self.weekday == 1:
            self.week += 1

    def advance_hours(self, h):
        self.hour += h
        while self.hour >= 24:
            self.hour -= 24
            self.advance_day()

    def get_weekday_name(self):
        return self.weekday_names[self.weekday]

    def get_time_str(self):
        return f"📅 第{self.week}周 第{self.day}天 {self.hour:02d}:{self.minute:02d}"

    def to_dict(self):
        return {'day': self.day, 'week': self.week, 'weekday': self.weekday,
                'hour': self.hour, 'minute': self.minute}

    def from_dict(self, d):
        self.day = d.get('day', 1)
        self.week = d.get('week', 1)
        self.weekday = d.get('weekday', 1)
        self.hour = d.get('hour', 8)
        self.minute = d.get('minute', 0)