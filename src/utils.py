from playsound import playsound
import os
from PyQt6.QtWidgets import QApplication

def play_sound():
    try:
        if os.path.exists('ring.mp3'):
            playsound('ring.mp3')
        else:
            print("Sound file 'ring.mp3' not found. Using system beep instead.")
            QApplication.beep()
    except Exception as e:
        print(f"Error playing sound: {e}")
        QApplication.beep()