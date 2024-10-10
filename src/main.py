from pomodoro_app import PomodoroApp
from PyQt6.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)
    pomodoro_app = PomodoroApp()
    pomodoro_app.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()