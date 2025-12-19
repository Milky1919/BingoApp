import os
import pygame
from config import SOUND_DIR

class AudioManager:
    def __init__(self):
        self.bgm_enabled = True
        self.se_enabled = True
        self.bgm_playing = False
        
        # Avoid crash if no audio device
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(32) # Allow many overlapping sounds
            self.has_mixer = True
        except Exception as e:
            print(f"Audio init failed: {e}")
            self.has_mixer = False

        self.sounds = {}
        self._load_sounds()

    def _load_sounds(self):
        if not self.has_mixer: return
        
        # Define paths
        base_names = ["move", "decide"]
        
        for name in base_names:
            # Try wav first, then mp3
            found = False
            for ext in [".wav", ".mp3"]:
                filename = name + ext
                path = os.path.join(SOUND_DIR, filename)
                if os.path.exists(path):
                    try:
                        self.sounds[name] = pygame.mixer.Sound(path)
                        found = True
                        break # Loaded successfully
                    except:
                        print(f"Failed to load {filename}")
            
            if not found:
                print(f"SE not found for: {name} (checked .wav and .mp3)")

        self.bgm_path = None
        for ext in [".mp3", ".wav"]:
            p = os.path.join(SOUND_DIR, "bgm" + ext)
            if os.path.exists(p):
                self.bgm_path = p
                break

    def play_bgm(self):
        if not self.has_mixer or not self.bgm_enabled: return
        if not self.bgm_path: return
        
        try:
            if not self.bgm_playing:
                pygame.mixer.music.load(self.bgm_path)
                pygame.mixer.music.play(-1) # Loop
                self.bgm_playing = True
            else:
                pygame.mixer.music.unpause()
        except Exception as e:
            print(f"BGM Error: {e}")

    def stop_bgm(self):
        if not self.has_mixer: return
        pygame.mixer.music.pause() # Pause instead of stop to resume smoothly if needed

    def play_se(self, name, maxtime=0):
        if not self.has_mixer or not self.se_enabled: return
        sound = self.sounds.get(name)
        if sound:
            sound.play(maxtime=maxtime)
            
    def set_bgm_volume(self, val):
        """ val: 0.0 to 1.0 """
        if not self.has_mixer: return
        try:
            pygame.mixer.music.set_volume(val)
        except: pass

    def set_se_volume(self, val):
        """ val: 0.0 to 1.0 """
        if not self.has_mixer: return
        # Update all loaded sounds
        for sound in self.sounds.values():
            try:
                sound.set_volume(val)
            except: pass

    def toggle_bgm(self):
        self.bgm_enabled = not self.bgm_enabled
        if self.bgm_enabled:
            self.play_bgm()
        else:
            self.stop_bgm()
        return self.bgm_enabled

    def toggle_se(self):
        self.se_enabled = not self.se_enabled
        return self.se_enabled
