from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSpinBox, QTextEdit, QComboBox, QSlider)
from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation, QRect, QEvent
from PyQt6.QtGui import QIcon, QFont
from datetime import datetime, timedelta
from config_manager import ConfigManager
from utils import play_sound

class PomodoroApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.is_resting = False
        self.time_remaining = 0
        self.start_time = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.opacity_level = self.config_manager.config.get('opacity', 50)
        self.initUI()
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.opacity_active = True  # Set to True by default
        self.opacity_timer = QTimer(self)
        self.opacity_timer.timeout.connect(self.apply_opacity)
        self.opacity_timer.setSingleShot(True)
        
        self.resizeEvent = self.resizeEvent  # Connect the resize event

    def initUI(self):
        self.setWindowTitle('Pomodoro App')
        self.setWindowIcon(QIcon('tomato.png'))
        self.setGeometry(100, 100, 500, 400)
        self.setMinimumSize(200, 150)  # Set minimum size
        
        # Main layout as horizontal
        self.main_layout = QHBoxLayout()
        
        # Left side (timer and controls)
        left_layout = QVBoxLayout()
        
        # Timer section
        self.timer_widget = QWidget()
        timer_layout = QVBoxLayout(self.timer_widget)
        self.time_label = QLabel(f'{self.config_manager.config["timer_duration"]:02d}:00')
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont('Arial', 48, QFont.Weight.Bold))
        
        self.timer_controls = QHBoxLayout()
        self.time_spinbox = QSpinBox()
        self.time_spinbox.setRange(1, 60)
        self.time_spinbox.setValue(self.config_manager.config["timer_duration"])
        self.time_spinbox.valueChanged.connect(self.update_timer_duration)
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_timer)
        self.abort_button = QPushButton('Give up')
        self.abort_button.clicked.connect(self.abort_timer)
        self.abort_button.setEnabled(False)
        
        self.timer_controls.addWidget(self.time_spinbox)
        self.timer_controls.addWidget(self.start_button)
        self.timer_controls.addWidget(self.abort_button)
        
        timer_layout.addWidget(self.time_label)
        timer_layout.addLayout(self.timer_controls)
        
        left_layout.addWidget(self.timer_widget)
        
        # Rest of the UI (will be hidden when window is small)
        self.rest_of_ui = QWidget()
        rest_layout = QVBoxLayout(self.rest_of_ui)
        
        # Rest time settings
        rest_time_layout = QHBoxLayout()
        rest_time_layout.addWidget(QLabel("Rest time (min):"))
        self.rest_spinbox = QSpinBox()
        self.rest_spinbox.setRange(1, 15)
        self.rest_spinbox.setValue(self.config_manager.config["rest_duration"])
        self.rest_spinbox.valueChanged.connect(self.update_rest_duration)
        rest_time_layout.addWidget(self.rest_spinbox)
        rest_layout.addLayout(rest_time_layout)
        
        # Buttons for showing/hiding sections and floating
        buttons_layout = QHBoxLayout()
        self.notes_button = QPushButton('Notes')
        self.notes_button.clicked.connect(self.toggle_note)
        self.float_button = QPushButton('Float')
        self.float_button.clicked.connect(self.toggle_float)
        buttons_layout.addWidget(self.notes_button)
        buttons_layout.addWidget(self.float_button)
        rest_layout.addLayout(buttons_layout)
        
        # Opacity control
        opacity_layout = QHBoxLayout()
        self.opacity_label = QLabel(f'Opacity: {self.opacity_level}%')
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)  # Set range from 20% to 100%
        self.opacity_slider.setValue(self.opacity_level)
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        self.opacity_slider.sliderReleased.connect(self.apply_opacity)  # Add this line
        opacity_layout.addWidget(self.opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        rest_layout.addLayout(opacity_layout)

        left_layout.addWidget(self.rest_of_ui)

        # Note section (hidden by default)
        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("Quick notes...")
        self.note_edit.setText(self.config_manager.config.get("notes", ""))
        self.note_edit.textChanged.connect(self.save_notes)
        self.note_edit.hide()
        left_layout.addWidget(self.note_edit)

        self.main_layout.addLayout(left_layout)

        # Right side (stats)
        right_layout = QVBoxLayout()
        self.stats_widget = QWidget()
        stats_layout = QVBoxLayout(self.stats_widget)
        self.today_label = QLabel()
        stats_layout.addWidget(self.today_label)
        self.week_label = QLabel()
        stats_layout.addWidget(self.week_label)
        self.month_label = QLabel()
        stats_layout.addWidget(self.month_label)
        right_layout.addWidget(self.stats_widget)
        right_layout.addStretch(1)  # Push stats to the top

        self.main_layout.addLayout(right_layout)

        self.setLayout(self.main_layout)
        
        self.update_stats()
        self.update_widget_visibility()

    def update_opacity(self, value):
        self.opacity_level = value
        self.opacity_label.setText(f'Opacity: {self.opacity_level}%')
        self.config_manager.config['opacity'] = self.opacity_level
        self.config_manager.save_config()
        self.setWindowOpacity(self.opacity_level / 100)

    def apply_opacity(self):
        if self.opacity_active:
            self.setWindowOpacity(self.opacity_level / 100)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Enter:
            self.setWindowOpacity(1.0)
        elif event.type() == QEvent.Type.Leave:
            if self.opacity_active:
                self.apply_opacity()
        return super().eventFilter(obj, event)

    def update_widget_visibility(self):
        small_window = self.width() < 300 or self.height() < 200
        self.rest_of_ui.setVisible(not small_window)
        self.time_spinbox.setVisible(not small_window)
        self.stats_widget.setVisible(not small_window)
        
        # Always show timer, start, and give up buttons
        self.time_label.setVisible(True)
        self.start_button.setVisible(True)
        self.abort_button.setVisible(True)

        # Adjust layout for small window
        if small_window:
            self.timer_controls.removeWidget(self.time_spinbox)
            self.time_spinbox.hide()
        else:
            if self.time_spinbox not in self.timer_controls.children():
                self.timer_controls.insertWidget(0, self.time_spinbox)
            self.time_spinbox.show()

    def update_timer_duration(self, value):
        self.config_manager.config["timer_duration"] = value
        self.config_manager.save_config()

    def start_timer(self):
        if not self.is_resting:
            self.time_remaining = self.time_spinbox.value() * 60
        else:
            self.time_remaining = self.config_manager.config["rest_duration"] * 60
        self.timer.start(1000)
        self.start_button.setEnabled(False)
        self.abort_button.setEnabled(True)
        self.start_time = datetime.now()

    def abort_timer(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.abort_button.setEnabled(False)
        self.time_label.setText(f'{self.time_spinbox.value():02d}:00')
        if not self.is_resting:
            self.config_manager.config['aborted_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M:%S'),
                'duration': self.time_spinbox.value()
            })
            self.config_manager.save_config()
            self.update_stats()
        self.is_resting = False

    def update_timer(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            minutes, seconds = divmod(self.time_remaining, 60)
            self.time_label.setText(f'{minutes:02d}:{seconds:02d}')
        else:
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.abort_button.setEnabled(False)
            play_sound()
            self.blink_and_shake()
            
            if not self.is_resting:
                self.config_manager.config['pomodoro_history'].append({
                    'date': self.start_time.strftime('%Y-%m-%d'),
                    'start_time': self.start_time.strftime('%H:%M:%S'),
                    'end_time': datetime.now().strftime('%H:%M:%S'),
                    'duration': self.time_spinbox.value()
                })
                self.config_manager.save_config()
                self.update_stats()
                self.is_resting = True
                self.time_label.setText(f'{self.config_manager.config["rest_duration"]:02d}:00')
                self.start_timer()
            else:
                self.is_resting = False
                self.time_label.setText(f'{self.time_spinbox.value():02d}:00')

    def blink_and_shake(self):
        def reset_style():
            self.setStyleSheet("")
        
        for i in range(5):  # Blink 5 times
            self.setStyleSheet("background-color: yellow;")
            QTimer.singleShot(200, reset_style)
            QTimer.singleShot(400, lambda: self.setStyleSheet("background-color: yellow;"))
            QTimer.singleShot(600, reset_style)
        
        # Shake animation
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(500)
        animation.setLoopCount(5)
        
        start = self.geometry()
        
        animation.setKeyValueAt(0, start)
        animation.setKeyValueAt(0.25, start.translated(5, 0))
        animation.setKeyValueAt(0.5, start)
        animation.setKeyValueAt(0.75, start.translated(-5, 0))
        animation.setKeyValueAt(1, start)
        
        animation.start()

    def update_stats(self):
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Today's stats
        today_completed = sum(1 for p in self.config_manager.config['pomodoro_history'] 
                              if datetime.strptime(p['date'], '%Y-%m-%d').date() == today)
        today_aborted = sum(1 for p in self.config_manager.config['aborted_history'] 
                            if datetime.strptime(p['date'], '%Y-%m-%d').date() == today)
        today_minutes = sum(p['duration'] for p in self.config_manager.config['pomodoro_history'] 
                            if datetime.strptime(p['date'], '%Y-%m-%d').date() == today)
        today_hours = today_minutes / 60

        self.today_label.setText(f"Today:\nComp: {today_completed}\nFail: {today_aborted}\nLength: {today_hours:.2f} hours")

        # Past 7 days stats
        week_completed = sum(1 for p in self.config_manager.config['pomodoro_history'] 
                             if datetime.strptime(p['date'], '%Y-%m-%d').date() > week_ago)
        week_aborted = sum(1 for p in self.config_manager.config['aborted_history'] 
                           if datetime.strptime(p['date'], '%Y-%m-%d').date() > week_ago)
        week_minutes = sum(p['duration'] for p in self.config_manager.config['pomodoro_history'] 
                           if datetime.strptime(p['date'], '%Y-%m-%d').date() > week_ago)
        week_hours = week_minutes / 60

        self.week_label.setText(f"Past 7 days:\nComp: {week_completed}\nFail: {week_aborted}\nLength: {week_hours:.2f} hours")

        # Past month stats
        month_completed = sum(1 for p in self.config_manager.config['pomodoro_history'] 
                              if datetime.strptime(p['date'], '%Y-%m-%d').date() > month_ago)
        month_aborted = sum(1 for p in self.config_manager.config['aborted_history'] 
                            if datetime.strptime(p['date'], '%Y-%m-%d').date() > month_ago)
        month_minutes = sum(p['duration'] for p in self.config_manager.config['pomodoro_history'] 
                            if datetime.strptime(p['date'], '%Y-%m-%d').date() > month_ago)
        month_hours = month_minutes / 60

        self.month_label.setText(f"Past month:\nComp: {month_completed}\nFail: {month_aborted}\nLength: {month_hours:.2f} hours")

    def update_rest_duration(self, value):
        self.config_manager.config["rest_duration"] = value
        self.config_manager.save_config()

    def toggle_note(self):
        self.note_edit.setVisible(not self.note_edit.isVisible())
        self.update_widget_visibility()

    def toggle_float(self):
        if self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.float_button.setStyleSheet("")
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            self.float_button.setStyleSheet("background-color: lightblue;")
        self.show()

    def save_notes(self):
        self.config_manager.config['notes'] = self.note_edit.toPlainText()
        self.config_manager.save_config()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_widget_visibility()