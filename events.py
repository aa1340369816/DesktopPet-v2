import random
import time
import tkinter as tk

# 事件数据从独立文件导入
from event_pool import EVENT_POOL


# ==================== 选择窗口 ====================
class ChoiceWindow:
    """极简二选一窗口：垂直排列按钮，文字永不截断"""
    def __init__(self, parent, event, on_choose, pet_x, pet_y, pet_w, pet_h):
        self.parent = parent
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        self.win.configure(bg="#FFFFFF")
        self.win.attributes("-alpha", 1.0)

        self.w = 340

        # 标题
        title_text = event.get("name", "")
        title_label = tk.Label(self.win, text=title_text,
                               font=("Segoe UI", 12, "bold"), fg="#000000", bg="#FFFFFF")
        title_label.pack(pady=(20, 0))

        # 分隔线
        sep = tk.Frame(self.win, height=1, bg="#E5E5E5")
        sep.pack(fill="x", padx=20, pady=(12, 0))

        # 描述
        desc_label = tk.Label(self.win, text=event["description"],
                              font=("Segoe UI", 10), fg="#404040", bg="#FFFFFF",
                              wraplength=280, justify="left")
        desc_label.pack(pady=(16, 0), padx=20)

        # 按钮框架（垂直排列）
        btn_frame = tk.Frame(self.win, bg="#FFFFFF")
        btn_frame.pack(pady=16, padx=20, fill="x")

        def make_choice(choice_idx):
            self.win.destroy()
            on_choose(event["choices"][choice_idx])

        for i, choice in enumerate(event["choices"]):
            btn = tk.Button(btn_frame, text=choice["text"],
                            font=("Segoe UI", 10), fg="#000000", bg="#FFFFFF",
                            activebackground="#F5F5F5",
                            bd=1, relief="solid",
                            justify="left",
                            wraplength=280,
                            padx=12, pady=8,
                            anchor="w",
                            command=lambda idx=i: make_choice(idx))
            btn.pack(fill="x", pady=4)

        # 底部提示
        tip_label = tk.Label(self.win, text="请选择一个选项",
                             font=("Segoe UI", 9), fg="#808080", bg="#FFFFFF")
        tip_label.pack(pady=(0, 12))

        # 自适应高度
        self.win.update_idletasks()
        req_height = self.win.winfo_reqheight()
        if req_height < 200:
            req_height = 200
        if req_height > 500:
            req_height = 500
        self.h = req_height

        self._update_position(pet_x, pet_y, pet_w, pet_h)
        self.win.geometry(f"{self.w}x{self.h}+{self.x}+{self.y}")

        self._follow()

    def _update_position(self, pet_x, pet_y, pet_w, pet_h):
        self.x = pet_x + (pet_w - self.w) // 2
        self.y = pet_y - self.h - 12
        if self.y < 0:
            self.y = pet_y + pet_h + 12

    def _follow(self):
        if not self.win.winfo_exists():
            return
        pet_x = self.parent.winfo_rootx()
        pet_y = self.parent.winfo_rooty()
        pet_w = self.parent.winfo_width()
        pet_h = self.parent.winfo_height()
        self._update_position(pet_x, pet_y, pet_w, pet_h)
        self.win.geometry(f"+{self.x}+{self.y}")
        self.win.after(200, self._follow)


