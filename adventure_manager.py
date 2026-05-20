import tkinter as tk
from tkinter import messagebox
import time
import random


class AdventureStageWindow:
    """奇遇叙事窗口（极简白底黑字，分页显示，选项在最后，高度固定）"""
    def __init__(self, parent, adventure_name, stage_text, options, callback, pet_x, pet_y, pet_w, pet_h, is_trigger=False):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        bg_color = "#FFF8E1" if is_trigger else "#FFFFFF"
        self.win.configure(bg=bg_color)
        self.win.attributes("-alpha", 1.0)

        self.w = 400
        self.pad = 20
        self.callback = callback
        self.options = options
        self.current_page = 0

        raw_paragraphs = stage_text.split('\n')
        paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]
        if not paragraphs:
            paragraphs = ["（剧情缺失）"]

        self.text_pages = []
        for i in range(0, len(paragraphs), 6):
            self.text_pages.append(paragraphs[i:i+6])

        self.has_options = bool(options)
        self.total_pages = len(self.text_pages) + (1 if self.has_options else 0)

        tk.Label(self.win, text=adventure_name, font=("Segoe UI", 12, "bold"),
                 fg="#000000", bg=bg_color).pack(pady=(self.pad, 0))
        tk.Frame(self.win, height=1, bg="#E5E5E5").pack(fill="x", padx=self.pad, pady=(8, 0))

        self.content_frame = tk.Frame(self.win, bg=bg_color)
        self.content_frame.pack(pady=(12, 0), padx=self.pad, fill="x")
        self.content_widgets = []

        self.btn_frame = tk.Frame(self.win, bg=bg_color)
        self.btn_frame.pack(pady=12, padx=self.pad, fill="x")

        self.pet_x = pet_x
        self.pet_y = pet_y
        self.pet_w = pet_w
        self.pet_h = pet_h

        self.fixed_h = 420
        self._show_page(0)
        x = pet_x + (pet_w - self.w) // 2
        y = pet_y - self.fixed_h - 12
        if y < 0:
            y = pet_y + pet_h + 12
        self.win.geometry(f"{self.w}x{self.fixed_h}+{x}+{y}")
        self._follow()

    def _show_page(self, page_idx):
        for w in self.content_widgets:
            w.destroy()
        self.content_widgets.clear()
        for w in self.btn_frame.winfo_children():
            w.destroy()

        if page_idx < len(self.text_pages):
            for paragraph in self.text_pages[page_idx]:
                lbl = tk.Label(self.content_frame, text=paragraph, font=("Segoe UI", 10),
                               fg="#404040", bg=self.win.cget("bg"),
                               anchor="w", justify="left", wraplength=360)
                lbl.pack(fill="x", pady=2)
                self.content_widgets.append(lbl)

            if page_idx < self.total_pages - 1:
                next_text = "继续 ▶"
                next_cmd = self._next_page
            else:
                next_text = "结束"
                next_cmd = self.win.destroy

            tk.Button(self.btn_frame, text=next_text, font=("Segoe UI", 12),
                      fg="#000000", bg="#FFFFFF", activebackground="#F5F5F5",
                      bd=1, relief="solid", padx=12, pady=14,
                      command=next_cmd).pack(side="left", padx=4)

            tk.Button(self.btn_frame, text="关闭", font=("Segoe UI", 12),
                      fg="#808080", bg="#FFFFFF", activebackground="#F5F5F5",
                      bd=1, relief="solid", padx=12, pady=14,
                      command=self.win.destroy).pack(side="right", padx=4)
        else:
            tk.Label(self.content_frame, text="请做出你的选择：", font=("Segoe UI", 10, "bold"),
                     fg="#000000", bg=self.win.cget("bg")).pack(anchor="w", pady=(0, 8))
            self.content_widgets.append(self.content_frame.winfo_children()[-1])

            for i, opt in enumerate(self.options):
                tk.Button(self.btn_frame, text=opt["text"], font=("Segoe UI", 12),
                          fg="#000000", bg="#FFFFFF", activebackground="#F5F5F5",
                          bd=1, relief="solid", padx=12, pady=14,
                          command=lambda idx=i: self._choose(idx)).pack(fill="x", pady=4)

            tk.Button(self.btn_frame, text="取消", font=("Segoe UI", 12),
                      fg="#808080", bg="#FFFFFF", activebackground="#F5F5F5",
                      bd=1, relief="solid", padx=12, pady=14,
                      command=self.win.destroy).pack(pady=(8, 0))

        self.current_page = page_idx

    def _next_page(self):
        if self.current_page < self.total_pages - 1:
            self._show_page(self.current_page + 1)
        else:
            self.win.destroy()

    def _choose(self, idx):
        result_text = self.options[idx].get("result", "") if isinstance(self.options[idx], dict) else ""
        if result_text:
            for w in self.content_widgets:
                w.destroy()
            self.content_widgets.clear()
            for w in self.btn_frame.winfo_children():
                w.destroy()
            tk.Label(self.content_frame, text=result_text, font=("Segoe UI", 10),
                     fg="#404040", bg=self.win.cget("bg"),
                     anchor="w", justify="left", wraplength=360).pack(fill="x", pady=2)
            tk.Button(self.btn_frame, text="继续", font=("Segoe UI", 12),
                      fg="#000000", bg="#FFFFFF", activebackground="#F5F5F5",
                      bd=1, relief="solid", padx=12, pady=8,
                      command=lambda: self._finish_choice(idx)).pack(side="right", padx=4)
        else:
            self._finish_choice(idx)

    def _finish_choice(self, idx):
        self.win.destroy()
        if self.callback:
            self.callback(idx)

    def _follow(self):
        if self.win.winfo_exists():
            nx = self.pet_x + (self.pet_w - 400) // 2
            ny = self.pet_y - self.fixed_h - 12
            if ny < 0:
                ny = self.pet_y + self.pet_h + 12
            self.win.geometry(f"+{nx}+{ny}")
            self.win.after(200, self._follow)


