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
            self.has_mixer = True
        except Exception as e:
            print(f"Audio init failed: {e}")
            self.has_mixer = False

        self.sounds = {}
        self._load_sounds()

    def _load_sounds(self):
        if not self.has_mixer: return
        
        # Define paths
        files = {
            "move": "move.wav",
            "decide": "decide.wav"
        }
        
        for name, filename in files.items():
            path = os.path.join(SOUND_DIR, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except:
                    print(f"Failed to load {filename}")

        self.bgm_path = os.path.join(SOUND_DIR, "bgm.mp3")

    def play_bgm(self):
        if not self.has_mixer or not self.bgm_enabled: return
        if not os.path.exists(self.bgm_path): return
        
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

    def play_se(self, name):
        if not self.has_mixer or not self.se_enabled: return
        sound = self.sounds.get(name)
        if sound:
            sound.play()

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
