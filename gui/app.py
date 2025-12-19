import customtkinter as ctk
import tkinter.messagebox as messagebox
from screeninfo import get_monitors
from config import APP_NAME, VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, COLORS
from gui.panels import LeftPanel, RightPanel
from gui.animations import SpinAnimation

class BingoApp(ctk.CTk):
    def __init__(self, data_manager, game_logic, audio_manager):
        super().__init__()
        
        self.dm = data_manager
        self.logic = game_logic
        self.audio = audio_manager

        # Constants
        self.current_theme = "dark" # Start dark
        self.monitors = get_monitors()
        self.target_monitor_index = 0 # Default to primary (or first detected)
        
        # Monitor Detection Logic fix for getting correct numbering?
        # get_monitors() returns list. We will just use index 0, 1, 2...
        
        # Window Setup
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        ctk.set_appearance_mode("Dark") # Global CTk setting

        # Grid Layout
        self.grid_columnconfigure(0, weight=0, minsize=530) # Left Panel
        self.grid_columnconfigure(1, weight=1)              # Right Panel
        self.grid_rowconfigure(0, weight=1)

        # Components
        self.left_panel = LeftPanel(
            self, 
            on_spin_click=self.start_spin,
            on_toggle_bgm=self.toggle_bgm,
            on_toggle_se=self.toggle_se,
            on_toggle_fullscreen=self.toggle_fullscreen
        )
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.right_panel = RightPanel(self)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        # Theme Toggle (Floating or Top-Right Overlay? 
        # Plan was "near audio controls". Let's put it on LeftPanel for simplicity,
        # but since LeftPanel is already instantiated, we can add it there or 
        # add a small button in top corner of Window.
        # Let's add a small toggle switch to LeftPanel via method for cleaner code)
        self._add_theme_toggle()

        # Keybinds
        self.bind("<Control-Shift-R>", self.confirm_reset)
        self.bind("<Control-Shift-r>", self.confirm_reset)

        # Animation Init
        self.animator = SpinAnimation(
            root=self,
            game_logic=self.logic,
            audio_manager=self.audio,
            on_update_display=self.update_display_during_spin,
            on_step_finish=self.on_step_finish,
            on_complete=self.on_spin_complete
        )

        # Initial State
        self.refresh_ui()
        self.audio.play_bgm()
        
        self.is_fullscreen = False
        self.windowed_geometry = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"

    def select_monitor(self, index):
        pass # Deprecated

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            # Entering Borderless Fullscreen
            # 1. Save current state
            self.windowed_geometry = self.geometry()
            
            # 2. Determine which monitor contains the window center
            wx = self.winfo_x()
            wy = self.winfo_y()
            ww = self.winfo_width()
            wh = self.winfo_height()
            cx = wx + ww // 2
            cy = wy + wh // 2
            
            target_monitor = self.monitors[0] # Default
            
            # Refresh monitors list to be safe
            current_monitors = get_monitors()
            
            for m in current_monitors:
                # Check if center is within this monitor's bounds
                if (m.x <= cx < m.x + m.width) and (m.y <= cy < m.y + m.height):
                    target_monitor = m
                    break
            
            # 3. Apply Borderless Fullscreen
            self.overrideredirect(True) # Remove title bar
            self.geometry(f"{target_monitor.width}x{target_monitor.height}+{target_monitor.x}+{target_monitor.y}")
            self.state("normal") # Ensure not minimized
            
            # Force focus and lift (helpful on Windows)
            self.lift()
            self.focus_force()
            
        else:
            # Exiting Fullscreen -> Restore Window
            self.overrideredirect(False) # Restore title bar
            self.geometry(self.windowed_geometry)

    def _add_theme_toggle(self):
        # We'll inject a switch into the LeftPanel's controls frame
        switch = ctk.CTkSwitch(
            self.left_panel.frame_controls, 
            text="Dark/Light",
            command=self.toggle_theme,
            onvalue="light",
            offvalue="dark"
        )
        # Select correct initial state
        switch.deselect() # Dark is offvalue
        switch.pack(side="left", padx=20)

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        
        # Update Global Appearance
        mode = "Light" if self.current_theme == "light" else "Dark"
        ctk.set_appearance_mode(mode)
        
        # Update Panels
        self.left_panel.update_theme(self.current_theme)
        self.right_panel.update_theme(self.current_theme)
        
        # Refresh grid colors
        self.refresh_ui()

    def refresh_ui(self):
        # Update Number
        self.left_panel.update_number(self.logic.current_number)
        
        # Update Grid
        self.right_panel.refresh_all(
            self.logic.history, 
            current_cursor=self.logic.current_number
        )
        
        # Update spin button state
        # Disable if all numbers derived (75 items in history)
        is_full = len(self.logic.history) >= 75
        # Also check if animator is running to avoid re-enabling during spin if refreshed
        is_running = self.animator.is_running if hasattr(self, 'animator') else False
        self.left_panel.set_spin_enabled(not is_full and not is_running)

    def start_spin(self):
        if self.animator.is_running: return
        
        # 1. Get next number (Logic updates history immediately for safety)
        target = self.logic.get_next_number()
        
        if target is None:
            messagebox.showinfo("Finished", "All numbers have been drawn!")
            return

        # 2. Disable UI
        self.left_panel.set_spin_enabled(False)

        # 3. Start Animation
        self.animator.start(target)

    def update_display_during_spin(self, number):
        # During heavy spin, we can just update the number
        self.left_panel.update_number(number)

    def on_step_finish(self, data):
        """
        data: Can be single int (cursor number) OR list of tuples [(num, intensity), ...]
        """
        # 1. Clear previous cursors
        if hasattr(self, "_last_highlighted_cells"):
            for num in self._last_highlighted_cells:
                # Revert to normal/hit based on history
                
                # CRITICAL FIX: The current target number is ALREADY in self.logic.history 
                # because we added it at start_spin. 
                # But visually, it should NOT be "Hit" (Blue) yet. It should be "Normal" (Gray)
                # until the animation finishes and we confirm it.
                
                # Check if this num is the current target being spun
                # (We can check via logic.current_number, usually)
                
                is_target = (num == self.logic.current_number)
                
                if num in self.logic.history and not is_target:
                     state = "hit"
                else:
                     state = "normal"
                     
                self.right_panel.update_cell_state(num, state, is_cursor=False)
        
        self._last_highlighted_cells = set()

        # 2. Parse Data
        if isinstance(data, list):
            for num, intensity in data:
                self.right_panel.update_cell_state(num, "normal", is_cursor=True, trail_intensity=intensity)
                self._last_highlighted_cells.add(num)
                
            if data:
                head_num = data[0][0]
                self.left_panel.update_number(head_num)
                
        else:
            number = data
            self.right_panel.update_cell_state(number, "normal", is_cursor=True)
            self._last_highlighted_cells.add(number)
            self.left_panel.update_number(number)


    def on_spin_complete(self, number):
        # 1. Update Left Panel to "Moving..." state or maintain last spun number?
        # The animation stopped at 'number'. We want to "Fly" it from Grid to Left.
        
        # Get start center
        start_bbox = self.right_panel.get_cell_bbox(number)
        end_widget = self.left_panel.lbl_number
        
        # NOTE: We do NOT update the UI yet (refresh_ui). We wait for the "Arrrival".
        # But we DO need to ensure the grid cell looks like it's the source.
        # Currently it's still "Cursor" state from last step.
        
        def on_arrive_at_target():
             # This runs when the flying number Hits the center (Trigger explosion + Update UI)
             self.refresh_ui() 
             # self.logic.save_game() - Removed, already saved in start_spin
        
        def on_effect_complete():
             # This runs after explosion fades
             is_full = len(self.logic.history) >= 75
             self.left_panel.set_spin_enabled(not is_full)

        if start_bbox:
            from gui.effects import FlyingNumberEffect
            
            FlyingNumberEffect(
                root=self,
                start_bbox=start_bbox,
                end_widget=end_widget,
                number=number,
                theme=self.current_theme,
                on_arrive=on_arrive_at_target, 
                on_complete=on_effect_complete
            )
        else:
            # Fallback if bbox failed
            # If no bbox, means we can't animate, so just do the final steps
            on_arrive_at_target()
            on_effect_complete()

    def _on_fly_complete(self, number):
        # 1. Show final number on Left Panel
        self.left_panel.update_number(number)
        
        # 2. Trigger "Impact" visual (Bright Flash)
        self._animate_impact(number)
        
        # 3. Update Grid to final "Hit" state (Blue)
        # Logic history was already updated in logic, but visually it showed 'cursor'.
        self.refresh_ui() 
        
        # 4. Enable button
        self.left_panel.set_spin_enabled(True)

    def _animate_impact(self, number):
        # Bright Flash of text color
        def set_impact_style():
            self.left_panel.lbl_number.configure(text_color=COLORS[self.current_theme]["accent_cursor"])
            
        def reset_impact_style():
            self.left_panel.lbl_number.configure(text_color=COLORS[self.current_theme]["text"])

        set_impact_style()
        self.after(300, reset_impact_style)
        self.audio.play_se("decide")

    def confirm_reset(self, event=None):
        if messagebox.askyesno("Reset", "Are you sure you want to reset all data?"):
            self.logic.reset_game()
            self.refresh_ui()
            # Also restart BGM if it stopped? No, BGM is independent.

    def toggle_bgm(self):
        return self.audio.toggle_bgm()

    def toggle_se(self):
        return self.audio.toggle_se()
