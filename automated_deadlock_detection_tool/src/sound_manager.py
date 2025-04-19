import pygame
import logging

# Configure logging to write errors to a file and console
logging.basicConfig(
    level=logging.ERROR,
    handlers=[
        logging.FileHandler('deadlock_detection.log'),
        logging.StreamHandler()  # Also output to console
    ]
)

class SoundManager:
    """Manages sound effects for the deadlock detection tool.

    Args:
        allocate_sound_path (str): Path to the sound file for allocation events.
        request_sound_path (str): Path to the sound file for request events.
        deadlock_sound_path (str): Path to the sound file for deadlock detection events.
        safe_sound_path (str): Path to the sound file for safe state (no deadlock) events.
    """
    def __init__(self, allocate_sound_path, request_sound_path, deadlock_sound_path, safe_sound_path="assets/safe_sound.wav"):
        self.sound_enabled = False  # Start as False, set to True only if all succeeds
        self.sounds_loaded = False
        try:
            pygame.mixer.init()
            print("Pygame mixer initialized successfully")
            logging.info("Pygame mixer initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize pygame mixer: {e}"
            logging.error(error_msg)
            print(error_msg)
            return

        try:
            self.allocate_sound = pygame.mixer.Sound(allocate_sound_path)
            print(f"Loaded allocate sound: {allocate_sound_path}")
            self.request_sound = pygame.mixer.Sound(request_sound_path)
            print(f"Loaded request sound: {request_sound_path}")
            self.deadlock_sound = pygame.mixer.Sound(deadlock_sound_path)
            print(f"Loaded deadlock sound: {deadlock_sound_path}")
            self.safe_sound = pygame.mixer.Sound(safe_sound_path)
            print(f"Loaded safe state sound: {safe_sound_path}")
            self.sounds_loaded = True
            self.sound_enabled = True  # Enable only if all sounds load
            logging.info(f"Sounds loaded successfully: allocate={allocate_sound_path}, request={request_sound_path}, deadlock={deadlock_sound_path}, safe={safe_sound_path}")
        except Exception as e:
            error_msg = f"Error loading sounds: {e}"
            logging.error(error_msg)
            print(error_msg)
            self.sound_enabled = False
            self.sounds_loaded = False

        print(f"SoundManager initialized with sound_enabled={self.sound_enabled}, sounds_loaded={self.sounds_loaded}")

    def toggle_sound(self):
        """Toggles sound on or off.

        Returns:
            bool: True if sound is enabled, False otherwise.
        """
        if not self.sounds_loaded:
            print("Sounds not loaded, cannot toggle.")
            logging.warning("Toggle attempted but sounds not loaded.")
            return False
        self.sound_enabled = not self.sound_enabled
        print(f"Sound toggled: enabled={self.sound_enabled}")
        logging.info(f"Sound toggled: enabled={self.sound_enabled}")
        return self.sound_enabled

    def play_allocate_sound(self):
        """Plays the sound for an allocation event."""
        print(f"Attempting to play allocate sound: enabled={self.sound_enabled}, sound={self.allocate_sound}")
        if self.sound_enabled and self.allocate_sound:
            self.allocate_sound.play()

    def play_request_sound(self):
        """Plays the sound for a request event."""
        print(f"Attempting to play request sound: enabled={self.sound_enabled}, sound={self.request_sound}")
        if self.sound_enabled and self.request_sound:
            self.request_sound.play()

    def play_deadlock_sound(self):
        """Plays the sound for a deadlock detection event."""
        print(f"Attempting to play deadlock sound: enabled={self.sound_enabled}, sound={self.deadlock_sound}")
        if self.sound_enabled and self.deadlock_sound:
            self.deadlock_sound.play()

    def play_safe_sound(self):
        """Plays the sound for a safe state (no deadlock) event."""
        print(f"Attempting to play safe state sound: enabled={self.sound_enabled}, sound={self.safe_sound}")
        if self.sound_enabled and self.safe_sound:
            self.safe_sound.play()