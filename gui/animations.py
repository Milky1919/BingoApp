import math

class SpinAnimation:
    def __init__(self, root, game_logic, audio_manager, 
                 on_update_display, on_step_finish, on_complete):
        """
        :param root: Tkinter root (for .after)
        :param game_logic: Instance of GameLogic
        :param audio_manager: Instance of AudioManager
        :param on_update_display: Callback(number) to update UI
        :param on_step_finish: Callback(number) called after each step (for grid highlight)
        :param on_complete: Callback(number) when animation finishes
        """
        self.root = root
        self.logic = game_logic
        self.audio = audio_manager
        
        self.on_update_display = on_update_display
        self.on_step_finish = on_step_finish
        self.on_complete = on_complete
        
        self.is_running = False
        self._cancel_id = None

    def start(self, target_number):
        if self.is_running: return
        self.is_running = True
        
        # === VELOCITY PROFILE GENERATION ===
        self.velocity_profile = []
        
        # 1. P1: Speedster (Constant)
        # Random duration: 1.0s - 2.0s (approx 60 - 125 frames at 16ms)
        import random
        p1_frames = random.randint(60, 125)
        p1_v = 2.0
        p1_profile = [p1_v] * p1_frames
        self.velocity_profile.extend(p1_profile)
        
        # 2. P2: Main Deceleration
        # V goes from 2.0 -> 0.05 (Very slow)
        p2_frames = 100
        p2_start_v = 2.0
        p2_end_v = 0.05 
        for i in range(p2_frames):
            t = i / p2_frames
            # Quadratic Decay for smooth feel
            v = (p2_start_v - p2_end_v) * ((1.0 - t)**2) + p2_end_v
            self.velocity_profile.append(v)
        
        # 3. P3: Creep / Tail (Randomized Length)
        # V goes from 0.05 -> 0.0
        # Calculate Duration T to cover 'creep_steps' starting from p2_end_v down to 0.
        
        import random
        creep_steps = random.randint(2, 4)
        
        # Linear decay: Avg V = p2_end_v / 2.
        # T = Steps / AvgV = 2 * Steps / p2_end_v.
        
        p3_start_v = p2_end_v
        p3_frames = int(2.0 * creep_steps / p3_start_v)
        
        for i in range(p3_frames):
             t = i / p3_frames
             # Linear decay to 0
             v = p3_start_v * (1.0 - t)
             self.velocity_profile.append(v)
        
        # Ensure hard stop at end
        self.velocity_profile.append(0.0) 
        
        # === CALCULATE PATH ===
        total_steps = int(sum(self.velocity_profile))
        self.path = self.logic.calculate_animation_path(target_number, total_steps)
        
        # === RUNTIME STATE ===
        self.current_frame = 0
        self.float_index = 0.0
        self.path_index = 0 
        self.TOTAL_FRAMES = len(self.velocity_profile)
        self._last_displayed = -1
        self.last_audio_time = 0 
        
        self._animate_step()

    def _animate_step(self):
        if not self.is_running: return
        import time 
        
        current_display_number = None
        trail_numbers = [] 
        play_sound = False
        now = time.time()
        
        if self.current_frame < len(self.velocity_profile):
            v = self.velocity_profile[self.current_frame]
            
            # Accumulate float steps
            self.float_index += v
            target_abs_index = int(self.float_index)
            
            # Clamp
            if target_abs_index >= len(self.path): target_abs_index = len(self.path) - 1
            
            current_display_number = self.path[target_abs_index]
            head_num = current_display_number
            
            # --- Trail Logic ---
            if v > 1.5: trail_len = 2 
            elif v > 0.5: trail_len = 1
            else: trail_len = 0 
            
            trail_numbers = [(head_num, 0)]
            if trail_len > 0:
                 for i in range(trail_len):
                     val = (head_num - 1 - (i + 1)) % 75 + 1
                     trail_numbers.append((val, i + 1))
            
            # --- Sound Logic ---
            # Unified approach: Play sounds based on visual change, but cap max frequency to ~60Hz
            # High speed (v=2.0) -> Changes every frame (16ms) -> Plays every frame
            # Decel (v=0.5) -> Changes every 2 frames (32ms) -> Plays every 2 frames
            # This ensures High Speed is always faster (or equal to max frame rate) than Decel.
            
            # MIN_INTERVAL should be ~30ms to allow ~30Hz playback.
            # 16ms frames -> 32ms (30Hz) trigger allowed.
            # This is significantly faster than typical deceleration curve, preserving the "High Speed > Slow Speed" feeling.
            MIN_INTERVAL = 0.03 
            
            if self._last_displayed != head_num and self._last_displayed != -1:
                # Check time to prevent glitches
                if now - self.last_audio_time >= MIN_INTERVAL:
                    play_sound = True
                    self.last_audio_time = now
            
            self._last_displayed = head_num

            # --- Frame Advance ---
            self.current_frame += 1
            
            if current_display_number is not None:
                self.on_update_display(current_display_number)
                self.on_step_finish(trail_numbers) 
            
            if play_sound:
                # Limit duration to 200ms to allow overlapping but prevent channel exhaustion
                self.audio.play_se("move", maxtime=200)
                
            self._cancel_id = self.root.after(16, self._animate_step)
            
        else:
            self._finish(self.path[-1])

    def _finish(self, final_number):
        self.is_running = False
        
        # Force final update
        self.on_update_display(final_number)
        self.on_step_finish([(final_number, 0)]) 
        # Removed redundant "move" sound here. Only "decide" should play.
        self.root.after(400, lambda: self._trigger_complete(final_number))

    def _trigger_complete(self, final_number):
        self.audio.play_se("decide")
        self.on_complete(final_number)
