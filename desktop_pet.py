import tkinter as tk
from tkinter import ttk, simpledialog
import random
import os
import sys
import time
import threading
from PIL import Image, ImageTk, ImageDraw
import pystray
import ctypes
import imageio
import numpy as np

from utils import resource_path, SAVE_FILE, get_startup_status, set_startup, check_single_instance
from pet_state import PetState
from activity_window import ActivityWindow
from shop_window import ShopWindow
from status_window import StatusWindow
from performance_window import PerformanceWindow
from activity_monitor import ActivityMonitor
from events import EventScheduler

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

        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.show_progress_bar("正在准备动画缓存，请稍候...")
        self.cache_thread = threading.Thread(target=self._generate_caches_async, daemon=True)
        self.cache_thread.start()
        self.root.after(100, self._check_cache_thread)

        self.performance_win = None
        self.shop_win = None
        self.danmu_win = None
        self.current_activity = None
        self.toast_win = None
        self.status_win = None

        self.tray = None
        self.create_tray()
        threading.Thread(target=self.tray.run, daemon=True).start()

        self.drag_data = {"x": 0, "y": 0}

        self.event_scheduler = EventScheduler(
            self.state,
            self.show_toast,
            self.show_info,
            self.show_float_text,
            self.show_narrative_window,
            self.refresh_status
        )

    # ---------- 后台缓存生成 ----------
    def _generate_caches_async(self):
        scales = [1.5, 2.0]
        for scale in scales:
            if not self.cache_exists(scale, "greet"):
                self.ensure_cache_for_scale(scale, "greet")
            if not self.cache_exists(scale, "idle"):
                self.ensure_cache_for_scale(scale, "idle")
            if not self.cache_exists(scale, "store"):
                self.ensure_cache_for_scale(scale, "store")

    def _check_cache_thread(self):
        if self.cache_thread and self.cache_thread.is_alive():
            self.root.after(100, self._check_cache_thread)
        else:
            if hasattr(self, 'progress_win') and self.progress_win:
                self.progress_win.destroy()
            self._on_cache_ready()

    def _on_cache_ready(self):
        self.anim_greet_frames, self.anim_idle_frames = self.load_current_anim_frames()
        self.static_img = None
        self.frames = []
        self.current_frame = 0
        self.has_image = self.load_frames(self.image_folder)
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
            self.play_animation(self.anim_greet_frames, loop=False, callback=self.switch_to_idle)
        else:
            self.anim_label.configure(image=self.static_img)

        self.bind_events()
        self.decay_timer()
        self.companion_loop()
        self.auto_save_loop()

    def show_progress_bar(self, title):
        self.progress_win = tk.Toplevel(self.root)
        self.progress_win.title("加载中")
        self.progress_win.geometry("300x100")
        self.progress_win.resizable(False, False)
        self.progress_win.update_idletasks()
        sw = self.progress_win.winfo_screenwidth()
        sh = self.progress_win.winfo_screenheight()
        x = (sw - 300) // 2
        y = (sh - 100) // 2
        self.progress_win.geometry(f"+{x}+{y}")
        tk.Label(self.progress_win, text=title, font=("微软雅黑", 11)).pack(pady=15)
        self.progress_bar = ttk.Progressbar(self.progress_win, length=250, mode='indeterminate')
        self.progress_bar.pack(pady=10)
        self.progress_bar.start(10)
        self.progress_win.lift()

    def cache_exists(self, scale, base_name):
        cache_dir = os.path.join(self.base_dir, f"{base_name}_{scale}x_frames")
        return os.path.isdir(cache_dir) and os.listdir(cache_dir)

    def ensure_cache_for_scale(self, scale, base_name):
        cache_dir = os.path.join(self.base_dir, f"{base_name}_{scale}x_frames")
        if not os.path.isdir(cache_dir) or not os.listdir(cache_dir):
            video_path = None
            for ext in [".webm", ".mp4"]:
                candidate = os.path.join(self.base_dir, f"{base_name}{ext}")
                if os.path.exists(candidate):
                    video_path = candidate
                    break
            if video_path:
                w = int(160 * scale)
                h = int(220 * scale)
                self.process_video_to_cache(video_path, cache_dir, w, h)

    def process_video_to_cache(self, video_path, cache_dir, target_w, target_h):
        try:
            reader = imageio.get_reader(video_path)
            os.makedirs(cache_dir, exist_ok=True)
            ref_r, ref_g, ref_b = 149, 93, 190
            max_dist = 80
            bg_color = (240, 240, 240, 255)
            for i, frame in enumerate(reader):
                img = Image.fromarray(frame).convert("RGBA")
                arr = np.array(img)
                # 距离紫色
                diff = arr[:,:,:3].astype(np.float32) - np.array([ref_r, ref_g, ref_b], dtype=np.float32)
                dist_purple = np.sqrt(np.sum(diff**2, axis=2))
                # 饱和度 = max(r,g,b) - min(r,g,b)
                max_rgb = np.max(arr[:,:,:3], axis=2)
                min_rgb = np.min(arr[:,:,:3], axis=2)
                saturation = max_rgb - min_rgb
                # 舌头保护区：R高 且 B低（#db5e61 = R219, G94, B97）
                is_tongue = (arr[:,:,0] > 180) & (arr[:,:,2] < 140)
                # 紫色区域：距离小 + 不透明 + 饱和度高（排除灰色） + 不是舌头
                is_purple = (dist_purple < max_dist) & (arr[:,:,3] > 200) & (saturation > 25)
                mask = is_purple & (~is_tongue)
                arr[mask] = bg_color
                img = Image.fromarray(arr)
                img.thumbnail((target_w, target_h), Image.LANCZOS)
                canvas = Image.new("RGBA", (target_w, target_h), bg_color)
                paste_x = (target_w - img.width) // 2
                paste_y = (target_h - img.height) // 2
                canvas.paste(img, (paste_x, paste_y), img)
                canvas.save(os.path.join(cache_dir, f"frame_{i:04d}.png"))
            reader.close()
        except Exception as e:
            print(f"生成缓存失败 {cache_dir}: {e}")

    def load_current_anim_frames(self):
        scale = self.state.scale
        greet_dir = os.path.join(self.base_dir, f"greet_{scale}x_frames")
        idle_dir = os.path.join(self.base_dir, f"idle_{scale}x_frames")
        greet_frames = self.load_png_frames(greet_dir)
        idle_frames = self.load_png_frames(idle_dir) if os.path.isdir(idle_dir) else None
        return greet_frames, idle_frames

    def set_scale(self, scale):
        self.state.scale = scale
        self.state.save()
        self.pet_w = self.state.pet_w
        self.pet_h = self.state.pet_h
        self.pet_win.geometry(f"{self.pet_w}x{self.pet_h}+{self.x}+{self.y}")
        self.anim_greet_frames, self.anim_idle_frames = self.load_current_anim_frames()
        self.static_img = None
        self.frames = []
        self.has_image = self.load_frames(self.image_folder) if os.path.isdir(self.image_folder) else False
        if self.has_image:
            self.static_img = self.frames[0]
        else:
            img = Image.new("RGBA", (self.pet_w, self.pet_h), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((30,30,self.pet_w-30,self.pet_h-30), fill="orange", outline="white", width=2)
            self.static_img = ImageTk.PhotoImage(img)
        if self.current_anim is not None:
            if self.anim_after_id:
                self.pet_win.after_cancel(self.anim_after_id)
            if self.current_anim == self.anim_greet_frames:
                self.play_animation(self.anim_greet_frames, loop=False, callback=self.switch_to_idle)
            elif self.current_anim == self.anim_idle_frames:
                self.play_animation(self.anim_idle_frames, loop=True)
            else:
                self.anim_label.configure(image=self.static_img)
        else:
            self.anim_label.configure(image=self.static_img)
        if self.bubble_win and self.bubble_win.winfo_exists():
            self.bubble_win.geometry(f"200x40+{self.x-20}+{self.y-50}")

    def load_png_frames(self, folder_path):
        if not os.path.isdir(folder_path):
            return None
        files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith('.png')])
        if not files:
            return None
        frames = []
        for f in files:
            img = Image.open(os.path.join(folder_path, f)).convert("RGBA")
            frames.append(ImageTk.PhotoImage(img))
        return frames

    def load_frames(self, folder):
        if not os.path.isdir(folder):
            return False
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith((".png",".gif"))])
        if not files:
            return False
        for f in files:
            try:
                img = Image.open(os.path.join(folder, f)).convert("RGBA")
                img.thumbnail((self.pet_w, self.pet_h), Image.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(img))
            except:
                pass
        return len(self.frames) > 0

    def play_animation(self, anim_list, loop=False, callback=None):
        if self.anim_after_id:
            self.pet_win.after_cancel(self.anim_after_id)
        self.current_anim = anim_list
        self.anim_index = 0
        self._animate_frame(loop, callback)

    def _animate_frame(self, loop, callback):
        if not self.current_anim:
            return
        if self.anim_index >= len(self.current_anim):
            if loop:
                self.anim_index = 0
            else:
                if callback:
                    callback()
                return
        frame = self.current_anim[self.anim_index]
        self.anim_label.configure(image=frame)
        self.anim_index += 1
        self.anim_after_id = self.pet_win.after(50, self._animate_frame, loop, callback)

    def switch_to_idle(self):
        if self.anim_idle_frames:
            self.play_animation(self.anim_idle_frames, loop=True)
        else:
            if self.static_img:
                self.anim_label.configure(image=self.static_img)

    # ---------- 便利店打工动画 ----------
    def play_store_animation(self):
        """播放便利店打工动画（循环），直到被停止"""
        self.ensure_cache_for_scale(self.state.scale, "store")
        cache_dir = os.path.join(self.base_dir, f"store_{self.state.scale}x_frames")
        frames = self.load_png_frames(cache_dir)
        if frames:
            self.play_animation(frames, loop=True)

    def bind_events(self):
        self.anim_label.bind("<Button-1>", self.start_drag)
        self.anim_label.bind("<B1-Motion>", self.on_drag)
        self.anim_label.bind("<Double-Button-1>", lambda e: self.hide_pet())
        self.anim_label.bind("<Button-3>", self.right_click_menu)

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

    def right_click_menu(self, event):
        menu = tk.Menu(self.pet_win, tearoff=0)
        s = self.state
        inv = s.inventory

        feed_menu = tk.Menu(menu, tearoff=0)
        has_food = False
        for name, qty in inv.items():
            if name in self.feed_effect_map and qty > 0:
                dur, func = self.feed_effect_map[name]
                feed_menu.add_command(label=f"{name} (剩余{qty})", command=lambda n=name,d=dur,f=func: self.use_inventory_item(n,d,f))
                has_food = True
        if not has_food:
            feed_menu.add_command(label="无食物", state="disabled")
        menu.add_cascade(label="🍽️ 喂食", menu=feed_menu)

        sc_menu = tk.Menu(menu, tearoff=0)
        has_skincare = False
        for name, qty in inv.items():
            if name in self.skincare_effect_map and qty > 0:
                dur, func = self.skincare_effect_map[name]
                sc_menu.add_command(label=f"{name} (剩余{qty})", command=lambda n=name,d=dur,f=func: self.use_inventory_item(n,d,f))
                has_skincare = True
        if not has_skincare:
            sc_menu.add_command(label="无护肤用品", state="disabled")
        menu.add_cascade(label="✨ 洁护管理", menu=sc_menu)

        basic_menu = tk.Menu(menu, tearoff=0)
        basic_menu.add_command(label="🧴 洗手消毒 (免费)", command=lambda: self.start_activity("洗手消毒",0,5,lambda s: setattr(s,'hygiene',min(100,s.hygiene+15))))
        basic_menu.add_command(label="🧽 快速洗脸 (免费)", command=lambda: self.start_activity("快速洗脸",0,8,lambda s: setattr(s,'hygiene',min(100,s.hygiene+25))))
        basic_menu.add_command(label="🪥 刷牙 (免费)", command=lambda: self.start_activity("刷牙",0,10,lambda s: (setattr(s,'hygiene',min(100,s.hygiene+20)), setattr(s,'charm',s.charm+3))))
        if inv.get("湿巾",0) > 0:
            basic_menu.add_command(label=f"🧻 湿巾擦拭 (剩余{inv['湿巾']})", command=lambda: self.use_inventory_item("湿巾",12,lambda s: setattr(s,'hygiene',min(100,s.hygiene+40))))
        else:
            basic_menu.add_command(label="🧻 湿巾擦拭 (无库存)", state="disabled")
        basic_menu.add_command(label="🚿 快速淋浴 (免费)", command=lambda: self.start_activity("快速淋浴",0,20,lambda s: (setattr(s,'hygiene',min(100,s.hygiene+80)), setattr(s,'stamina',min(100,s.stamina+5)), setattr(s,'mood',min(100,s.mood+5)))))
        basic_menu.add_command(label="🛁 泡澡 (免费)", command=lambda: self.start_activity("泡澡",0,50,lambda s: (setattr(s,'hygiene',min(100,s.hygiene+100)), setattr(s,'stamina',min(100,s.stamina+10)), setattr(s,'mood',min(100,s.mood+20)))))
        menu.add_cascade(label="🧼 基础清洁", menu=basic_menu)

        if s.stage == 1:
            work_menu = tk.Menu(menu, tearoff=0)
            work_menu.add_command(label="🏪 便利店兼职 (+20💰)", command=lambda: self.do_part_time_job("便利店兼职"))
            work_menu.add_command(label="☕ 咖啡店打工 (+15💰, ✨+3)", command=lambda: self.do_part_time_job("咖啡店打工"))
            work_menu.add_command(label="📦 快递分拣 (+30💰, ⚡-15)", command=lambda: self.do_part_time_job("快递分拣"))
            menu.add_cascade(label="💼 打工培训", menu=work_menu)

            train_menu = tk.Menu(menu, tearoff=0)
            train_menu.add_command(label="🎤 社区声乐班 (-30💰)", command=lambda: self.buy_training("声乐班"))
            train_menu.add_command(label="💃 街舞入门课 (-30💰)", command=lambda: self.buy_training("街舞课"))
            train_menu.add_command(label="🎭 表演兴趣班 (-30💰)", command=lambda: self.buy_training("表演班"))
            if s.vocal >= 30:
                train_menu.add_command(label="🎤 进阶声乐班 (-60💰)", command=lambda: self.buy_training("进阶声乐"))
            if s.dance >= 30:
                train_menu.add_command(label="💃 进阶舞蹈班 (-60💰)", command=lambda: self.buy_training("进阶舞蹈"))
            menu.add_cascade(label="📚 自费培训", menu=train_menu)

            menu.add_command(label="🎤 街头表演", command=self.street_performance)
            menu.add_separator()
            menu.add_command(label="🏢 主动面试", command=self.start_interview)
        else:
            train_menu = tk.Menu(menu, tearoff=0)
            for label, t in [("🎤 声乐课","voice"),("💃 舞蹈集训","fitness"),("🎭 表演工作坊","expression"),("🏋️ 形体管理","shape")]:
                train_menu.add_command(label=label, command=lambda tp=t: self.start_train(tp))
            menu.add_cascade(label="🏋️ 训练", menu=train_menu)

            if s.stage >= 5:
                menu.add_command(label="📺 接通告", command=self.start_schedule)

            menu.add_command(label="😴 睡觉", command=self.sleep)

        menu.add_command(label="🛒 商店", command=self.open_shop)
        menu.add_command(label="💊 治疗", command=self.cure)
        menu.add_separator()

        zoom_menu = tk.Menu(menu, tearoff=0)
        zoom_menu.add_command(label="小 (1.5x)", command=lambda: self.set_scale(1.5))
        zoom_menu.add_command(label="中 (2.0x)", command=lambda: self.set_scale(2.0))
        zoom_menu.add_separator()
        zoom_menu.add_command(label="自定义倍数...", command=self.custom_scale)
        menu.add_cascade(label="🔲 缩放", menu=zoom_menu)

        menu.add_command(label="🎒 背包", command=self.show_inventory)
        if self.state.focus_mode:
            menu.add_command(label="🍅 结束专注", command=self.toggle_focus)
        else:
            menu.add_command(label="🍅 开始专注 (25min)", command=self.toggle_focus)
        menu.add_command(label="隐藏到托盘", command=self.hide_pet)
        if get_startup_status():
            menu.add_command(label="✔ 开机自启：开", command=self.toggle_startup)
        else:
            menu.add_command(label="✔ 开机自启：关", command=self.toggle_startup)
        menu.add_command(label="📋 查看状态", command=self.show_status)
        menu.add_command(label="❌ 退出", command=self.quit_app)
        menu.post(event.x_root, event.y_root)

    def custom_scale(self):
        result = simpledialog.askfloat("自定义大小", "输入缩放倍数（例如 1.8）：",
                                       initialvalue=self.state.scale,
                                       minvalue=0.3, maxvalue=5.0)
        if result is not None and result > 0:
            self.show_progress_bar("正在生成新尺寸缓存...")
            self.ensure_cache_for_scale(result, "greet")
            self.ensure_cache_for_scale(result, "idle")
            if hasattr(self, 'progress_win') and self.progress_win:
                self.progress_win.destroy()
            self.set_scale(result)

    def do_part_time_job(self, job):
        s = self.state
        if job == "便利店兼职":
            self.play_store_animation()          # 开始打工动画
            duration = 3600
            game_hours = 1
            def effect(state):
                state.gold += 20
                state.gain_exp(5)
                self.switch_to_idle()            # 打工结束切回待机
        elif job == "咖啡店打工":
            duration = 3600
            game_hours = 1
            def effect(state):
                state.gold += 15
                state.charm += 3
                state.gain_exp(5)
        elif job == "快递分拣":
            duration = 5400
            game_hours = 1.5
            def effect(state):
                state.gold += 30
                state.stamina = max(0, state.stamina - 15)
                state.gain_exp(5)
        else:
            return
        self.start_activity(job, 0, duration, effect, game_hours=game_hours)

    def buy_training(self, course):
        s = self.state
        if "进阶" in course:
            cost = 60
            gain = 15
            duration = 5400
            game_hours = 1.5
        else:
            cost = 30
            gain = 8
            duration = 3600
            game_hours = 1
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

        self.start_activity(course, cost, duration, effect, game_hours=game_hours)

    def street_performance(self):
        s = self.state
        gain = random.randint(1, 5)
        is_vocal = random.random() < 0.5

        def effect(state):
            if is_vocal:
                state.vocal += gain
            else:
                state.dance += gain
            state.charm += 5
            state.gain_exp(5)

        self.start_activity("街头表演", 0, 3600, effect, game_hours=1)

    def start_interview(self):
        s = self.state
        total = s.vocal + s.dance + s.charm
        if total >= 90 and s.vocal >= 25 and s.dance >= 25 and s.charm >= 25:
            s.promote(2, "见习练习生 🎓")
            self.show_toast("面试通过！成为见习练习生")
        else:
            self.show_info("面试未通过，继续努力吧")
        s.save()

    def show_inventory(self):
        inv = self.state.inventory
        win = tk.Toplevel(self.pet_win)
        win.title("背包")
        win.geometry("300x400")
        tk.Label(win, text="🎒 背包", font=("微软雅黑",14,"bold")).pack(pady=10)
        if not inv:
            tk.Label(win, text="背包空空如也").pack()
        else:
            for name, qty in inv.items():
                tk.Label(win, text=f"{name} x{qty}", font=("微软雅黑",10)).pack(anchor="w", padx=20, pady=2)

    def use_inventory_item(self, name, duration, effect_func):
        if self.state.inventory.get(name,0) <= 0:
            self.show_info("背包中没有该物品！")
            return
        self.state.inventory[name] -= 1
        if self.state.inventory[name] == 0:
            del self.state.inventory[name]
        self.show_toast(f"使用 {name}")
        self.start_activity(name, 0, duration, effect_func)

    def start_activity(self, name, price, duration, effect_func, game_hours=0):
        s = self.state
        if price > 0 and s.gold < price:
            self.show_info("金币不足！")
            return
        if price > 0:
            s.gold -= price

        self.event_scheduler.set_action(name)

        def on_finish():
            effect_func(s)
            if game_hours > 0:
                s.game_time.advance_hours(game_hours)
            self.show_toast(f"✅ {name}完成")
            s.save()
            self.refresh_status()
            self.event_scheduler.set_action(None)

        def on_cancel():
            if price > 0:
                s.gold += price
            self.show_toast(f"❌ {name}已取消")
            s.save()
            self.event_scheduler.set_action(None)

        self.current_activity = ActivityWindow(self.pet_win, f"{name}中...", duration, on_finish, on_cancel,
                                               pet_x=self.x, pet_y=self.y, pet_w=self.pet_w, pet_h=self.pet_h)

    def start_train(self, type_):
        ok, msg = self.state.train(type_)
        if not ok:
            self.show_info(msg)
            return
        self.event_scheduler.set_action(f"训练-{type_}")
        self.performance_win = PerformanceWindow(self.pet_win, self.state, "train", type_,
                                                 callback=self.on_activity_end, pet_x=self.x, pet_y=self.y,
                                                 pet_w=self.pet_w, pet_h=self.pet_h)

    def start_schedule(self):
        ok, msg = self.state.do_schedule()
        if not ok:
            self.show_info(msg)
            return
        self.event_scheduler.set_action("接通告")
        self.performance_win = PerformanceWindow(self.pet_win, self.state, "schedule", "",
                                                 callback=self.on_activity_end, pet_x=self.x, pet_y=self.y,
                                                 pet_w=self.pet_w, pet_h=self.pet_h)

    def on_activity_end(self, msg=None):
        self.performance_win = None
        if msg:
            self.show_info(msg)
        self.state.save()
        self.refresh_status()
        self.event_scheduler.set_action(None)

    def show_info(self, msg):
        self.pet_win.update_idletasks()
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.wm_attributes("-topmost", True)
        popup.configure(bg="black")
        tk.Label(popup, text=msg, fg="white", bg="black", font=("微软雅黑", 10)).pack(padx=10, pady=5)
        popup.update_idletasks()
        pet_x = self.pet_win.winfo_x()
        pet_y = self.pet_win.winfo_y()
        popup.geometry(f"+{pet_x + self.pet_w + 5}+{pet_y + 5}")
        self.active_notifications.append(popup)
        def destroy_popup():
            if popup in self.active_notifications:
                self.active_notifications.remove(popup)
            popup.destroy()
        popup.after(2000, destroy_popup)

    def show_toast(self, msg, duration=1500):
        if hasattr(self, 'toast_win') and self.toast_win and self.toast_win.winfo_exists():
            self.toast_win.destroy()
        self.pet_win.update_idletasks()
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.wm_attributes("-topmost", True)
        toast.wm_attributes("-alpha", 0.85)
        toast.configure(bg="#333333")
        tk.Label(toast, text=msg, fg="white", bg="#333333", font=("微软雅黑", 9, "bold"), padx=8, pady=2).pack()
        toast.update_idletasks()
        pet_x = self.pet_win.winfo_x()
        pet_y = self.pet_win.winfo_y()
        toast.geometry(f"+{pet_x + self.pet_w + 5}+{pet_y + 5}")
        self.active_notifications.append(toast)
        def destroy_toast():
            if toast in self.active_notifications:
                self.active_notifications.remove(toast)
            toast.destroy()
        toast.after(duration, destroy_toast)
        self.toast_win = toast

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

    def show_narrative_window(self, text, title=""):
        win = tk.Toplevel(self.pet_win)
        win.overrideredirect(True)
        win.wm_attributes("-topmost", True)
        win.configure(bg="#2E2E2E")
        win.attributes("-alpha", 0.92)
        
        w = 340
        
        temp_label = tk.Label(win, text=text, font=("微软雅黑", 10),
                              fg="white", bg="#2E2E2E",
                              wraplength=300, justify="left")
        win.update_idletasks()
        req_height = temp_label.winfo_reqheight()
        temp_label.destroy()
        
        title_height = 30 if title else 0
        btn_height = 40
        pad_total = 50
        
        h = req_height + title_height + btn_height + pad_total
        if h < 130:
            h = 130
        if h > 400:
            h = 400
        
        x = self.x + (self.pet_w - w) // 2
        y = self.y - h - 10
        if y < 0:
            y = self.y + self.pet_h + 10
        win.geometry(f"{w}x{h}+{x}+{y}")
        
        if title:
            title_label = tk.Label(win, text=title, font=("微软雅黑", 11, "bold"),
                                   fg="#FFD700", bg="#2E2E2E")
            title_label.pack(pady=(10, 0))
        
        desc_label = tk.Label(win, text=text, font=("微软雅黑", 10),
                              fg="white", bg="#2E2E2E",
                              wraplength=300, justify="left")
        desc_label.pack(pady=10, padx=20)
        
        close_btn = tk.Button(win, text="我知道了", command=win.destroy,
                              bg="#555555", fg="white", font=("微软雅黑", 9))
        close_btn.pack(pady=(0, 10))
        
        auto_close_ms = int(max(3000, min(15000, len(text) * 300)))
        win.after(auto_close_ms, lambda: win.destroy() if win.winfo_exists() else None)
        
        def follow():
            if win.winfo_exists():
                nx = self.x + (self.pet_w - w) // 2
                ny = self.y - h - 10
                if ny < 0:
                    ny = self.y + self.pet_h + 10
                win.geometry(f"+{nx}+{ny}")
                win.after(200, follow)
        follow()

    def refresh_status(self):
        if self.status_win and self.status_win.win.winfo_exists():
            self.status_win.refresh()

    def show_float_text(self, texts):
        base_x = self.x + self.pet_w // 2
        base_y = self.y - 20
        for i, text in enumerate(texts):
            offset_x = (i % 3 - 1) * 50
            offset_y = -(i // 3) * 30
            win = tk.Toplevel(self.pet_win)
            win.overrideredirect(True)
            win.wm_attributes("-topmost", True)
            win.wm_attributes("-transparentcolor", "#F0F0F0")
            win.configure(bg="#F0F0F0")
            label = tk.Label(win, text=text, font=("微软雅黑", 14, "bold"),
                             fg="#FFD700", bg="#F0F0F0")
            label.pack()
            win.geometry(f"+{base_x + offset_x}+{base_y + offset_y}")
            self._animate_float(win, 0)

    def _animate_float(self, win, step):
        if not win.winfo_exists():
            return
        if step >= 40:
            win.destroy()
            return
        x = win.winfo_x()
        y = win.winfo_y() - 1
        alpha = 1.0 - step / 40
        win.wm_attributes("-alpha", alpha)
        win.geometry(f"+{x}+{y}")
        self.root.after(50, lambda: self._animate_float(win, step + 1))

    def show_danmu(self):
        s = self.state
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
        if self.danmu_win and self.danmu_win.winfo_exists():
            self.danmu_win.destroy()
        danmu = tk.Toplevel(self.pet_win)
        danmu.overrideredirect(True)
        danmu.wm_attributes("-topmost", True)
        danmu.wm_attributes("-alpha", 0.8)
        danmu.configure(bg="black")
        sx = self.x + self.pet_w//2
        sy = self.y - 10
        danmu.geometry(f"+{sx}+{sy}")
        tk.Label(danmu, text=text, fg="white", bg="black", font=("微软雅黑", 9), padx=5, pady=2).pack()
        self.danmu_win = danmu
        self.animate_danmu(sx, sy)

    def animate_danmu(self, x, y, step=0):
        if step > 40 or not self.danmu_win or not self.danmu_win.winfo_exists():
            if self.danmu_win:
                self.danmu_win.destroy()
                self.danmu_win = None
            return
        x -= 2
        y -= 1
        self.danmu_win.geometry(f"+{x}+{y}")
        if step > 20:
            self.danmu_win.wm_attributes("-alpha", max(0.2, 0.8-(step-20)*0.03))
        self.root.after(100, lambda: self.animate_danmu(x, y, step+1))

    def companion_loop(self):
        s = self.state
        now = time.time()
        idle = ActivityMonitor.get_idle_seconds()
        s.idle_time = idle
        s.total_playtime += 1
        gt = s.game_time
        if gt.week > s.last_milestone_week:
            s.last_milestone_week = gt.week
            self.show_toast(f"🎉 第{gt.week}周纪念！一起加油哦！", 3000)
        if gt.day > s.last_milestone_day and gt.day % 100 == 0:
            s.last_milestone_day = gt.day
            self.show_toast(f"🎈 一起走过{gt.day}天！", 3000)
        if s.focus_mode and now > s.focus_end_time:
            s.focus_mode = False
            self.show_toast("🍅 专注时间结束！", 3000)
        if not s.focus_mode and not s.resting:
            if idle > s.idle_threshold:
                self.show_toast("💺 坐太久啦，起来活动一下！")
                s.idle_time = 0
            if now - s.last_water_reminder > s.water_interval:
                self.show_toast("💧 喝点水吧～")
                s.last_water_reminder = now
            if now - s.last_eye_reminder > s.eye_interval:
                self.show_toast("👀 休息一下眼睛哦")
                s.last_eye_reminder = now
        if not s.focus_mode and now - s.last_danmu_time > s.danmu_interval:
            self.show_danmu()
            s.last_danmu_time = now
            s.danmu_interval = random.randint(120, 300)
        self.check_daytime_greeting(now)

        # 随机事件检查
        self.event_scheduler.update(self.pet_win)

        self.root.after(1000, self.companion_loop)

    def check_daytime_greeting(self, now):
        s = self.state
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
            self.show_toast("☀️ 早上好！今天也要加油哦！", 3000)
            s._greeted_morning = True
        elif not s._greeted_night and 22 <= hour <= 23:
            self.show_toast("🌙 晚安，早点休息～", 3000)
            s._greeted_night = True
        elif not s._greeted_night and hour >= 2:
            self.show_toast("😟 还不休息吗？", 3000)
            s._greeted_night = True

    def sleep(self):
        self.state.sleep(40)
        self.state.save()
        self.refresh_status()

    def cure(self):
        self.state.cure()
        self.state.save()
        self.refresh_status()

    def open_shop(self):
        if self.shop_win and self.shop_win.win.winfo_exists():
            self.shop_win.win.lift()
            return
        self.shop_win = ShopWindow(self.pet_win, self.state)

    def show_status(self):
        if self.status_win and self.status_win.win.winfo_exists():
            self.status_win.win.lift()
            return
        self.status_win = StatusWindow(self.pet_win, self.state)
        self.status_win.win.geometry(f"+{self.x+self.pet_w+10}+{self.y}")
        
        def on_close():
            self.status_win.win.destroy()
            self.status_win = None
        
        self.status_win.win.protocol("WM_DELETE_WINDOW", on_close)

    def toggle_focus(self):
        s = self.state
        if not s.focus_mode:
            s.focus_mode = True
            s.focus_end_time = time.time() + s.focus_duration
            self.show_toast("🍅 专注模式开始", 2000)
        else:
            s.focus_mode = False
            self.show_toast("专注模式已结束", 2000)
        s.save()

    def toggle_startup(self):
        if get_startup_status():
            set_startup(False)
            self.show_toast("开机自启已关闭")
        else:
            set_startup(True)
            self.show_toast("开机自启已开启")

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
            pystray.MenuItem("显示宠物", self.show_pet, default=True),
            pystray.MenuItem("专注模式", self.toggle_focus),
            pystray.MenuItem("开机自启", self.toggle_startup, checked=lambda item: get_startup_status()),
            pystray.MenuItem("退出", self.quit_app)
        )
        self.tray = pystray.Icon("pet", img, "练习生", menu)

    def decay_timer(self):
        self.state.decay()
        self.refresh_status()
        self.root.after(15000, self.decay_timer)

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