# ==================== 事件调度器 ====================
class EventScheduler:
    def __init__(self, pet_state, toast_callback, info_callback,
                 float_callback=None, narrative_callback=None, refresh_callback=None):
        self.state = pet_state
        self.toast = toast_callback
        self.info = info_callback
        self.float_callback = float_callback
        self.narrative_callback = narrative_callback if narrative_callback else info_callback
        self.refresh_callback = refresh_callback

        # 冷却记录
        self.cooldowns = {}
        if hasattr(pet_state, 'event_cooldowns'):
            self.cooldowns = pet_state.event_cooldowns

        # 下次检查时间（启动后5分钟开始检查）
        self.next_check_time = time.time() + 300

        # 当前打开的选择窗口
        self.current_choice_win = None

        # 当前正在进行的活动（用于条件判断）
        self.current_action = None

    def set_action(self, action_name):
        """设置当前活动，如 '便利店兼职'、'训练-voice'、None 表示空闲"""
        self.current_action = action_name
        # 开始活动时立即允许一次事件检查
        if action_name is not None:
            self.next_check_time = time.time()

    def update(self, parent_window):
        """在 companion_loop 中每秒调用一次"""
        # 专注模式或休息时不触发
        if self.state.focus_mode or self.state.resting:
            return

        now = time.time()
        if now < self.next_check_time:
            return

        # 重置下次检查时间（5~30分钟随机间隔）
        self.next_check_time = now + random.randint(300, 1800)

        # 概率过滤（50%）
        if random.random() > 0.5:
            return

        # 筛选可用事件
        available = []
        for event in EVENT_POOL:
            if not self._check_cooldown(event, now):
                continue
            if not self._check_conditions(event.get("trigger_condition")):
                continue
            available.append(event)

        if not available:
            return

        # 按权重随机选择
        total_weight = sum(ev.get("weight", 10) for ev in available)
        rand = random.uniform(0, total_weight)
        cumulative = 0
        chosen = None
        for ev in available:
            cumulative += ev.get("weight", 10)
            if rand <= cumulative:
                chosen = ev
                break

        if chosen:
            self.trigger_event(chosen, parent_window)

    def _check_cooldown(self, event, now):
        eid = event["id"]
        if eid in self.cooldowns:
            last = self.cooldowns[eid]
            if now - last < event.get("cooldown", 0):
                return False
        return True

    def _check_conditions(self, conditions):
        """检查是否满足触发条件（stage, action, state, hour_range 等）"""
        if conditions is None:
            return True

        s = self.state

        # 阶段限制
        if "stage" in conditions:
            if s.stage not in conditions["stage"]:
                return False

        # 活动限制
        if "action" in conditions:
            if self.current_action != conditions["action"]:
                return False

        # 属性条件
        if "state" in conditions:
            for attr, rule in conditions["state"].items():
                current_val = getattr(s, attr, 0)
                if rule.startswith(">"):
                    if not (current_val > float(rule[1:])):
                        return False
                elif rule.startswith("<"):
                    if not (current_val < float(rule[1:])):
                        return False
                elif rule.startswith(">="):
                    if not (current_val >= float(rule[2:])):
                        return False
                elif rule.startswith("<="):
                    if not (current_val <= float(rule[2:])):
                        return False

        # 游戏内时间
        if "hour_range" in conditions:
            low, high = conditions["hour_range"]
            if not (low <= s.game_time.hour < high):
                return False

        # 空闲限制
        if conditions.get("not_busy") and s.busy:
            return False

        return True

    def trigger_event(self, event, parent_window):
        """执行事件并显示对应 UI"""
        etype = event["type"]

        # 记录冷却
        self.cooldowns[event["id"]] = time.time()
        self._save_cooldowns()

        if etype == "instant":
            effects = event.get("effects", {})
            self._apply_effects(effects)
            # 浮动飘字
            effect_list = self._format_effects(effects)
            effect_str = "  ".join(effect_list) if effect_list else ""
            if self.float_callback and effect_list:
                self.float_callback(effect_list)
            # 头顶弹窗
            display_text = event.get("description", "")
            if effect_str:
                display_text += "\n\n✨ " + effect_str
            self.narrative_callback(display_text, event.get("name", ""))
            # toast 简短提示（如果有）
            toast_msg = event.get("toast", "")
            if toast_msg:
                self.toast(toast_msg, 3000)

        elif etype == "narrative":
            effects = event.get("effects", {})
            if effects:
                self._apply_effects(effects)
            effect_list = self._format_effects(effects)
            effect_str = "  ".join(effect_list) if effect_list else ""
            if self.float_callback and effect_list:
                self.float_callback(effect_list)
            desc = event["description"]
            if effect_str:
                desc += "\n\n✨ " + effect_str
            self.narrative_callback(desc, event.get("name", ""))

        elif etype == "choice":
            if self.current_choice_win and self.current_choice_win.winfo_exists():
                return
            pet_x = parent_window.winfo_rootx()
            pet_y = parent_window.winfo_rooty()
            pet_w = parent_window.winfo_width()
            pet_h = parent_window.winfo_height()
            self.current_choice_win = ChoiceWindow(
                parent_window,
                event,
                lambda choice: self._on_choice_made(event, choice),
                pet_x, pet_y, pet_w, pet_h
            )

    def _on_choice_made(self, event, choice):
        if choice is None:
            return
        effects = choice["effects"]
        self._apply_effects(effects)

        # 浮动飘字
        if self.float_callback:
            effect_list = self._format_effects(effects)
            if effect_list:
                self.float_callback(effect_list)

        # 结果文字 + 效果数值显示在头顶
        result_text = choice.get("result", "")
        effect_str = "  ".join(self._format_effects(effects))
        if result_text and effect_str:
            display = f"{result_text}\n\n✨ {effect_str}"
        elif result_text:
            display = result_text
        elif effect_str:
            display = f"✨ {effect_str}"
        else:
            display = ""
        if display:
            self.narrative_callback(display, event.get("name", ""))

    def _apply_effects(self, effects):
        """将效果字典应用到 PetState"""
        s = self.state
        for attr, value in effects.items():
            if attr == "sick":
                if value:
                    s.sick = True
                continue

            current = getattr(s, attr, 0)
            if attr in ("satiety", "stamina", "hygiene", "mood"):
                setattr(s, attr, max(0, min(100, current + value)))
            elif attr == "fatigue":
                setattr(s, attr, max(0, min(100, current + value)))
            elif attr in ("gold", "fans", "popularity"):
                setattr(s, attr, max(0, current + value))
            else:
                setattr(s, attr, max(0, current + value))
        s.save()
        if self.refresh_callback:
            self.refresh_callback()

    def _format_effects(self, effects):
        """将效果字典格式化为列表，如 ['饱食+5', '心情+3']"""
        if not effects:
            return []
        name_map = {
            "satiety": "饱食", "stamina": "体力", "hygiene": "清洁", "mood": "心情",
            "gold": "金币", "vocal": "唱功", "dance": "舞蹈", "acting": "演技",
            "variety": "综艺", "charm": "魅力", "popularity": "人气", "fans": "粉丝",
            "fatigue": "疲劳", "sick": "生病"
        }
        parts = []
        for attr, val in effects.items():
            if attr == "sick":
                if val:
                    parts.append("生病了！")
                continue
            display = name_map.get(attr, attr)
            if val > 0:
                parts.append(f"{display}+{val}")
            elif val < 0:
                parts.append(f"{display}{val}")
        return parts

    def _save_cooldowns(self):
        """将冷却记录写入 pet_state 以便存档"""
        self.state.event_cooldowns = self.cooldowns
