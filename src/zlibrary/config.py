"""
Configuration management for Z-Library Search Application
"""
import json
import os
from typing import Optional, Dict, Any

from zlibrary.constants import DEFAULT_CONFIG, ENV_VAR_MAPPING, ConfigKeys


class Config:
    """Configuration class to manage application settings"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or 'config.json'
        self.settings = self._load_config()

        # Use centralized defaults from constants
        self.defaults = DEFAULT_CONFIG.copy()

        # Apply defaults for missing settings
        for key, value in self.defaults.items():
            if key not in self.settings:
                self.settings[key] = value

        # Override with environment variables
        self._apply_environment_overrides()
        
        # Validate configuration
        self._validate_config()

    def _apply_environment_overrides(self):
        """Apply configuration overrides from environment variables."""
        for env_var, config_key in ENV_VAR_MAPPING.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                # Convert string to appropriate type based on default value
                default_value = self.defaults[config_key]
                if isinstance(default_value, bool):
                    # Convert string to boolean (case-insensitive)
                    self.settings[config_key] = env_value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(default_value, int):
                    try:
                        self.settings[config_key] = int(env_value)
                    except ValueError:
                        print(f"Warning: Invalid value for {env_var}: {env_value}. Using default: {default_value}")
                elif isinstance(default_value, float):
                    try:
                        self.settings[config_key] = float(env_value)
                    except ValueError:
                        print(f"Warning: Invalid value for {env_var}: {env_value}. Using default: {default_value}")
                else:
                    # For string values, just use the environment variable value
                    self.settings[config_key] = env_value
    
    def _validate_config(self):
        """Validate configuration values."""
        # Validate timeout is positive
        timeout = self.settings.get(ConfigKeys.REQUEST_TIMEOUT)
        if timeout is not None and timeout <= 0:
            print(f"Warning: Invalid request_timeout {timeout}. Using default.")
            self.settings[ConfigKeys.REQUEST_TIMEOUT] = self.defaults[ConfigKeys.REQUEST_TIMEOUT]
        
        # Validate max_retries is non-negative
        max_retries = self.settings.get(ConfigKeys.MAX_RETRIES)
        if max_retries is not None and max_retries < 0:
            print(f"Warning: Invalid max_retries {max_retries}. Using default.")
            self.settings[ConfigKeys.MAX_RETRIES] = self.defaults[ConfigKeys.MAX_RETRIES]
        
        # Validate max_pages is positive
        max_pages = self.settings.get(ConfigKeys.MAX_PAGES)
        if max_pages is not None and max_pages <= 0:
            print(f"Warning: Invalid max_pages {max_pages}. Using default.")
            self.settings[ConfigKeys.MAX_PAGES] = self.defaults[ConfigKeys.MAX_PAGES]
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # Only parse if file is not empty
                    return json.loads(content)
        return {}

    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get a configuration value"""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set a configuration value"""
        self.settings[key] = value