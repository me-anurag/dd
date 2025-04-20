import pygame
import logging
import os

# Configure logging to write errors to a file and console
logging.basicConfig(
    level=logging.ERROR,
    handlers=[
        logging.FileHandler('deadlock_detection.log'),
        logging.StreamHandler()
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
        pop_sound_path (str): Path to the sound file for input data display.
    """
    def __init__(self, radar_sound_path, click_sound_path, chime_sound_path, suspense_sound_path, 
                 deadlock_sound_path, safe_sound_path, rewind_sound_path, pop_sound_path):
        self.sound_enabled = False
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
            self.pop_sound = pygame.mixer.Sound(pop_sound_path)
            print(f"Loaded pop sound: {pop_sound_path}")
            self.sounds_loaded = True
            self.sound_enabled = True
            logging.info(f"Sounds loaded successfully: radar={radar_sound_path}, click={click_sound_path}, chime={chime_sound_path}, suspense={suspense_sound_path}, deadlock={deadlock_sound_path}, safe={safe_sound_path}, rewind={rewind_sound_path}, pop={pop_sound_path}")
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

    def play_sound_with_fadeout(self, sound_type, fadeout_ms):
        """Plays a sound with a specified fadeout duration to prevent overlap.

        Args:
            sound_type (str): Type of sound to play ('radar', 'click', 'chime', etc.).
            fadeout_ms (int): Duration in milliseconds after which to fade out the sound.
        """
        if not self.sound_enabled or not self.sounds_loaded:
            print(f"Sound {sound_type} not played: enabled={self.sound_enabled}, loaded={self.sounds_loaded}")
            return

        # Stop any currently playing sounds to prevent overlap
        pygame.mixer.stop()

        sound = None
        if sound_type == "radar":
            sound = self.radar_sound
        elif sound_type == "click":
            sound = self.click_sound
        elif sound_type == "chime":
            sound = self.chime_sound
        elif sound_type == "suspense":
            sound = self.suspense_sound
        elif sound_type == "deadlock":
            sound = self.deadlock_sound
        elif sound_type == "safe":
            sound = self.safe_sound
        elif sound_type == "rewind":
            sound = self.rewind_sound
        elif sound_type == "pop":
            sound = self.pop_sound

        if sound:
            try:
                print(f"Playing {sound_type} sound with {fadeout_ms}ms fadeout")
                sound.play()
                sound.fadeout(fadeout_ms)
            except Exception as e:
                logging.error(f"Error playing {sound_type} sound: {e}")
                print(f"Error playing {sound_type} sound: {e}")

    def play_radar_sound(self):
        """Plays the sound for start of detection."""
        self.play_sound_with_fadeout("radar", 1500)

    def play_click_sound(self):
        """Plays the sound for checking a process."""
        self.play_sound_with_fadeout("click", 1500)

    def play_chime_sound(self):
        """Plays the sound for resource allocation."""
        self.play_sound_with_fadeout("chime", 1500)

    def play_suspense_sound(self):
        """Plays the sound for wait detection."""
        self.play_sound_with_fadeout("suspense", 1500)

    def play_deadlock_sound(self):
        """Plays the sound for deadlock detection."""
        self.play_sound_with_fadeout("deadlock", 1500)

    def play_safe_sound(self):
        """Plays the sound for a safe state."""
        self.play_sound_with_fadeout("safe", 1500)

    def play_rewind_sound(self):
        """Plays the sound for backtracking/retry."""
        self.play_sound_with_fadeout("rewind", 1500)

    def play_pop_sound(self):
        """Plays the sound for input data display."""
        self.play_sound_with_fadeout("pop", 1500)