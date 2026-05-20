import tkinter as tk
from tkinter import simpledialog
import random
import os
import sys
import time
import threading
from PIL import Image, ImageTk, ImageDraw
import pystray

from utils import resource_path, SAVE_FILE, get_startup_status, set_startup, check_single_instance
from pet_state import PetState
from events import EventScheduler
from animation_manager import AnimationManager
from ui_manager import UIManager
from action_manager import ActionManager
from status_panel_manager import StatusPanelManager
from danmaku_manager import DanmakuManager
from companion_manager import CompanionManager
from adventure_manager import AdventureManager, AdventureStageWindow


class DesktopPet:
    def __init__(self, image_folder="pet_frames"):
        self.state = PetState()
        self.state.load()
        self.image_folder = image_folder
        self.active_notifications = []

        self.root = tk.Tk()
        self.root.title("练习生桌面宠物")
        self.root.geometry("1x1+9999+9999")
        self.root.withdraw()

        self.pet_win = tk.Toplevel(self.root)
        self.pet_win.overrideredirect(True)
        self.pet_win.wm_attributes("-topmost", True)
        self.pet_win.wm_attributes("-transparentcolor", "#F0F0F0")
        self.pet_win.configure(bg="#F0F0F0")
        self.pet_w = self.state.pet_w
        self.pet_h = self.state.pet_h
        self.x = self.pet_win.winfo_screenwidth() // 2
        self.y = self.pet_win.winfo_screenheight() // 2
        self.pet_win.geometry(f"{self.pet_w}x{self.pet_h}+{self.x}+{self.y}")

        self.bubble_win = tk.Toplevel(self.pet_win)
        self.bubble_win.overrideredirect(True)
        self.bubble_win.wm_attributes("-topmost", True)
        self.bubble_win.wm_attributes("-transparentcolor", "#F0F0F0")
        self.bubble_win.configure(bg="#F0F0F0")
        self.bubble_win.geometry(f"200x40+{self.x-20}+{self.y-50}")
        self.bubble_label = tk.Label(self.bubble_win, text="", fg="black", bg="#F0F0F0",
                                     font=("微软雅黑", 8), wraplength=190)
        self.bubble_label.pack()
        self.bubble_win.withdraw()

        self.anim_label = tk.Label(self.pet_win, bd=0, bg="#F0F0F0")
        self.anim_label.pack()
        self.pet_win.withdraw()

        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # 初始化管理器
        self.anim_manager = AnimationManager(self)
        self.ui_manager = UIManager(self)
        self.action_manager = ActionManager(self)
        self.status_panel_manager = StatusPanelManager(self)
        self.danmaku_manager = DanmakuManager(self)
        self.companion_manager = CompanionManager(self)

        # 奇遇管理器
        self.adventure_manager = AdventureManager(self.state)
        self.adventure_manager.set_stage_callback(self.show_adventure_stage)

        # 缓存与启动
        self.anim_manager.show_progress_bar("正在准备动画缓存，请稍候...")
        self.cache_thread = threading.Thread(target=self.anim_manager.generate_caches_async, daemon=True)
        self.cache_thread.start()
        self.root.after(100, self._check_cache_thread)

        self.performance_win = None
        self.shop_win = None
        self.danmu_win = None
        self.current_activity = None
        self.status_win = None
        self.toast_win = None
        self.current_activity_name = None

        self.tray = None
        self.create_tray()
        threading.Thread(target=self.tray.run, daemon=True).start()

        self.drag_data = {"x": 0, "y": 0}
        self.follow_windows = []

        self.event_scheduler = EventScheduler(
            self.state,
            self.ui_manager.show_toast,
            self.ui_manager.show_info,
            self.ui_manager.show_float_text,
            self.ui_manager.show_narrative_window,
            self.refresh_status,
            pet=self
        )

    # ---------- 缓存与启动 ----------
    def _check_cache_thread(self):
        if self.cache_thread and self.cache_thread.is_alive():
            self.root.after(100, self._check_cache_thread)
        else:
            if hasattr(self.anim_manager, 'progress_win') and self.anim_manager.progress_win:
                self.anim_manager.progress_win.destroy()
            self._on_cache_ready()

    def _on_cache_ready(self):
        self.anim_greet_frames, self.anim_idle_frames = self.anim_manager.load_current_anim_frames()
        self.static_img = None
        self.frames = []
        self.current_frame = 0
        self.has_image = self.anim_manager.load_frames(self.image_folder)
        if self.has_image:
            self.static_img = self.frames[0]
        else:
            img = Image.new("RGBA", (self.pet_w, self.pet_h), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((30,30,self.pet_w-30,self.pet_h-30), fill="orange", outline="white", width=2)
            self.static_img = ImageTk.PhotoImage(img)

        self.current_anim = None
        self.anim_index = 0
        self.anim_after_id = None

        if self.anim_greet_frames:
            self.anim_manager.play_animation(self.anim_greet_frames, loop=False, callback=self.anim_manager.switch_to_idle)
        else:
            self.anim_label.configure(image=self.static_img)

        self.bind_events()
        self.decay_timer()
        self.companion_manager.companion_loop()
        self.auto_save_loop()
        self.pet_win.deiconify()

    def bind_events(self):
        self.anim_label.bind("<Button-1>", self.start_drag)
        self.anim_label.bind("<B1-Motion>", self.on_drag)
        self.anim_label.bind("<Double-Button-1>", lambda e: self.hide_pet())
        self.anim_label.bind("<Button-3>", self.right_click_menu)

    # ---------- 奇遇回调 ----------
    def show_adventure_stage(self, stage_data):
        is_trigger = stage_data.get("is_entry", False)
        if is_trigger:
            # 先弹出触发提示窗
            def open_narrative():
                tip_win.destroy()
                # 重新调用，但这次不再走提示窗
                AdventureStageWindow(
                    self.pet_win,
                    stage_data["adventure_name"],
                    stage_data["stage_text"],
                    stage_data["options"],
                    self.on_adventure_choice,
                    self.x, self.y, self.pet_w, self.pet_h,
                    is_trigger=False   # 剧情窗用纯白背景
                )

            tip_win = tk.Toplevel(self.pet_win)
            tip_win.overrideredirect(True)
            tip_win.wm_attributes("-topmost", True)
            tip_win.configure(bg="#FFF8E1")
            tip_win.attributes("-alpha", 1.0)

            w, h = 360, 130
            pad = 20

            tk.Label(tip_win, text=f"✨ 奇遇触发 · {stage_data['adventure_name']}",
                     font=("Segoe UI", 12, "bold"), fg="#000000", bg="#FFF8E1"
                     ).pack(pady=(pad, 0))
            tk.Frame(tip_win, height=1, bg="#E5E5E5").pack(fill="x", padx=pad, pady=(8, 0))
            tk.Label(tip_win, text="一段不寻常的遭遇正在发生……",
                     font=("Segoe UI", 10), fg="#404040", bg="#FFF8E1"
                     ).pack(pady=(12, 0))
            tk.Button(tip_win, text="进入剧情", font=("Segoe UI", 11),
                      fg="#000000", bg="#FFFFFF", activebackground="#F5F5F5",
                      bd=1, relief="solid", padx=12, pady=12,
                      command=open_narrative).pack(pady=(12, pad))

            x = self.x + (self.pet_w - w) // 2
            y = self.y - h - 12
            if y < 0:
                y = self.y + self.pet_h + 12
            tip_win.geometry(f"{w}x{h}+{x}+{y}")

            def follow_tip():
                if tip_win.winfo_exists():
                    nx = self.x + (self.pet_w - w) // 2
                    ny = self.y - h - 12
                    if ny < 0:
                        ny = self.y + self.pet_h + 12
                    tip_win.geometry(f"+{nx}+{ny}")
                    tip_win.after(200, follow_tip)
            follow_tip()
            return   # 直接返回，不创建 AdventureStageWindow

        # 普通剧情窗口（包括后续阶段）
        AdventureStageWindow(
            self.pet_win,
            stage_data["adventure_name"],
            stage_data["stage_text"],
            stage_data["options"],
            self.on_adventure_choice,
            self.x, self.y, self.pet_w, self.pet_h,
            is_trigger=False
        )

    def on_adventure_choice(self, choice_index):
        next_stage = self.adventure_manager.proceed(choice_index)
        if next_stage:
            self.show_adventure_stage(next_stage)

    # ---------- 效果表 ----------
    feed_effect_map = {
        "超级食物碗": (20, lambda s: s.feed(30,5,0)),
        "波奇饭便当": (25, lambda s: s.feed(40,8,5)),
        "绿色排毒果汁": (15, lambda s: (setattr(s,'satiety',min(100,s.satiety+15)), s.gain_exp(3))),
        "牛肉沙拉碗": (35, lambda s: s.feed(55,10,8)),
        "泡菜豆腐锅": (40, lambda s: s.feed(50,5,10)),
        "荞麦冷面": (30, lambda s: s.feed(45,5,5)),
        "冰美式": (15, lambda s: (setattr(s,'satiety',min(100,s.satiety+5)), setattr(s,'stamina',min(100,s.stamina+15)), s.gain_exp(3))),
        "抹茶燕麦拿铁": (20, lambda s: (setattr(s,'satiety',min(100,s.satiety+10)), setattr(s,'stamina',min(100,s.stamina+5)), setattr(s,'mood',min(100,s.mood+20)), setattr(s,'charm',s.charm+3), s.gain_exp(3))),
        "燕麦拿铁": (20, lambda s: (setattr(s,'satiety',min(100,s.satiety+15)), setattr(s,'stamina',min(100,s.stamina+8)), setattr(s,'mood',min(100,s.mood+25)), s.gain_exp(3))),
        "气泡冷萃": (15, lambda s: (setattr(s,'satiety',min(100,s.satiety+5)), setattr(s,'stamina',min(100,s.stamina+20)), setattr(s,'mood',min(100,s.mood+10)), s.gain_exp(3))),
        "三角饭团": (10, lambda s: s.feed(25,3,0)),
        "能量香蕉": (8, lambda s: s.feed(15,8,0)),
    }
    skincare_effect_map = {
        "唇膜": (15, lambda s: (setattr(s,'charm',s.charm+5), setattr(s,'mood',min(100,s.mood+8)))),
        "眼膜": (20, lambda s: (setattr(s,'charm',s.charm+6),)),
        "清洁泥膜": (25, lambda s: (setattr(s,'hygiene',min(100,s.hygiene+30)), setattr(s,'charm',s.charm+8))),
        "补水面膜": (30, lambda s: (setattr(s,'charm',s.charm+10), setattr(s,'mood',min(100,s.mood+8)))),
        "面部刮痧": (35, lambda s: (setattr(s,'charm',s.charm+12), setattr(s,'mood',min(100,s.mood+5)))),
        "精华导入": (40, lambda s: (setattr(s,'hygiene',min(100,s.hygiene+10)), setattr(s,'charm',s.charm+15))),
        "一键精致护理": (60, lambda s: (setattr(s,'hygiene',min(100,s.hygiene+40)), setattr(s,'charm',s.charm+20), setattr(s,'mood',min(100,s.mood+15)))),
        "汗蒸排毒": (45, lambda s: (setattr(s,'hygiene',min(100,s.hygiene+70)), setattr(s,'mood',min(100,s.mood+10)), setattr(s,'charm',s.charm+8))),
        "全身按摩": (50, lambda s: (setattr(s,'stamina',min(100,s.stamina+40)), setattr(s,'mood',min(100,s.mood+30)))),
        "香薰水疗": (60, lambda s: (setattr(s,'hygiene',min(100,s.hygiene+100)), setattr(s,'stamina',min(100,s.stamina+10)), setattr(s,'mood',min(100,s.mood+40)), setattr(s,'charm',s.charm+12))),
    }

    # ---------- 右键菜单 ----------
    def right_click_menu(self, event):
        menu = tk.Menu(self.pet_win, tearoff=0)
        s = self.state
        inv = s.inventory

        feed_menu = tk.Menu(menu, tearoff=0)
        has_food = False
        for name, qty in inv.items():
            if name in self.feed_effect_map and qty > 0:
                dur, func = self.feed_effect_map[name]
                feed_menu.add_command(label=f"{name} (剩余{qty})", command=lambda n=name,d=dur,f=func: self.action_manager.use_inventory_item(n,d,f))
                has_food = True
        if not has_food:
            feed_menu.add_command(label="无食物", state="disabled")
        menu.add_cascade(label="🍽️ 喂食", menu=feed_menu)

        sc_menu = tk.Menu(menu, tearoff=0)
        has_skincare = False
        for name, qty in inv.items():
            if name in self.skincare_effect_map and qty > 0:
                dur, func = self.skincare_effect_map[name]
                sc_menu.add_command(label=f"{name} (剩余{qty})", command=lambda n=name,d=dur,f=func: self.action_manager.use_inventory_item(n,d,f))
                has_skincare = True
        if not has_skincare:
            sc_menu.add_command(label="无护肤用品", state="disabled")
        menu.add_cascade(label="✨ 洁护管理", menu=sc_menu)

        basic_menu = tk.Menu(menu, tearoff=0)
        basic_menu.add_command(label="🧴 洗手消毒 (免费)", command=lambda: self.action_manager.start_clean_action("洗手消毒",0,5,lambda s: setattr(s,'hygiene',min(100,s.hygiene+15))))
        basic_menu.add_command(label="🧽 快速洗脸 (免费)", command=lambda: self.action_manager.start_clean_action("快速洗脸",0,10,lambda s: setattr(s,'hygiene',min(100,s.hygiene+25))))
        basic_menu.add_command(label="🪥 刷牙 (免费)", command=lambda: self.action_manager.start_clean_action("刷牙",0,10,lambda s: (setattr(s,'hygiene',min(100,s.hygiene+20)), setattr(s,'charm',s.charm+3))))
        if inv.get("湿巾",0) > 0:
            basic_menu.add_command(label=f"🧻 湿巾擦拭 (剩余{inv['湿巾']})", command=lambda: self.action_manager.use_inventory_item("湿巾",12,lambda s: setattr(s,'hygiene',min(100,s.hygiene+40))))
        else:
            basic_menu.add_command(label="🧻 湿巾擦拭 (无库存)", state="disabled")
        basic_menu.add_command(label="🚿 快速淋浴 (免费)", command=lambda: self.action_manager.start_clean_action("快速淋浴",0,20,lambda s: (setattr(s,'hygiene',min(100,s.hygiene+80)), setattr(s,'stamina',min(100,s.stamina+5)), setattr(s,'mood',min(100,s.mood+5)))))
        basic_menu.add_command(label="🛁 泡澡 (免费)", command=lambda: self.action_manager.start_clean_action("泡澡",0,10,lambda s: (setattr(s,'hygiene',min(100,s.hygiene+100)), setattr(s,'stamina',min(100,s.stamina+10)), setattr(s,'mood',min(100,s.mood+20)))))
        menu.add_cascade(label="🧼 基础清洁", menu=basic_menu)

        if s.stage == 1:
            work_menu = tk.Menu(menu, tearoff=0)
            work_menu.add_command(label="🏪 便利店兼职 (+20💰)", command=lambda: self.action_manager.do_part_time_job("便利店兼职"))
            work_menu.add_command(label="☕ 咖啡店打工 (+15💰, ✨+3)", command=lambda: self.action_manager.do_part_time_job("咖啡店打工"))
            work_menu.add_command(label="📦 快递分拣 (+30💰, ⚡-15)", command=lambda: self.action_manager.do_part_time_job("快递分拣"))
            menu.add_cascade(label="💼 打工培训", menu=work_menu)

            train_menu = tk.Menu(menu, tearoff=0)
            train_menu.add_command(label="🎤 社区声乐班 (-30💰)", command=lambda: self.action_manager.buy_training("声乐班"))
            train_menu.add_command(label="💃 街舞入门课 (-30💰)", command=lambda: self.action_manager.buy_training("街舞课"))
            train_menu.add_command(label="🎭 表演兴趣班 (-30💰)", command=lambda: self.action_manager.buy_training("表演班"))
            if s.vocal >= 30:
                train_menu.add_command(label="🎤 进阶声乐班 (-60💰)", command=lambda: self.action_manager.buy_training("进阶声乐"))
            if s.dance >= 30:
                train_menu.add_command(label="💃 进阶舞蹈班 (-60💰)", command=lambda: self.action_manager.buy_training("进阶舞蹈"))
            menu.add_cascade(label="📚 自费培训", menu=train_menu)

            menu.add_command(label="🎤 街头表演", command=self.action_manager.street_performance)
            menu.add_separator()
            menu.add_command(label="🏢 主动面试", command=self.action_manager.start_interview)
        else:
            train_menu = tk.Menu(menu, tearoff=0)
            for label, t in [("🎤 声乐课","voice"),("💃 舞蹈集训","fitness"),("🎭 表演工作坊","expression"),("🏋️ 形体管理","shape")]:
                train_menu.add_command(label=label, command=lambda tp=t: self.action_manager.start_train(tp))
            menu.add_cascade(label="🏋️ 训练", menu=train_menu)

            if s.stage >= 5:
                menu.add_command(label="📺 接通告", command=self.action_manager.start_schedule)

            menu.add_command(label="😴 睡觉", command=self.sleep)

        menu.add_command(label="🛒 商店", command=self.status_panel_manager.open_shop)
        menu.add_command(label="💊 治疗", command=self.cure)
        menu.add_command(label="⏹️ 中止活动", command=self.action_manager.cancel_current_activity)
        menu.add_separator()

        zoom_menu = tk.Menu(menu, tearoff=0)
        zoom_menu.add_command(label="小 (1.5x)", command=lambda: self.anim_manager.set_scale(1.5))
        zoom_menu.add_command(label="中 (2.0x)", command=lambda: self.anim_manager.set_scale(2.0))
        zoom_menu.add_separator()
        zoom_menu.add_command(label="自定义倍数...", command=self.custom_scale)
        menu.add_cascade(label="🔲 缩放", menu=zoom_menu)

        menu.add_command(label="🎒 背包", command=self.status_panel_manager.show_inventory)
        menu.add_command(label="🎒 奇遇背包", command=lambda: self.adventure_manager.show_bag(self.pet_win))
        if self.state.focus_mode:
            menu.add_command(label="🍅 结束专注", command=self.toggle_focus)
        else:
            menu.add_command(label="🍅 开始专注 (25min)", command=self.toggle_focus)
        menu.add_command(label="隐藏到托盘", command=self.hide_pet)
        if get_startup_status():
            menu.add_command(label="✔ 开机自启：开", command=self.toggle_startup)
        else:
            menu.add_command(label="✔ 开机自启：关", command=self.toggle_startup)
        menu.add_command(label="📋 查看状态", command=self.status_panel_manager.show_status)
        menu.add_command(label="❌ 退出", command=self.quit_app)
        menu.post(event.x_root, event.y_root)

    # ---------- 基础操作 ----------
    def custom_scale(self):
        result = simpledialog.askfloat("自定义大小", "输入缩放倍数（例如 1.8）：",
                                       initialvalue=self.state.scale,
                                       minvalue=0.3, maxvalue=5.0)
        if result is not None and result > 0:
            self.anim_manager.show_progress_bar("正在生成新尺寸缓存...")
            self.anim_manager.ensure_cache_for_scale(result, "greet")
            self.anim_manager.ensure_cache_for_scale(result, "idle")
            if hasattr(self.anim_manager, 'progress_win') and self.anim_manager.progress_win:
                self.anim_manager.progress_win.destroy()
            self.anim_manager.set_scale(result)

    def sleep(self):
        self.state.sleep(40)
        self.state.save()
        self.refresh_status()

    def cure(self):
        self.state.cure()
        self.state.save()
        self.refresh_status()

    def toggle_focus(self):
        s = self.state
        if not s.focus_mode:
            s.focus_mode = True
            s.focus_end_time = time.time() + s.focus_duration
            self.ui_manager.show_toast("🍅 专注模式开始", 2000)
        else:
            s.focus_mode = False
            self.ui_manager.show_toast("专注模式已结束", 2000)
        s.save()

    def toggle_startup(self):
        if get_startup_status():
            set_startup(False)
            self.ui_manager.show_toast("开机自启已关闭")
        else:
            set_startup(True)
            self.ui_manager.show_toast("开机自启已开启")

    def show_pet(self, *args):
        self.pet_win.deiconify()
        self.pet_win.lift()

    def hide_pet(self, *args):
        self.pet_win.withdraw()

    def create_tray(self):
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((8, 8, 56, 56), fill="#8B5CF6")
        draw.ellipse((22, 22, 30, 30), fill="white")
        draw.ellipse((34, 22, 42, 30), fill="white")
        draw.arc((22, 34, 42, 44), start=0, end=180, fill="white", width=2)
        menu = pystray.Menu(
            pystray.MenuItem("状态面板", self.status_panel_manager.show_tray_status, default=True),
            pystray.MenuItem("显示宠物", self.show_pet),
            pystray.MenuItem("专注模式", self.toggle_focus),
            pystray.MenuItem("开机自启", self.toggle_startup, checked=lambda item: get_startup_status()),
            pystray.MenuItem("退出", self.quit_app)
        )
        self.tray = pystray.Icon("pet", img, "练习生", menu)

    def decay_timer(self):
        self.state.decay()
        self.refresh_status()
        self.root.after(15000, self.decay_timer)

    def refresh_status(self):
        self.status_panel_manager.refresh_status()

    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.x += dx
        self.y += dy
        self.pet_win.geometry(f"+{self.x}+{self.y}")
        if self.performance_win:
            self.performance_win.move_to(self.x, self.y)
        if self.current_activity:
            self.current_activity.pos_x = self.x + (self.pet_w - 280) // 2
            self.current_activity.pos_y = self.y + self.pet_h + 10
            self.current_activity.win.geometry(f"+{self.current_activity.pos_x}+{self.current_activity.pos_y}")
        self.move_notifications()

        for win, update_func in self.follow_windows[:]:
            if win.winfo_exists():
                update_func()
            else:
                self.follow_windows.remove((win, update_func))

    def register_follow_window(self, win, update_func):
        for w, _ in self.follow_windows:
            if w is win:
                return
        self.follow_windows.append((win, update_func))

    def unregister_follow_window(self, win):
        self.follow_windows = [(w, f) for w, f in self.follow_windows if w != win]

    def move_notifications(self):
        for popup in self.active_notifications[:]:
            try:
                if popup.winfo_exists():
                    pet_x = self.pet_win.winfo_x()
                    pet_y = self.pet_win.winfo_y()
                    popup.geometry(f"+{pet_x + self.pet_w + 5}+{pet_y + 5}")
            except:
                if popup in self.active_notifications:
                    self.active_notifications.remove(popup)

    def auto_save_loop(self):
        self.state.save()
        self.root.after(30000, self.auto_save_loop)

    def quit_app(self, *args):
        self.state.save()
        if self.tray:
            self.tray.stop()
        self.bubble_win.destroy()
        self.pet_win.destroy()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    if not check_single_instance():
        import tkinter.messagebox
        tk.messagebox.showwarning("已运行", "练习生桌面宠物已经在运行中，不能重复打开。")
        sys.exit(0)
    pet = DesktopPet(image_folder=resource_path("pet_frames"))
    pet.run()
