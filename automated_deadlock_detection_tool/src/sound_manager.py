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
        radar_sound_path (str): Path to the sound file for start of detection.
        click_sound_path (str): Path to the sound file for process checks.
        chime_sound_path (str): Path to the sound file for resource allocation.
        suspense_sound_path (str): Path to the sound file for wait detection.
        deadlock_sound_path (str): Path to the sound file for deadlock detection.
        safe_sound_path (str): Path to the sound file for safe state.
        rewind_sound_path (str): Path to the sound file for backtracking/retry.
    """
    def __init__(self, radar_sound_path, click_sound_path, chime_sound_path, suspense_sound_path, 
                 deadlock_sound_path, safe_sound_path, rewind_sound_path):
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
            self.radar_sound = pygame.mixer.Sound(radar_sound_path)
            print(f"Loaded radar sound: {radar_sound_path}")
            self.click_sound = pygame.mixer.Sound(click_sound_path)
            print(f"Loaded click sound: {click_sound_path}")
            self.chime_sound = pygame.mixer.Sound(chime_sound_path)
            print(f"Loaded chime sound: {chime_sound_path}")
            self.suspense_sound = pygame.mixer.Sound(suspense_sound_path)
            print(f"Loaded suspense sound: {suspense_sound_path}")
            self.deadlock_sound = pygame.mixer.Sound(deadlock_sound_path)
            print(f"Loaded deadlock sound: {deadlock_sound_path}")
            self.safe_sound = pygame.mixer.Sound(safe_sound_path)
            print(f"Loaded safe state sound: {safe_sound_path}")
            self.rewind_sound = pygame.mixer.Sound(rewind_sound_path)
            print(f"Loaded rewind sound: {rewind_sound_path}")
            self.sounds_loaded = True
            self.sound_enabled = True  # Enable onlymarshall
            logging.info(f"Sounds loaded successfully: radar={radar_sound_path}, click={click_sound_path}, chime={chime_sound_path}, suspense={suspense_sound_path}, deadlock={deadlock_sound_path}, safe={safe_sound_path}, rewind={rewind_sound_path}")
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

    def play_radar_sound(self):
        """Plays the sound for start of detection."""
        print(f"Attempting to play radar sound: enabled={self.sound_enabled}, sound={self.radar_sound}")
        if self.sound_enabled and self.radar_sound:
            self.radar_sound.play()

    def play_click_sound(self):
        """Plays the sound for checking a process."""
        print(f"Attempting to play click sound: enabled={self.sound_enabled}, sound={self.click_sound}")
        if self.sound_enabled and self.click_sound:
            self.click_sound.play()

    def play_chime_sound(self):
        """Plays the sound for resource allocation."""
        print(f"Attempting to play chime sound: enabled={self.sound_enabled}, sound={self.chime_sound}")
        if self.sound_enabled and self.chime_sound:
            self.chime_sound.play()

    def play_suspense_sound(self):
        """Plays the sound for wait detection."""
        print(f"Attempting to play suspense sound: enabled={self.sound_enabled}, sound={self.suspense_sound}")
        if self.sound_enabled and self.suspense_sound:
            self.suspense_sound.play()

    def play_deadlock_sound(self):
        """Plays the sound for deadlock detection."""
        print(f"Attempting to play deadlock sound: enabled={self.sound_enabled}, sound={self.deadlock_sound}")
        if self.sound_enabled and self.deadlock_sound:
            self.deadlock_sound.play()

    def play_safe_sound(self):
        """Plays the sound for a safe state."""
        print(f"Attempting to play safe state sound: enabled={self.sound_enabled}, sound={self.safe_sound}")
        if self.sound_enabled and self.safe_sound:
            self.safe_sound.play()

    def play_rewind_sound(self):
        """Plays the sound for backtracking/retry."""
        print(f"Attempting to play rewind sound: enabled={self.sound_enabled}, sound={self.rewind_sound}")
        if self.sound_enabled and self.rewind_sound:
            self.rewind_sound.play()