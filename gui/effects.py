import customtkinter as ctk
import time
from config import COLORS

class FlyingNumberEffect:
    def __init__(self, root, start_bbox, end_widget, number, theme, on_complete):
        """
        :param root: The root window (to place floating label)
        :param start_bbox: (x, y, w, h) of the starting cell in root coords
        :param end_widget: The target widget (LeftPanel label) to fly TO
        :param number: The number to display
        :param theme: Current theme name ("dark"/"light")
        :param on_complete: Callback when animation ends
        """
        self.root = root
        self.on_complete = on_complete
        
        # 1. Create the floating label
        self.label = ctk.CTkLabel(
            self.root,
            text=str(number),
            font=("Arial", 20, "bold"), # Start small-ish
            width=start_bbox[2],
            height=start_bbox[3],
            fg_color=COLORS[theme]["accent_hit"],
            text_color="#ffffff",
            corner_radius=5
        )
        
        # 2. Setup Coordinates
        self.start_x = start_bbox[0]
        self.start_y = start_bbox[1]
        self.start_w = start_bbox[2]
        self.start_h = start_bbox[3]
        
        # Target Coords (Center of end_widget)
        # end_widget is likely inside LeftPanel, so we need its root coords
        try:
            target_x_root = end_widget.winfo_rootx() - self.root.winfo_rootx()
            target_y_root = end_widget.winfo_rooty() - self.root.winfo_rooty()
            target_w = end_widget.winfo_width()
            target_h = end_widget.winfo_height()
            
            # Center to Center
            self.target_x = target_x_root + (target_w // 2) - (self.start_w // 2)
            self.target_y = target_y_root + (target_h // 2) - (self.start_h // 2)
        except:
            # Fallback if widget not mapped well
            self.target_x = 200
            self.target_y = 200

        # Animation State
        self.duration = 600 # ms
        self.steps = 30
        self.current_step = 0
        self.interval = self.duration // self.steps
        
        # Place at start
        self.label.place(x=self.start_x, y=self.start_y)
        
        # Start
        self.root.after(10, self._animate)

    def _animate(self):
        t = self.current_step / self.steps
        
        # Easing (Ease In Out Quad)
        if t < 0.5:
            eased_t = 2 * t * t
        else:
            eased_t = 1 - pow(-2 * t + 2, 2) / 2
            
        # Interpolate Pos
        curr_x = self.start_x + (self.target_x - self.start_x) * eased_t
        curr_y = self.start_y + (self.target_y - self.start_y) * eased_t
        
        # Interpolate Scale (Simulated by font size approx? CustomTkinter font update might be heavy)
        # Instead, we just move it. Scale effect is hard with standard labels efficiently.
        # Maybe scale size of widget (width/height) but text won't scale automatically.
        # Let's just move + fade in/out or color shift. 
        # User asked for "Flying number". Movement is key.
        
        self.label.place(x=int(curr_x), y=int(curr_y))
        
        self.current_step += 1
        
        if self.current_step <= self.steps:
            self.root.after(self.interval, self._animate)
        else:
            self._finish()

    def _finish(self):
        self.label.destroy()
        if self.on_complete:
            self.on_complete()
