import sys
from managers.data_manager import DataManager
from managers.game_logic import GameLogic
from managers.audio_manager import AudioManager
from gui.app import BingoApp

def main():
    # 1. Initialize Logic
    dm = DataManager()
    logic = GameLogic(dm)
    audio = AudioManager()

    # 2. Launch GUI
    # app = BingoApp(...)
    # app.mainloop()
    
    app = BingoApp(dm, logic, audio)
    app.mainloop()

if __name__ == "__main__":
    main()
