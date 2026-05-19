import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import imageio
import numpy as np


class AnimationManager:
    def __init__(self, pet):
        self.pet = pet
        self.base_dir = pet.base_dir
        self.image_folder = pet.image_folder
        self.progress_win = None

        # 视频目录：base_dir/videos
        self.video_dir = os.path.join(self.base_dir, 'videos')
        # 缓存目录：base_dir/cache
        self.cache_dir = os.path.join(self.base_dir, 'cache')
        os.makedirs(self.video_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

        self.action_anim_map = {
            "超级食物碗": "feed_superbowl",
            "波奇饭便当": "feed_poke",
            "绿色排毒果汁": "feed_juice",
            "牛肉沙拉碗": "feed_beefsalad",
            "冰美式": "drink_iceamericano",
            "泡澡": "bath",
            "快速洗脸": "face_wash",
            "便利店兼职": "store",  
            "咖啡店打工": "cafe",
            "社区声乐班": "vocal_beginner",
            "街舞入门课": "dance_beginner",
            "进阶声乐": "vocal_advanced",
            "进阶舞蹈": "dance_advanced",
        }

    def generate_caches_async(self):
        scales = [1.5, 2.0]
        tasks = []
        for scale in scales:
            for base in ["greet", "idle", "store"]:
                if not self.cache_exists(scale, base):
                    tasks.append((scale, base))
            for base in set(self.action_anim_map.values()):
                if not self.cache_exists(scale, base):
                    tasks.append((scale, base))
        if tasks:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=4) as executor:
                for scale, name in tasks:
                    executor.submit(self.ensure_cache_for_scale, scale, name)

    def play_action_animation(self, action_name):
        if action_name not in self.action_anim_map:
            return
        base = self.action_anim_map[action_name]
        self.ensure_cache_for_scale(self.pet.state.scale, base)
        cache_dir = os.path.join(self.cache_dir, f"{base}_{self.pet.state.scale}x_frames")
        frames = self.load_png_frames(cache_dir)
        if frames:
            self.play_animation(frames, loop=True)

    def cache_exists(self, scale, base_name):
        cache_dir = os.path.join(self.cache_dir, f"{base_name}_{scale}x_frames")
        return os.path.isdir(cache_dir) and os.listdir(cache_dir)

    def ensure_cache_for_scale(self, scale, base_name):
        cache_dir = os.path.join(self.cache_dir, f"{base_name}_{scale}x_frames")
        if not os.path.isdir(cache_dir) or not os.listdir(cache_dir):
            video_path = None
            for ext in [".webm", ".mp4"]:
                candidate = os.path.join(self.video_dir, f"{base_name}{ext}")
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
                diff = arr[:,:,:3].astype(np.float32) - np.array([ref_r, ref_g, ref_b], dtype=np.float32)
                dist_purple = np.sqrt(np.sum(diff**2, axis=2))
                max_rgb = np.max(arr[:,:,:3], axis=2)
                min_rgb = np.min(arr[:,:,:3], axis=2)
                saturation = max_rgb - min_rgb
                is_tongue = (arr[:,:,0] > 180) & (arr[:,:,2] < 140)
                is_bg = (dist_purple < max_dist) & (arr[:,:,3] > 200) & (saturation > 25)
                mask = is_bg & (~is_tongue)
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
        scale = self.pet.state.scale
        greet_dir = os.path.join(self.cache_dir, f"greet_{scale}x_frames")
        idle_dir = os.path.join(self.cache_dir, f"idle_{scale}x_frames")
        greet_frames = self.load_png_frames(greet_dir)
        idle_frames = self.load_png_frames(idle_dir) if os.path.isdir(idle_dir) else None
        return greet_frames, idle_frames

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
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith((".png", ".gif"))])
        if not files:
            return False
        for f in files:
            try:
                img = Image.open(os.path.join(folder, f)).convert("RGBA")
                img.thumbnail((self.pet.pet_w, self.pet.pet_h), Image.LANCZOS)
                self.pet.frames.append(ImageTk.PhotoImage(img))
            except:
                pass
        return len(self.pet.frames) > 0

    def play_animation(self, anim_list, loop=False, callback=None):
        if self.pet.anim_after_id:
            self.pet.pet_win.after_cancel(self.pet.anim_after_id)
        self.pet.current_anim = anim_list
        self.pet.anim_index = 0
        self._animate_frame(loop, callback)

    def _animate_frame(self, loop, callback):
        if not self.pet.current_anim:
            return
        if self.pet.anim_index >= len(self.pet.current_anim):
            if loop:
                self.pet.anim_index = 0
            else:
                if callback:
                    callback()
                return
        frame = self.pet.current_anim[self.pet.anim_index]
        self.pet.anim_label.configure(image=frame)
        self.pet.anim_index += 1
        self.pet.anim_after_id = self.pet.pet_win.after(50, self._animate_frame, loop, callback)

    def switch_to_idle(self):
        if self.pet.anim_after_id:
            self.pet.pet_win.after_cancel(self.pet.anim_after_id)
            self.pet.anim_after_id = None
        self.pet.current_anim = None
        if self.pet.anim_idle_frames:
            self.play_animation(self.pet.anim_idle_frames, loop=True)
        else:
            if self.pet.static_img:
                self.pet.anim_label.configure(image=self.pet.static_img)

    def play_store_animation(self):
        self.ensure_cache_for_scale(self.pet.state.scale, "store")
        cache_dir = os.path.join(self.cache_dir, f"store_{self.pet.state.scale}x_frames")
        frames = self.load_png_frames(cache_dir)
        if frames:
            self.play_animation(frames, loop=True)

    def set_scale(self, scale):
        self.pet.state.scale = scale
        self.pet.state.save()
        self.pet.pet_w = self.pet.state.pet_w
        self.pet.pet_h = self.pet.state.pet_h
        self.pet.pet_win.geometry(f"{self.pet.pet_w}x{self.pet.pet_h}+{self.pet.x}+{self.pet.y}")
        self.pet.anim_greet_frames, self.pet.anim_idle_frames = self.load_current_anim_frames()
        self.pet.static_img = None
        self.pet.frames = []
        self.pet.has_image = self.load_frames(self.image_folder) if os.path.isdir(self.image_folder) else False
        if self.pet.has_image:
            self.pet.static_img = self.pet.frames[0]
        else:
            img = Image.new("RGBA", (self.pet.pet_w, self.pet.pet_h), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((30,30,self.pet.pet_w-30,self.pet.pet_h-30), fill="orange", outline="white", width=2)
            self.pet.static_img = ImageTk.PhotoImage(img)
        if self.pet.current_anim is not None:
            if self.pet.anim_after_id:
                self.pet.pet_win.after_cancel(self.pet.anim_after_id)
            if self.pet.current_anim == self.pet.anim_greet_frames:
                self.play_animation(self.pet.anim_greet_frames, loop=False, callback=self.switch_to_idle)
            elif self.pet.current_anim == self.pet.anim_idle_frames:
                self.play_animation(self.pet.anim_idle_frames, loop=True)
            else:
                self.pet.anim_label.configure(image=self.pet.static_img)
        else:
            self.pet.anim_label.configure(image=self.pet.static_img)
        if self.pet.bubble_win and self.pet.bubble_win.winfo_exists():
            self.pet.bubble_win.geometry(f"200x40+{self.pet.x-20}+{self.pet.y-50}")

    def show_progress_bar(self, title):
        self.progress_win = tk.Toplevel(self.pet.root)
        self.progress_win.title("加载中")
        self.progress_win.geometry("300x100")
        self.progress_win.resizable(False, False)
        self.progress_win.configure(bg="#FFFFFF")
        self.progress_win.update_idletasks()
        sw = self.progress_win.winfo_screenwidth()
        sh = self.progress_win.winfo_screenheight()
        x = (sw - 300) // 2
        y = (sh - 100) // 2
        self.progress_win.geometry(f"+{x}+{y}")
        tk.Label(self.progress_win, text=title, font=("Segoe UI", 12),
                 fg="#1A1A1A", bg="#FFFFFF").pack(pady=24)
        self.progress_bar = ttk.Progressbar(self.progress_win, length=250, mode='indeterminate')
        self.progress_bar.pack(pady=16)
        self.progress_bar.start(10)
        self.progress_win.lift()
