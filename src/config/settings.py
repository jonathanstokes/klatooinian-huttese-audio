"""
Settings persistence for Klatooinian Huttese Audio.

Handles loading and saving user preferences to a JSON file in a
platform-appropriate configuration directory.
"""
import json
from pathlib import Path
from typing import Optional, Any
import sounddevice as sd
from platformdirs import user_config_dir


# Application name for config directory
APP_NAME = "klatooinian-huttese"
APP_AUTHOR = "jonathanstokes"

# Default settings
DEFAULT_SETTINGS = {
    'engine': 'simple',
    'voice': 'Lee',
    'seed': 42,
    'semitones': -2,
    'grit_drive': 0,
    'grit_color': 10,
    'chorus_ms': 0,
    'grit_mode': 'combo',
    'tempo': 0.9,
    'strip_every_nth': 3,
    'output_device': None,  # None = system default
}


def get_config_dir() -> Path:
    """Get the platform-appropriate configuration directory."""
    config_dir = Path(user_config_dir(APP_NAME, APP_AUTHOR))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_settings_file() -> Path:
    """Get the path to the settings file."""
    return get_config_dir() / "settings.json"


def find_device_by_name(device_name: str) -> Optional[int]:
    """
    Find an audio device by name and return its index.
    
    Args:
        device_name: The name of the device to find
        
    Returns:
        The device index if found, None otherwise
    """
    if not device_name:
        return None
    
    try:
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            # Only consider devices with output channels
            if device['max_output_channels'] > 0:
                if device['name'] == device_name:
                    return i
    except Exception as e:
        print(f"Error querying audio devices: {e}")
    
    return None


def get_device_name(device_index: Optional[int]) -> Optional[str]:
    """
    Get the name of an audio device by its index.
    
    Args:
        device_index: The index of the device, or None for system default
        
    Returns:
        The device name if found, None for system default or if not found
    """
    if device_index is None:
        return None
    
    try:
        devices = sd.query_devices()
        if 0 <= device_index < len(devices):
            device = devices[device_index]
            if device['max_output_channels'] > 0:
                return device['name']
    except Exception as e:
        print(f"Error querying audio devices: {e}")
    
    return None


def load_settings() -> dict[str, Any]:
    """
    Load settings from the settings file.
    
    Returns a dictionary with the loaded settings. If the file doesn't exist
    or is corrupted, returns default settings. The 'output_device' field will
    contain a device index (or None for system default).
    """
    settings = DEFAULT_SETTINGS.copy()
    settings_file = get_settings_file()
    
    if not settings_file.exists():
        return settings
    
    try:
        with open(settings_file, 'r') as f:
            saved_settings = json.load(f)
        
        # Merge saved settings with defaults (in case new settings were added)
        settings.update(saved_settings)
        
        # Convert device name to device index
        device_name = settings.get('output_device_name')
        if device_name:
            device_index = find_device_by_name(device_name)
            if device_index is not None:
                settings['output_device'] = device_index
                print(f"Restored audio device: {device_name} (index {device_index})")
            else:
                # Device not found, fall back to system default
                settings['output_device'] = None
                print(f"Previously selected device '{device_name}' not found, using system default")
        else:
            settings['output_device'] = None
        
        # Remove the device name from settings (we only use it for persistence)
        settings.pop('output_device_name', None)
        
    except Exception as e:
        print(f"Error loading settings: {e}")
        print("Using default settings")
    
    return settings


def save_settings(settings: dict[str, Any]) -> None:
    """
    Save settings to the settings file.
    
    The 'output_device' field should contain a device index (or None for
    system default). This will be converted to a device name for storage.
    """
    settings_file = get_settings_file()
    
    try:
        # Convert device index to device name for storage
        settings_to_save = settings.copy()
        device_index = settings_to_save.get('output_device')
        device_name = get_device_name(device_index)
        
        # Store the device name instead of the index
        settings_to_save['output_device_name'] = device_name
        settings_to_save.pop('output_device', None)
        
        # Write to file
        with open(settings_file, 'w') as f:
            json.dump(settings_to_save, f, indent=2)
        
        if device_name:
            print(f"Settings saved (device: {device_name})")
        else:
            print("Settings saved (device: system default)")
            
    except Exception as e:
        print(f"Error saving settings: {e}")

