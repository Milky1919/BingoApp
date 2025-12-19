import customtkinter as ctk
from config import COLORS, MIN_NUMBER, MAX_NUMBER

class PanelBase(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._colors = COLORS["dark"] # Default

    def update_theme(self, theme_name):
        self._colors = COLORS[theme_name]
        self._apply_theme()

    def _apply_theme(self):
        """Override in subclasses"""
        self.configure(fg_color=self._colors["panel_bg"])

class LeftPanel(PanelBase):
    def __init__(self, master, on_spin_click, on_toggle_bgm, on_toggle_se, on_bgm_vol, on_se_vol, on_toggle_fullscreen, **kwargs):
        super().__init__(master, **kwargs)
        self.on_spin_click = on_spin_click
        self.on_toggle_bgm = on_toggle_bgm
        self.on_toggle_se = on_toggle_se
        self.on_bgm_vol = on_bgm_vol
        self.on_se_vol = on_se_vol
        self.on_toggle_fullscreen = on_toggle_fullscreen

        # Layout
        self.grid_rowconfigure(0, weight=1) # Spacer
        self.grid_rowconfigure(1, weight=0) # Number
        self.grid_rowconfigure(2, weight=0) # Button
        self.grid_rowconfigure(3, weight=1) # Spacer
        self.grid_rowconfigure(4, weight=0) # Controls
        self.grid_columnconfigure(0, weight=1)

        # 1. Current Number Display
        self.lbl_number = ctk.CTkLabel(
            self, 
            text="--",
            font=("Roboto", 400, "bold"),
            text_color=self._colors["text"]
        )
        self.lbl_number.grid(row=1, column=0, pady=(0, 40))

        # 2. SPIN Button
        self.btn_spin = ctk.CTkButton(
            self,
            text="SPIN",
            font=("Arial", 32, "bold"),
            height=80,
            width=200,
            corner_radius=40,
            command=self._on_spin,
            fg_color=self._colors["btn_spin"],
            hover_color=self._colors["btn_hover"]
        )
        self.btn_spin.grid(row=2, column=0)

        # 3. Audio Controls (Bottom Left)
        self.frame_controls = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_controls.grid(row=4, column=0, sticky="sw", padx=20, pady=20)
        
        # --- BGM Group ---
        self.fr_bgm = ctk.CTkFrame(self.frame_controls, fg_color="transparent")
        self.fr_bgm.pack(side="left", padx=(0, 10))
        
        self.btn_bgm = ctk.CTkButton(
            self.fr_bgm, text="🎵", width=40, height=40,
            font=("Segoe UI Emoji", 20),
            fg_color="transparent", hover_color=self.btn_spin._fg_color,
            command=self._on_click_bgm
        )
        self.btn_bgm.pack(side="left")
        
        self.slider_bgm = ctk.CTkSlider(
            self.fr_bgm, from_=0, to=1, number_of_steps=20,
            width=80, command=self.on_bgm_vol
        )
        self.slider_bgm.set(1.0) 
        self.slider_bgm.pack(side="left", padx=5)

        # --- SE Group ---
        self.fr_se = ctk.CTkFrame(self.frame_controls, fg_color="transparent")
        self.fr_se.pack(side="left", padx=(0, 10))

        self.btn_se = ctk.CTkButton(
            self.fr_se, text="🔊", width=40, height=40,
            font=("Segoe UI Emoji", 20),
            fg_color="transparent", hover_color=self.btn_spin._fg_color,
            command=self._on_click_se
        )
        self.btn_se.pack(side="left")
        
        self.slider_se = ctk.CTkSlider(
            self.fr_se, from_=0, to=1, number_of_steps=20,
            width=80, command=self.on_se_vol
        )
        self.slider_se.set(1.0) 
        self.slider_se.pack(side="left", padx=5)
        
        # --- Fullscreen ---
        self.btn_fs = ctk.CTkButton(
            self.frame_controls, text="⛶", width=40, height=40,
            font=("Segoe UI Emoji", 20),
            fg_color="transparent", hover_color=self.btn_spin._fg_color,
            command=self._on_click_fullscreen
        )
        self.btn_fs.pack(side="left", padx=(0, 10))

        self.apply_theme_initial()

    def apply_theme_initial(self):
        # We call this manually to force color Application
        self._apply_theme()

    def _apply_theme(self):
        super()._apply_theme()
        if hasattr(self, 'lbl_number'):
            self.lbl_number.configure(text_color=self._colors["text"])
        if hasattr(self, 'btn_spin'):
            self.btn_spin.configure(
                fg_color=self._colors["btn_spin"],
                hover_color=self._colors["btn_hover"],
                text_color="#ffffff" # Always white for button
            )
        # Update Audio button active states if needed
        # (For simplicity, we keep them text-based, maybe change text color)
        
    def update_number(self, num):
        text = str(num) if num is not None else "--"
        self.lbl_number.configure(text=text)

    def set_spin_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.btn_spin.configure(state=state)
        # Visual feedback for disabled state
        if not enabled:
            self.btn_spin.configure(fg_color="gray")
        else:
            self.btn_spin.configure(fg_color=self._colors["btn_spin"])

    def _on_spin(self):
        self.on_spin_click()

    def _on_click_bgm(self):
        state = self.on_toggle_bgm()
        self._update_audio_btn_visual(self.btn_bgm, state)

    def _on_click_se(self):
        state = self.on_toggle_se()
        self._update_audio_btn_visual(self.btn_se, state)
        
    def _on_click_fullscreen(self):
        self.on_toggle_fullscreen()

    def _update_audio_btn_visual(self, btn, active):
        if active:
            btn.configure(text_color=self._colors["accent_hit"], fg_color="transparent")
        else:
            btn.configure(text_color="gray", fg_color="transparent")


class RightPanel(PanelBase):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_cells = {}
        self._create_grid()

    def _create_grid(self):
        # 10 lines x 8 rows (approx for 75)
        # Spec: 10 columns
        columns = 10
        
        for num in range(MIN_NUMBER, MAX_NUMBER + 1):
            row = (num - 1) // columns
            col = (num - 1) % columns
            
            # Cell Frame
            frame = ctk.CTkFrame(self, corner_radius=5)
            frame.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            
            # Label
            label = ctk.CTkLabel(
                frame, 
                text=str(num),
                font=("Arial", 70, "bold")
            )
            label.place(relx=0.5, rely=0.5, anchor="center")
            
            self.grid_cells[num] = {"frame": frame, "label": label}
            
        # Configure grid weights
        for i in range(columns):
            self.grid_columnconfigure(i, weight=1)
        # Rows
        for i in range(8):
            self.grid_rowconfigure(i, weight=1)

    def _apply_theme(self):
        super()._apply_theme()
        # Reset all cells to "normal" for the new theme
        # We need to know which are hit/cursor to re-apply correctly.
        # Ideally, the App should trigger a full refresh.
        # For now, just setting base colors for unhit cells
        pass 

    def update_cell_state(self, num, state, is_cursor=False, trail_intensity=0):
        """
        state: 'normal', 'hit'
        is_cursor: bool (overrides state)
        trail_intensity: int (0=Head/None, 1=Strong, 2=Med, 3=Weak)
        """
        if num not in self.grid_cells: return
        
        widgets = self.grid_cells[num]
        frame = widgets["frame"]
        label = widgets["label"]
        
        # Colors
        cursor_color = self._colors["accent_cursor"] # e.g. #00ffff or similar logic
        hit_color = self._colors["accent_hit"]
        normal_bg = self._colors["cell_bg"]
        
        # Pre-calculated gradients for 'cyan'/'orange' themes roughly
        # Since we use 'accent_cursor' from logic, we might not know specific hex.
        # But for 'dark' theme accent_cursor is likely Cyan-ish.
        # Let's try to act smart: if cursor color is Hex, we can't easily dim it without lib.
        # However, we only have 2 themes. We can just check self._colors["accent_cursor"] and map manually?
        # Or simpler: Just hardcode nice "Fade" colors for Dark/Light mode in panels.
        
        # We need to know current theme to pick gradients? 
        # self._colors is populated by update_theme.
        # Let's check typical values: 
        # Dark Cursor: #4cc9f0 (Cyan)
        # Light Cursor: #eebb00 (Orange)? checking config...
        # Let's assume standard colors for now.
        
        bg = normal_bg
        fg = self._colors["text_dim"]
        border_width = 0
        border_color = bg
        
        if is_cursor:
            fg = "#ffffff"
            if trail_intensity == 0:
                # HEAD
                bg = cursor_color
                border_width = 2
                border_color = "#ffffff"
            else:
                # TRAIL (Faded)
                # Use cursor_color for all, but remove border.
                # Since we can't easily fade HEX without lib, we stick to solid cursor color
                # But maybe we can distinct based on intensity? 
                # User wants "Orange" (Single Color) fade.
                # If we use the exact same color, it looks like a block.
                # We need a way to show "Fading".
                # If we are Light Mode (Orange), let's use predetermined lighter oranges?
                # Or just use the Hit Color (which is usually diff) as tail?
                # User said "Fade is single color (Orange)".
                
                # Let's check if we are in Light Mode (Orange Cursor)
                # Config has: Light -> Accent Cursor = #FF9800 (Orange)
                # Dark -> Accent Cursor = #00E5FF (Cyan)
                
                bg = cursor_color
                border_width = 0
                
                # Manual Gradient Hack for known colors
                # Light Mode (Orange #FF9800)
                if "FF9800" in cursor_color.upper() or "ORANGE" in cursor_color.upper():
                    # Fade to Yellow/White?
                    if trail_intensity == 1: bg = "#FFB74D" # Lighter Orange
                    elif trail_intensity == 2: bg = "#FFCC80"
                    elif trail_intensity == 3: bg = "#FFE0B2"
                    
                # Dark Mode (Cyan #00E5FF)
                elif "00E5FF" in cursor_color.upper() or "CYAN" in cursor_color.upper() or "4CC9F0" in cursor_color.upper(): 
                     if trail_intensity == 1: bg = "#26C6DA"
                     elif trail_intensity == 2: bg = "#4DD0E1"
                     elif trail_intensity == 3: bg = "#80DEEA"
                
                # If unknown color, keep solid (better than wrong color)


        elif state == "hit":
            bg = hit_color
            fg = "#ffffff"
            
        frame.configure(fg_color=bg, border_width=border_width, border_color=border_color)
        label.configure(text_color=fg)



    def get_cell_bbox(self, num):
        """Returns (x, y, width, height) of the cell relative to the SCREEN (or at least root window)"""
        if num not in self.grid_cells: return None
        
        frame = self.grid_cells[num]["frame"]
        
        # We need coordinates relative to the root window to place a floating label
        try:
            x = frame.winfo_rootx() - self.winfo_toplevel().winfo_rootx()
            y = frame.winfo_rooty() - self.winfo_toplevel().winfo_rooty()
            w = frame.winfo_width()
            h = frame.winfo_height()
            return (x, y, w, h)
        except:
            return None


    def refresh_all(self, history, current_cursor=None):
        for num in range(MIN_NUMBER, MAX_NUMBER + 1):
            state = "hit" if num in history else "normal"
            is_cursor = (num == current_cursor)
            self.update_cell_state(num, state, is_cursor)
