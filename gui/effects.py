import customtkinter as ctk
import random
import math
from config import COLORS

class Particle:
    def __init__(self, x, y, color, p_type="circle"):
        self.x = x
        self.y = y
        self.color = color
        self.type = p_type
        
        # Explosion Physics
        angle = random.uniform(0, 2 * math.pi)
        
        # Speed varies by type
        if p_type == "line":
            speed = random.uniform(10, 25) # Fast streaks
            self.drag = 0.85
            self.size = random.uniform(2, 4)
            self.length = random.uniform(10, 30)
        else:
            speed = random.uniform(2, 12)
            self.drag = 0.95
            self.size = random.uniform(4, 12)
            self.length = 0

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.gravity = 0.4 if p_type != "line" else 0.1
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.03)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= self.drag
        self.vy *= self.drag
        self.life -= self.decay

class Shockwave:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 10
        self.max_radius = 300
        self.width = 20
        self.life = 1.0
        self.decay = 0.04
        self.speed = 15

    def update(self):
        self.radius += self.speed
        self.life -= self.decay
        self.width *= 0.95

class FlyingNumberEffect:
    def __init__(self, root, start_bbox, end_widget, number, theme, on_arrive=None, on_complete=None):
        self.root = root
        self.on_arrive = on_arrive
        self.on_complete = on_complete
        self.number = number 
        self.theme = theme 
        
        # Colors
        self.theme_colors = [COLORS[theme]["accent_hit"], "#FFD700", "#FFEC8B", "#FFFFFF", "#C0C0C0"] 
        
        # 1. Setup Coordinates
        self.start_x = start_bbox[0]
        self.start_y = start_bbox[1]
        self.start_w = start_bbox[2]
        self.start_h = start_bbox[3]
        
        # Target Coords
        try:
            target_x_root = end_widget.winfo_rootx() - self.root.winfo_rootx()
            target_y_root = end_widget.winfo_rooty() - self.root.winfo_rooty()
            target_w = end_widget.winfo_width()
            target_h = end_widget.winfo_height()
            
            self.target_x = target_x_root + (target_w // 2) - (self.start_w // 2)
            self.target_y = target_y_root + (target_h // 2) - (self.start_h // 2)
            
            # Center points for Canvas drawing
            self.start_cx = self.start_x + self.start_w // 2
            self.start_cy = self.start_y + self.start_h // 2
            
            self.target_cx = self.target_x + self.start_w // 2
            self.target_cy = self.target_y + self.start_h // 2
            
        except:
            self.start_cx, self.start_cy = 100, 100
            self.target_cx, self.target_cy = 200, 200

        # 2. Create Overlay Window IMMEDIATELY
        self.overlay = ctk.CTkToplevel(self.root)
        self.overlay.overrideredirect(True)
        
        trans_color = "#000001"
        self.overlay.configure(fg_color=trans_color)
        self.overlay.attributes("-transparentcolor", trans_color)
        self.overlay.attributes("-topmost", True)
        
        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.overlay.geometry(f"{w}x{h}+{x}+{y}")
        
        self.canvas = ctk.CTkCanvas(self.overlay, width=w, height=h, bg=trans_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Animation State
        self.duration = 400 
        self.steps = 25 # Smoother
        self.current_step = 0
        self.interval = self.duration // self.steps
        
        # Bezier Control Point (Arching upwards/randomly)
        # Midpoint + Offset
        mid_x = (self.start_cx + self.target_cx) / 2
        mid_y = (self.start_cy + self.target_cy) / 2
        offset = 100 if random.random() > 0.5 else -100
        self.ctrl_x = mid_x + random.randint(-50, 50)
        self.ctrl_y = mid_y - 150 # Curve UP usually looks nice
        
        # Particles Container
        self.particles = []
        self.shockwaves = []
        self.trail_particles = []
        
        # Start Flight
        self.root.after(10, self._animate_flight)

    def _animate_flight(self):
        self.canvas.delete("all")
        
        t = self.current_step / self.steps
        
        # Ease In Out
        # if t < 0.5: eased_t = 2 * t * t
        # else: eased_t = 1 - pow(-2 * t + 2, 2) / 2
        eased_t = t # Linear t for bezier math, actually visual is better if we just use t? 
        # Or apply ease to t BEFORE bezier.
        
        # Quadratic Bezier: (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
        u = 1 - t
        tt = t * t
        uu = u * u
        
        curr_x = (uu * self.start_cx) + (2 * u * t * self.ctrl_x) + (tt * self.target_cx)
        curr_y = (uu * self.start_cy) + (2 * u * t * self.ctrl_y) + (tt * self.target_cy)
        
        # Spawn Trail Particles
        for _ in range(5):
            # Trail is simple fading dots
            tp = Particle(curr_x, curr_y, random.choice(self.theme_colors), p_type="circle")
            tp.vx *= 0.2 # low speed
            tp.vy *= 0.2
            tp.life = 0.6 # short life
            tp.size = random.randint(2, 6)
            self.trail_particles.append(tp)
        
        # Update & Draw Trail
        alive_trail = []
        for p in self.trail_particles:
            p.update()
            if p.life > 0:
                r = p.size * p.life
                self.canvas.create_oval(
                    p.x - r, p.y - r, p.x + r, p.y + r,
                    fill=p.color, outline=""
                )
                alive_trail.append(p)
        self.trail_particles = alive_trail
        
        # Draw Main Number (Glowing)
        # Glow
        glow_r = 40
        self.canvas.create_oval(
            curr_x - glow_r, curr_y - glow_r, curr_x + glow_r, curr_y + glow_r,
            fill="", outline=COLORS[self.theme]["accent_hit"], width=2
        )
        
        # Text
        font_size = int(20 + 40 * t) # Grow from 20 to 60
        self.canvas.create_text(
            curr_x, curr_y,
            text=str(self.number),
            font=("Arial", font_size, "bold"),
            fill="#FFFFFF"
        )
        
        self.current_step += 1
        
        if self.current_step <= self.steps:
            self.root.after(self.interval, self._animate_flight)
        else:
            self.exp_cx, self.exp_cy = curr_x, curr_y # Handover exact pos
            self._start_explosion()

    def _start_explosion(self):
        # Trigger UI update
        if self.on_arrive:
            self.on_arrive()
            
        # Init Explosion Objects
        # A. Shockwave Ring
        self.shockwaves.append(Shockwave(self.exp_cx, self.exp_cy, "#FFFFFF"))
        self.shockwaves.append(Shockwave(self.exp_cx, self.exp_cy, COLORS[self.theme]["accent_hit"]))
        
        # B. Particles (200+)
        for _ in range(200):
            color = random.choice(self.theme_colors)
            p = Particle(self.exp_cx, self.exp_cy, color, p_type="circle")
            self.particles.append(p)
            
        # C. Fast Streaks (Lines)
        for _ in range(50):
            color = "#FFFFFF"
            p = Particle(self.exp_cx, self.exp_cy, color, p_type="line")
            self.particles.append(p)

        self.flash_life = 5 
        
        self._animate_explosion()

    def _animate_explosion(self):
        if not self.particles and not self.shockwaves and self.flash_life <= 0:
            self._finish()
            return

        self.canvas.delete("all")
        
        # 1. Flash
        if self.flash_life > 0:
            # Draw semi-transparent white rect over everything? 
            # Tkinter canvas transparency is tricky. 
            # We can use stipple='gray50' or simply a big white circle
            r = 1000
            # Simulating flash by just drawing big white circle that shrinks?
            # Or just skip full screen flash if it blocks view too much.
            # Let's do a central white glow.
            flash_r = 300 * (self.flash_life / 5)
            self.canvas.create_oval(
                 self.exp_cx - flash_r, self.exp_cy - flash_r,
                 self.exp_cx + flash_r, self.exp_cy + flash_r,
                 fill="#FFFFFF", outline=""
            )
            self.flash_life -= 1

        # 2. Shockwaves
        alive_waves = []
        for s in self.shockwaves:
            s.update()
            if s.life > 0:
                # Draw ring
                width = s.width * s.life
                # tk create_oval outline width
                self.canvas.create_oval(
                    s.x - s.radius, s.y - s.radius, s.x + s.radius, s.y + s.radius,
                    outline=s.color, width=width
                )
                alive_waves.append(s)
        self.shockwaves = alive_waves
        
        # 3. Particles
        alive_particles = []
        for p in self.particles:
            p.update()
            if p.life > 0:
                alpha_sim = p.color # Tkinter doesn't do alpha easily without hack.
                # We assume background is black-transparent.
                
                if p.type == "line":
                    # Draw Line based on velocity vector
                    tail_x = p.x - p.vx * 2
                    tail_y = p.y - p.vy * 2
                    self.canvas.create_line(
                        tail_x, tail_y, p.x, p.y,
                        fill=p.color, width=2
                    )
                else:
                    # Draw Circle
                    r = p.size * p.life
                    self.canvas.create_oval(
                        p.x - r, p.y - r, p.x + r, p.y + r,
                        fill=p.color, outline=""
                    )
                alive_particles.append(p)
        
        self.particles = alive_particles
        
        if self.particles or self.shockwaves or self.flash_life > 0:
            self.root.after(20, self._animate_explosion)
        else:
            self._finish()
            
    def _finish(self):
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy()
            
        if self.on_complete:
            self.on_complete()
