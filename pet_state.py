import random
import os
import time
import json
from game_time import GameTime
from utils import SAVE_FILE

class PetState:
    def __init__(self):
        self.init_defaults()
        self.bubble_msg = ""
        self.bubble_timer = 0
        self.idle_time = 0
        self.idle_threshold = 3600
        self.water_interval = 45 * 60
        self.eye_interval = 50 * 60
        self.last_water_reminder = time.time()
        self.last_eye_reminder = time.time()
        self.last_danmu_time = time.time()
        self.danmu_interval = random.randint(120, 300)
        self._last_greeting_day = 0
        self._greeted_morning = False
        self._greeted_night = False
        self.total_playtime = 0
        self.last_milestone_week = 0
        self.last_milestone_day = 0
        self.inventory = {}
        self.scale = 1.5
        self.base_w = 160
        self.base_h = 220

    def init_defaults(self):
        self.satiety = 60
        self.stamina = 50
        self.hygiene = 80
        self.mood = 60
        self.gold = 50
        self.star = 0
        self.sick = False
        self.resting = False
        self.fatigue = 0
        self.consecutive_train = 0

        self.vocal = random.randint(10, 40)
        self.dance = random.randint(10, 40)
        self.acting = 10
        self.variety = 0
        self.charm = random.randint(10, 45)
        self.popularity = 0
        self.fans = 0

        self.exp = 0
        self.level = 1
        self.exp_to_next = 50
        self.stage = 1
        self.stage_name = "素人 👤"
        self.route = 0

        self.game_time = GameTime()
        self.busy = False
        self.train_boost = {"voice": 0, "fitness": 0, "expression": 0, "shape": 0}
        self.mood_decay_reduce = 0

        self.focus_mode = False
        self.focus_end_time = 0
        self.focus_duration = 25 * 60

        self.event_cooldowns = {}   # 事件冷却记录

    @property
    def pet_w(self):
        return int(self.base_w * self.scale)

    @property
    def pet_h(self):
        return int(self.base_h * self.scale)

    @property
    def health(self):
        return int((self.satiety + self.stamina + self.hygiene) / 3)

    @property
    def talent(self):
        return int((self.vocal + self.dance + self.acting + self.variety) / 4)

    def decay(self):
        self.satiety = max(0, self.satiety - 4)
        self.hygiene = max(0, self.hygiene - 3)
        self.mood = max(0, self.mood - 2 * (1 - self.mood_decay_reduce))
        if self.hygiene < 30 and random.random() < 0.15:
            self.sick = True
        if self.health < 20 and random.random() < 0.3:
            self.sick = True
        self.game_time.tick()
        if self.stamina <= 0 and not self.resting:
            self.resting = True
            self.bubble_msg = "体力耗尽，必须休息！"
            self.bubble_timer = 5
        if self.resting:
            self.stamina = min(100, self.stamina + 5)
            if self.stamina >= 30:
                self.resting = False
                self.bubble_msg = "体力恢复了！"
                self.bubble_timer = 3
        if self.bubble_timer > 0:
            self.bubble_timer -= 1
        else:
            self.bubble_msg = ""
        self.check_promotion()

    def feed(self, satiety_amt=20, stamina_amt=0, mood_amt=0):
        if self.resting:
            return
        self.satiety = min(100, self.satiety + satiety_amt)
        self.stamina = min(100, self.stamina + stamina_amt)
        self.mood = min(100, self.mood + mood_amt)
        self.gain_exp(3)

    def sleep(self, amt=40):
        self.stamina = min(100, self.stamina + amt)
        self.fatigue = max(0, self.fatigue - 15)
        self.resting = False
        self.gain_exp(3)

    def cure(self):
        self.sick = False
        self.hygiene = min(100, self.hygiene + 20)

    def train(self, type_):
        if self.busy:
            return False, "正在进行其他活动！"
        if self.resting:
            return False, "需要休息！"
        if self.mood < 30:
            return False, "心情太差，不想训练！"
        if self.stamina < 20:
            return False, "体力不足！"
        self.busy = True
        return True, ""

    def do_schedule(self):
        if self.busy:
            return False, "正在进行其他活动！"
        if self.resting:
            return False, "需要休息！"
        if self.stamina < 20:
            return False, "体力不足！"
        self.busy = True
        return True, ""

    def apply_train_result(self, type_, modifier=1.0, extra_msg=""):
        self.busy = False
        boost = 1 + self.train_boost.get(type_, 0)
        mood_factor = 1.0
        if self.mood >= 70:
            mood_factor += 0.1
        elif self.mood < 30:
            mood_factor -= 0.3
        satiety_penalty = 1.0
        if self.satiety > 90:
            satiety_penalty -= 0.05
        stage_bonus = 1.0
        if self.stage < 2:
            stage_bonus += 0.15
        if self.route == 2:
            stage_bonus += 0.15
        total_multiplier = mood_factor * satiety_penalty * stage_bonus * boost * modifier

        injury = random.random() < min(0.3, self.fatigue * 0.01 + self.consecutive_train * 0.03)

        if type_ == "voice":
            gain = int(40 * total_multiplier)
            self.vocal += gain
            msg = f"声乐课完成！唱功 +{gain}"
            if random.random() < 0.1:
                self.vocal += 2
                msg += " 🎵开嗓！额外+2"
            cost_stamina, cost_hyg, cost_satiety, cost_mood = 25, 15, 10, 3
        elif type_ == "fitness":
            gain = int(55 * total_multiplier)
            self.dance += gain
            msg = f"舞蹈集训完成！舞蹈 +{gain}"
            if random.random() < 0.05:
                injury = True
                msg += " ⚠️加练受伤！"
            cost_stamina, cost_hyg, cost_satiety, cost_mood = 35, 30, 12, 5
        elif type_ == "expression":
            gain_act = int(45 * total_multiplier)
            gain_charm = int(10 * total_multiplier)
            self.acting += gain_act
            self.charm += gain_charm
            msg = f"表演课完成！演技 +{gain_act} 魅力 +{gain_charm}"
            cost_stamina, cost_hyg, cost_satiety, cost_mood = 20, 10, 8, 2
        elif type_ == "shape":
            gain_charm = int(35 * total_multiplier)
            self.charm += gain_charm
            self.satiety = max(0, self.satiety - 10)
            msg = f"形体管理完成！魅力 +{gain_charm}"
            cost_stamina, cost_hyg, cost_satiety, cost_mood = 30, 20, 10, 3
        else:
            return "未知训练"

        self.stamina = max(0, self.stamina - cost_stamina)
        self.hygiene = max(0, self.hygiene - cost_hyg)
        self.satiety = max(0, self.satiety - cost_satiety)
        self.mood = max(0, self.mood - cost_mood)
        self.fatigue = min(100, self.fatigue + random.randint(5, 15))
        self.consecutive_train += 1
        self.gain_exp(8)
        if injury:
            self.sick = True
            msg += " 🤕受伤生病！"
        if extra_msg:
            msg += " " + extra_msg
        self.train_boost[type_] = 0
        return msg

    def apply_schedule_result(self, modifier=1.0, extra_msg=""):
        self.busy = False
        self.stamina = max(0, self.stamina - random.randint(20, 40))
        self.hygiene = max(0, self.hygiene - random.randint(5, 25))
        self.satiety = max(0, self.satiety - random.randint(8, 12))
        self.fatigue = min(100, self.fatigue + random.randint(5, 10))
        rate = min(0.9, (self.talent + self.charm) / 250)
        if self.mood > 70:
            rate += 0.1
        rate *= modifier
        if random.random() < rate:
            gold = random.randint(20, 50) + self.popularity // 5
            pop = random.randint(5, 15)
            fans = random.randint(10, 30)
            self.gold += gold
            self.popularity += pop
            self.fans += fans
            self.mood = min(100, self.mood + 8)
            msg = f"通告成功！💰+{gold} 人气+{pop} 粉丝+{fans}"
        else:
            self.mood = max(0, self.mood - 20)
            msg = "通告失败……心情大幅下降"
        if extra_msg:
            msg += " " + extra_msg
        self.gain_exp(10)
        return msg

    def check_promotion(self):
        s = self
        if s.stage == 2:
            if s.vocal >= 80 and s.dance >= 80 and s.charm >= 60:
                s.promote(3, "公开练习生 🌱", route=1)
            elif (s.vocal >= 120 or s.dance >= 120 or s.acting >= 120) and random.random() < 0.05:
                s.promote(4, "未公开练习生 🔒", route=2)
        elif s.stage in (3, 4):
            if s.vocal >= 150 and s.dance >= 150 and s.charm >= 120:
                s.promote(5, "新人偶像 🚀")
        elif s.stage == 5:
            if s.popularity >= 5000 and s.charm >= 200 and (s.vocal >= 250 or s.dance >= 250 or s.acting >= 250):
                s.promote(6, "当红明星 👑")
        elif s.stage == 6:
            if s.popularity >= 15000 and s.charm >= 350 and ((s.vocal >= 400 and s.dance >= 400) or (s.vocal >= 400 and s.acting >= 400) or (s.dance >= 400 and s.acting >= 400)):
                s.promote(7, "时代巨星 🌟")

    def promote(self, new_stage, name, route=None):
        self.stage = new_stage
        self.stage_name = name
        if route is not None:
            self.route = route
        self.mood = 100
        self.gold += 100
        self.fans += 50

    def gain_exp(self, amt):
        self.exp += amt
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.exp_to_next = int(self.exp_to_next * 1.5)

    def to_dict(self):
        return {
            'satiety': self.satiety, 'stamina': self.stamina, 'hygiene': self.hygiene,
            'mood': self.mood, 'gold': self.gold, 'star': self.star,
            'sick': self.sick, 'resting': self.resting,
            'fatigue': self.fatigue, 'consecutive_train': self.consecutive_train,
            'vocal': self.vocal, 'dance': self.dance, 'acting': self.acting,
            'variety': self.variety, 'charm': self.charm, 'popularity': self.popularity,
            'fans': self.fans, 'exp': self.exp, 'level': self.level,
            'exp_to_next': self.exp_to_next, 'stage': self.stage,
            'stage_name': self.stage_name, 'route': self.route,
            'game_time': self.game_time.to_dict(),
            'focus_mode': self.focus_mode, 'focus_end_time': self.focus_end_time,
            'focus_duration': self.focus_duration,
            'total_playtime': self.total_playtime,
            'last_milestone_week': self.last_milestone_week,
            'last_milestone_day': self.last_milestone_day,
            'inventory': self.inventory,
            'scale': self.scale,
            'event_cooldowns': self.event_cooldowns
        }

    def from_dict(self, d):
        self.satiety = d.get('satiety', d.get('hunger', 60))
        self.stamina = d.get('stamina', d.get('energy', 50))
        self.hygiene = d.get('hygiene', 80)
        self.mood = d.get('mood', 60)
        self.gold = d.get('gold', 50)
        self.star = d.get('star', 0)
        self.sick = d.get('sick', False)
        self.resting = d.get('resting', False)
        self.fatigue = d.get('fatigue', 0)
        self.consecutive_train = d.get('consecutive_train', 0)
        self.vocal = d.get('vocal', random.randint(10, 40))
        self.dance = d.get('dance', random.randint(10, 40))
        self.acting = d.get('acting', 10)
        self.variety = d.get('variety', 0)
        self.charm = d.get('charm', random.randint(10, 45))
        self.popularity = d.get('popularity', 0)
        self.fans = d.get('fans', 0)
        self.exp = d.get('exp', 0)
        self.level = d.get('level', 1)
        self.exp_to_next = d.get('exp_to_next', 50)
        self.stage = d.get('stage', 1)
        self.stage_name = d.get('stage_name', '素人 👤')
        self.route = d.get('route', 0)
        if 'game_time' in d:
            self.game_time.from_dict(d['game_time'])
        self.focus_mode = d.get('focus_mode', False)
        self.focus_end_time = d.get('focus_end_time', 0)
        self.focus_duration = d.get('focus_duration', 25 * 60)
        self.total_playtime = d.get('total_playtime', 0)
        self.last_milestone_week = d.get('last_milestone_week', 0)
        self.last_milestone_day = d.get('last_milestone_day', 0)
        self.inventory = d.get('inventory', {})
        self.scale = d.get('scale', 1.5)
        self.event_cooldowns = d.get('event_cooldowns', {})

    def save(self):
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"存档失败:{e}")

    def load(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.from_dict(data)
        except Exception as e:
            print(f"读档失败:{e}")
