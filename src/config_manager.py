import os
import yaml
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / 'pomodoro_config.yaml'
        self.config = self._load_config()

    def _get_config_dir(self):
        if os.name == 'posix':  # macOS or Linux
            config_dir = Path.home() / '.config' / 'pomodoro_app'
        elif os.name == 'nt':  # Windows
            config_dir = Path(os.getenv('APPDATA')) / 'pomodoro_app'
        else:
            raise OSError("Unsupported operating system")
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def _load_config(self):
        default_config = {
            'pomodoro_history': [],
            'aborted_history': [],
            'timer_duration': 25,
            'rest_duration': 5,
            'notes': '',
            'opacity': 80
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f)
            except (yaml.YAMLError, IOError) as e:
                print(f"Error loading config file: {e}")
                return default_config
        else:
            return default_config

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f)
        except IOError as e:
            print(f"Error saving config file: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()