class AdventureManager:
    def __init__(self, pet_state):
        self.pet_state = pet_state
        self.state = "idle"
        self.current_adventure_id = None
        self.current_stage_id = None
        self.pending_timer = None
        self.callback_on_stage = None

        if pet_state.active_adventure_id:
            self.current_adventure_id = pet_state.active_adventure_id
            self.current_stage_id = pet_state.active_adventure_stage
            self.pending_timer = pet_state.pending_adventure_timer
            self.state = "pending"

        self.adventure_pool = self._load_pool()
        self._current_adventure_data = None

    def _load_pool(self):
        from adventure_pool import ADVENTURES
        return {adv["id"]: adv for adv in ADVENTURES}

    def _get_adventure(self, adv_id):
        return self.adventure_pool.get(adv_id)

    def set_stage_callback(self, callback):
        self.callback_on_stage = callback

    def check_trigger(self, now=None, current_activity=""):
        if self.state == "active":
            return None

        if now is None:
            now = time.time()

        pet = self.pet_state

        if self.state == "pending":
            adv = self._get_adventure(self.current_adventure_id)
            if not adv:
                self._reset_to_idle()
                return None
            stage = adv["stages"].get(self.current_stage_id)
            if not stage:
                self._reset_to_idle()
                return None

            trigger = stage.get("stage_trigger")
            if not trigger:
                self._reset_to_idle()
                return None

            if not self._check_flags(trigger.get("flag_required", [])):
                return None

            trigger_type = trigger.get("trigger_type", "default")
            if trigger_type == "timer":
                if self.pending_timer and now >= self.pending_timer:
                    return self._start_stage(self.current_adventure_id, self.current_stage_id)
                else:
                    return None
            elif trigger_type == "item_use":
                return None
            else:
                if self._check_conditions(trigger, current_activity):
                    return self._start_stage(self.current_adventure_id, self.current_stage_id)
                else:
                    return None

        candidates = []
        for adv_id, adv in self.adventure_pool.items():
            if adv_id in pet.adventure_history:
                continue
            if self._check_conditions(adv.get("trigger", {}), current_activity):
                prob = adv.get("base_probability", 0.01)
                if random.random() < prob:
                    candidates.append(adv_id)

        if not candidates:
            return None

        chosen_id = random.choice(candidates)
        return self._start_adventure_entry(chosen_id)

    def _start_adventure_entry(self, adv_id):
        adv = self._get_adventure(adv_id)
        if not adv:
            return None
        entry_stage_id = list(adv["stages"].keys())[0]
        return self._start_stage(adv_id, entry_stage_id, is_entry=True)

    def _start_stage(self, adv_id, stage_id, is_entry=False):
        adv = self._get_adventure(adv_id)
        stage = adv["stages"][stage_id]
        self.state = "active"
        self.current_adventure_id = adv_id
        self.current_stage_id = stage_id
        self._current_adventure_data = adv
        return {
            "adventure_name": adv["name"],
            "stage_text": stage["text"],
            "options": stage.get("options", []),
            "location": stage.get("location", adv.get("location", "")),
            "is_entry": is_entry
        }

    def check_item_trigger(self, item_id):
        if self.state != "pending":
            return None

        adv = self._get_adventure(self.current_adventure_id)
        stage = adv["stages"].get(self.current_stage_id) if adv else None
        if not stage:
            return None

        trigger = stage.get("stage_trigger")
        if not trigger or trigger.get("trigger_type") != "item_use":
            return None
        if trigger.get("item_id") == item_id:
            if self._check_flags(trigger.get("flag_required", [])):
                return self._start_stage(self.current_adventure_id, self.current_stage_id)
        return None

    def proceed(self, option_index):
        if self.state != "active":
            return None

        adv = self._current_adventure_data
        stage = adv["stages"][self.current_stage_id]
        options = stage.get("options", [])

        if option_index < 0 or option_index >= len(options):
            return None

        chosen = options[option_index]
        effects = chosen.get("effects", {})
        self._apply_effects(effects)

        next_stage_id = chosen.get("next", "end")
        if next_stage_id == "end":
            self._complete_adventure()
            return None

        next_stage = adv["stages"].get(next_stage_id)
        if not next_stage:
            self._complete_adventure()
            return None

        if next_stage.get("stage_trigger"):
            self.state = "pending"
            self.current_stage_id = next_stage_id
            self._current_adventure_data = adv

            if "set_timer" in effects:
                self.pending_timer = time.time() + (effects["set_timer"] * 60)
            else:
                self.pending_timer = None

            self._save_pending_state()
            return {"pending": True}
        else:
            return self._start_stage(self.current_adventure_id, next_stage_id)

    def _apply_effects(self, effects):
        pet = self.pet_state
        if "mood" in effects:
            pet.mood = max(0, min(100, pet.mood + effects["mood"]))
        if "gold" in effects:
            pet.gold += effects["gold"]
        if "trait_add" in effects:
            trait = effects["trait_add"]
            if isinstance(trait, list):
                for t in trait:
                    pet.add_trait(t)
            else:
                pet.add_trait(trait)
        if "trait_remove" in effects:
            pet.remove_trait(effects["trait_remove"])
        if "set_flag" in effects:
            pet.set_flag(effects["set_flag"])
        if "remove_flag" in effects:
            pet.remove_flag(effects["remove_flag"])
        if "give_item" in effects:
            item = effects["give_item"].copy()
            item["origin_adventure"] = self.current_adventure_id
            pet.add_adventure_item(item)
        if "update_item_desc" in effects:
            info = effects["update_item_desc"]
            pet.update_adventure_item(info["id"], info["desc"])
        if "unlock_job" in effects:
            pet.unlock_job(effects["unlock_job"])
        if "unlock_event" in effects:
            pet.unlock_event(effects["unlock_event"])

    def _check_conditions(self, trigger, current_activity):
        pet = self.pet_state
        if "activity" in trigger:
            if current_activity != trigger["activity"]:
                return False
        if "charm_min" in trigger:
            if pet.charm < trigger["charm_min"]:
                return False
        if "mood_max" in trigger:
            if pet.mood > trigger["mood_max"]:
                return False
        if "gold_min" in trigger:
            if pet.gold < trigger["gold_min"]:
                return False
        if "time_range" in trigger:
            hour = time.localtime().tm_hour
            start, end = trigger["time_range"]
            if start <= end:
                if not (start <= hour < end):
                    return False
            else:
                if not (hour >= start or hour < end):
                    return False
        if "activity_count_min" in trigger:
            count = pet.activity_counts.get(trigger["activity"], 0)
            if count < trigger["activity_count_min"]:
                return False
        if "flag_required" in trigger:
            if not self._check_flags(trigger["flag_required"]):
                return False
        return True

    def _check_flags(self, required_flags):
        if not required_flags:
            return True
        for f in required_flags:
            if f not in self.pet_state.flags:
                return False
        return True

    def _complete_adventure(self):
        adv_id = self.current_adventure_id
        self.pet_state.adventure_history.append(adv_id)
        self._reset_to_idle()

    def _reset_to_idle(self):
        self.state = "idle"
        self.current_adventure_id = None
        self.current_stage_id = None
        self.pending_timer = None
        self._current_adventure_data = None
        self._clear_pending_state()

    def _save_pending_state(self):
        pet = self.pet_state
        pet.active_adventure_id = self.current_adventure_id
        pet.active_adventure_stage = self.current_stage_id
        pet.pending_adventure_timer = self.pending_timer

    def _clear_pending_state(self):
        pet = self.pet_state
        pet.active_adventure_id = None
        pet.active_adventure_stage = None
        pet.pending_adventure_timer = None

    # ---------- 背包 UI ----------
    def show_bag(self, parent):
        win = tk.Toplevel(parent)
        win.title("背包")
        win.configure(bg="white")
        win.geometry("300x400")
        win.resizable(False, False)

        tk.Label(win, text="📦 普通物品", font=("Segoe UI", 11, "bold"), bg="white", anchor="w").pack(fill="x", padx=10, pady=(10,0))
        inv = self.pet_state.inventory
        if inv:
            frame_inv = tk.Frame(win, bg="white")
            frame_inv.pack(fill="x", padx=10, pady=2)
            for name, qty in inv.items():
                tk.Label(frame_inv, text=f"{name} x{qty}", font=("Segoe UI", 10), bg="white", anchor="w").pack(fill="x", pady=1)
        else:
            tk.Label(win, text="（空）", bg="white", fg="gray", font=("Segoe UI", 9)).pack(anchor="w", padx=10)

        tk.Label(win, text="✨ 奇遇道具", font=("Segoe UI", 11, "bold"), bg="white", anchor="w").pack(fill="x", padx=10, pady=(12,0))
        items = self.pet_state.adventure_items
        if items:
            frame_adv = tk.Frame(win, bg="white")
            frame_adv.pack(fill="x", padx=10, pady=2)
            for item in items:
                row = tk.Frame(frame_adv, bg="white")
                row.pack(fill="x", pady=2)
                tk.Label(row, text=f"{item['name']}", font=("Segoe UI", 10), bg="white", anchor="w").pack(side="left")
                if item.get("usable", False):
                    tk.Button(row, text="使用", font=("Segoe UI", 10),
                              bg="white", fg="black", padx=8, pady=2,
                              command=lambda i=item: self._use_item(i, win)).pack(side="right")
        else:
            tk.Label(win, text="（无）", bg="white", fg="gray", font=("Segoe UI", 9)).pack(anchor="w", padx=10)

    def _use_item(self, item, bag_window):
        result = self.check_item_trigger(item["id"])
        if result:
            bag_window.destroy()
            if self.callback_on_stage:
                self.callback_on_stage(result)
        else:
            messagebox.showinfo("提示", "现在不是使用的时候", parent=bag_window)
