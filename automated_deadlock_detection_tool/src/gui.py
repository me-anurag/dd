import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.font as tkfont
import time
from deadlock_algo import DeadlockDetector
from visualization.visualization import visualize_rag
from visualization.cycle_visualization import CycleVisualization
from visualization.sync_cycle_visualization import SyncCycleVisualization  # Import the new class
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

class DeadlockDetectionGUI:
    """A GUI for detecting deadlocks in a system with single-instance resources.

    Args:
        window (tk.Tk): The main Tkinter window.
        sound_manager (SoundManager): The sound manager for playing audio feedback.
    """
    def __init__(self, window, sound_manager):
        self.window = window
        self.sound_manager = sound_manager
        self.window.title("Deadlock Detection Tool")
        self.window.geometry("500x400")
        self.window.minsize(400, 300)

        self.dark_mode_on = False

        # Background canvas with gradient
        self.background_canvas = tk.Canvas(self.window, highlightthickness=0)
        self.background_canvas.pack(fill="both", expand=True)
        self.add_gradient(self.background_canvas, "#A3BFFA", "#F3F4F6", 500, 400)

        # Title and subtitle
        self.title_text = tk.Label(self.background_canvas, text="Deadlock Detection Tool",
                                   font=("Helvetica", 20, "bold"), bg="#A3BFFA", fg="#2E3A59")
        self.title_text.place(relx=0.5, rely=0.15, anchor="center")
        self.title_text.configure(fg="#A3BFFA")
        self.fade_in_title(0)

        self.subtitle_text = tk.Label(self.background_canvas, text="Choose a detection mode to begin!",
                                      font=("Helvetica", 12), bg="#A3BFFA", fg="#2E3A59")
        self.subtitle_text.place(relx=0.5, rely=0.25, anchor="center")

        # Animated gear
        self.gear_label = tk.Label(self.background_canvas, text="⚙️", font=("Helvetica", 24),
                                   bg="#A3BFFA", fg="#2E3A59")
        self.gear_label.place(relx=0.5, rely=0.35, anchor="center")
        self.rotate_gear(0)

        self.button_font = tkfont.Font(family="Helvetica", size=14)

        # Single-instance detection button
        self.button_single_frame = tk.Frame(self.background_canvas, bg="#4CAF50", bd=2, relief="raised")
        self.button_single_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.button_single_label = tk.Label(self.button_single_frame, text="Single-Instance Detection",
                                            font=self.button_font, bg="#4CAF50", fg="white", padx=10, pady=5)
        self.button_single_label.pack()
        self.button_single_frame.bind("<Button-1>", lambda e: self.open_single_window())
        self.button_single_label.bind("<Button-1>", lambda e: self.open_single_window())
        self.button_single_frame.bind("<Enter>", lambda e: self.button_single_frame.config(bg="#45A049"))
        self.button_single_frame.bind("<Leave>", lambda e: self.button_single_frame.config(bg="#4CAF50"))
        self.button_single_label.bind("<Enter>", lambda e: self.button_single_frame.config(bg="#45A049"))
        self.button_single_label.bind("<Leave>", lambda e: self.button_single_frame.config(bg="#4CAF50"))

        # Multi-instance detection button (placeholder)
        self.button_multi_frame = tk.Frame(self.background_canvas, bg="#2196F3", bd=2, relief="raised")
        self.button_multi_frame.place(relx=0.5, rely=0.6, anchor="center")
        self.button_multi_label = tk.Label(self.button_multi_frame, text="Multi-Instance Detection",
                                           font=self.button_font, bg="#2196F3", fg="white", padx=10, pady=5)
        self.button_multi_label.pack()
        self.button_multi_frame.bind("<Button-1>", lambda e: self.open_multi_window())
        self.button_multi_label.bind("<Button-1>", lambda e: self.open_multi_window())
        self.button_multi_frame.bind("<Enter>", lambda e: self.button_multi_frame.config(bg="#1E88E5"))
        self.button_multi_frame.bind("<Leave>", lambda e: self.button_multi_frame.config(bg="#2196F3"))
        self.button_multi_label.bind("<Enter>", lambda e: self.button_multi_frame.config(bg="#1E88E5"))
        self.button_multi_label.bind("<Leave>", lambda e: self.button_multi_frame.config(bg="#2196F3"))

        # Dark mode toggle
        self.dark_mode_checkbox = ttk.Checkbutton(self.background_canvas, text="Dark Mode",
                                                  command=self.switch_mode)
        self.dark_mode_checkbox.place(relx=0.5, rely=0.75, anchor="center")
        self.dark_mode_checkbox.bind("<Enter>", lambda e: self.dark_mode_checkbox.config(text="Dark Mode 🌙"))
        self.dark_mode_checkbox.bind("<Leave>", lambda e: self.dark_mode_checkbox.config(text="Dark Mode"))

        # Sound toggle
        self.sound_checkbox = ttk.Checkbutton(self.background_canvas, 
                                              text="Sound On" if sound_manager.sounds_loaded else "Sound Off",
                                              command=self.toggle_sound)
        self.sound_checkbox.place(relx=0.5, rely=0.85, anchor="center")
        print(f"Initial sound state: enabled={sound_manager.sound_enabled}, sounds_loaded={sound_manager.sounds_loaded}")

        self.resources_held = {}
        self.resources_wanted = {}

        self.window.bind("<Configure>", self.on_window_resize)
        self.on_window_resize(None)

    def toggle_sound(self):
        """Toggles sound on or off and updates the checkbox label."""
        sound_on = self.sound_manager.toggle_sound()
        self.sound_checkbox.config(text="Sound On" if sound_on else "Sound Off")
        print(f"Sound checkbox updated: text={'Sound On' if sound_on else 'Sound Off'}")

    def on_window_resize(self, event):
        """Handles window resizing by updating the canvas and font sizes."""
        new_width = self.window.winfo_width()
        new_height = self.window.winfo_height()

        self.background_canvas.config(width=new_width, height=new_height)
        self.background_canvas.delete("all")
        if self.dark_mode_on:
            self.add_gradient(self.background_canvas, "#2E3A59", "#121212", new_width, new_height)
        else:
            self.add_gradient(self.background_canvas, "#A3BFFA", "#F3F4F6", new_width, new_height)

        title_font_size = max(16, min(30, int(new_width / 25)))
        subtitle_font_size = max(10, min(18, int(new_width / 40)))
        button_font_size = max(12, min(20, int(new_width / 35)))
        gear_font_size = max(20, min(40, int(new_width / 20)))

        self.title_text.config(font=("Helvetica", title_font_size, "bold"))
        self.subtitle_text.config(font=("Helvetica", subtitle_font_size))
        self.button_font.configure(size=button_font_size)

        if hasattr(self, "gear_label") and self.gear_label.winfo_exists():
            self.gear_label.config(font=("Helvetica", gear_font_size))

    def add_gradient(self, canvas, color_start, color_end, width, height):
        """Adds a gradient background to the canvas."""
        steps = 100
        for i in range(steps):
            r1 = int(color_start[1:3], 16)
            g1 = int(color_start[3:5], 16)
            b1 = int(color_start[5:7], 16)
            r2 = int(color_end[1:3], 16)
            g2 = int(color_end[3:5], 16)
            b2 = int(color_end[5:7], 16)
            r = int(r1 + (r2 - r1) * i / steps)
            g = int(g1 + (g2 - g1) * i / steps)
            b = int(b1 + (b2 - b1) * i / steps)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y_start = i * (height / steps)
            y_end = (i + 1) * (height / steps)
            canvas.create_rectangle(0, y_start, width, y_end, fill=color, outline="")

    def fade_in_title(self, step):
        """Animates the title by fading in the color."""
        if step <= 20:
            r1, g1, b1 = 163, 191, 250
            r2, g2, b2 = 46, 58, 89
            r = int(r1 + (r2 - r1) * step / 20)
            g = int(g1 + (g2 - g1) * step / 20)
            b = int(b1 + (b2 - b1) * step / 20)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.title_text.configure(fg=color)
            self.window.after(50, self.fade_in_title, step + 1)
        else:
            self.title_text.configure(fg="#2E3A59")

    def rotate_gear(self, step):
        """Animates the gear icon by rotating it."""
        if step < 8:
            gear_positions = ["⚙️", "⚙️", "⚙️", "⚙️", "⚙️", "⚙️", "⚙️", "⚙️"]
            self.gear_label.configure(text=gear_positions[step % 8])
            self.window.after(100, self.rotate_gear, step + 1)
        else:
            self.gear_label.destroy()
            delattr(self, "gear_label")

    def switch_mode(self):
        """Toggles between light and dark mode."""
        if self.dark_mode_on:
            self.background_canvas.delete("all")
            new_width = self.window.winfo_width()
            new_height = self.window.winfo_height()
            self.add_gradient(self.background_canvas, "#A3BFFA", "#F3F4F6", new_width, new_height)
            self.title_text.config(bg="#A3BFFA", fg="#2E3A59")
            self.subtitle_text.config(bg="#A3BFFA", fg="#2E3A59")
            self.button_single_frame.config(bg="#4CAF50")
            self.button_single_label.config(bg="#4CAF50")
            self.button_multi_frame.config(bg="#2196F3")
            self.button_multi_label.config(bg="#2196F3")
            self.dark_mode_on = False
        else:
            self.background_canvas.delete("all")
            new_width = self.window.winfo_width()
            new_height = self.window.winfo_height()
            self.add_gradient(self.background_canvas, "#2E3A59", "#121212", new_width, new_height)
            self.title_text.config(bg="#2E3A59", fg="#A3BFFA")
            self.subtitle_text.config(bg="#2E3A59", fg="#A3BFFA")
            self.button_single_frame.config(bg="#66BB6A")
            self.button_single_label.config(bg="#66BB6A")
            self.button_multi_frame.config(bg="#42A5F5")
            self.button_multi_label.config(bg="#42A5F5")
            self.dark_mode_on = True

    def open_single_window(self):
        """Opens a new window for single-instance deadlock detection."""
        self.new_window = tk.Toplevel(self.window)
        self.new_window.title("Single-Instance Detection")
        self.new_window.geometry("1000x700")
        self.new_window.grab_set()

        # Input area for processes, resources, and buttons (Reset, Undo)
        input_area = tk.Frame(self.new_window)
        input_area.pack(pady=10)

        label_processes = tk.Label(input_area, text="Processes:", font=("Arial", 12))
        label_processes.pack(side=tk.LEFT, padx=5)
        self.entry_processes = tk.Entry(input_area, width=5)
        self.entry_processes.pack(side=tk.LEFT, padx=5)

        label_resources = tk.Label(input_area, text="Resources:", font=("Arial", 12))
        label_resources.pack(side=tk.LEFT, padx=5)
        self.entry_resources = tk.Entry(input_area, width=5)
        self.entry_resources.pack(side=tk.LEFT, padx=5)

        button_create = tk.Button(input_area, text="Create Canvas", font=("Arial", 12),
                                  command=self.make_canvas)
        button_create.pack(side=tk.LEFT, padx=10)

        self.button_reset = tk.Button(input_area, text="Reset", font=("Arial", 12),
                                      command=self.reset_everything, bg="#FF9800", fg="white")
        self.button_reset.pack(side=tk.LEFT, padx=5)
        self.button_reset.bind("<Enter>", lambda e: self.button_reset.config(bg="#F57C00"))
        self.button_reset.bind("<Leave>", lambda e: self.button_reset.config(bg="#FF9800"))

        self.button_undo = tk.Button(input_area, text="Undo", font=("Arial", 12),
                                     command=self.undo_last_action, bg="#FF5722", fg="white")
        self.button_undo.pack(side=tk.LEFT, padx=5)
        self.button_undo.bind("<Enter>", lambda e: self.button_undo.config(bg="#E64A19"))
        self.button_undo.bind("<Leave>", lambda e: self.button_undo.config(bg="#FF5722"))

    def make_canvas(self):
        """Creates the canvas for drag-and-drop interaction."""
        try:
            self.total_processes = int(self.entry_processes.get())
            self.total_resources = int(self.entry_resources.get())
            if self.total_processes <= 0 or self.total_resources <= 0:
                messagebox.showerror("Error", "Please enter positive numbers.", parent=self.new_window)
                return
            if self.total_processes > 10 or self.total_resources > 10:
                messagebox.showerror("Error", "Maximum 10 processes and resources allowed.", parent=self.new_window)
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.", parent=self.new_window)
            return

        # Main area for the canvas
        main_area = tk.Frame(self.new_window)
        main_area.pack(pady=10, fill=tk.BOTH, expand=True)

        # Left panel for allocations
        self.left_area = tk.Frame(main_area, width=200)
        self.left_area.pack(side=tk.LEFT, fill=tk.Y)
        self.left_canvas = tk.Canvas(self.left_area, width=200, height=500, bg="#E6F0FA")
        self.left_scroll = tk.Scrollbar(self.left_area, orient=tk.VERTICAL, command=self.left_canvas.yview)
        self.left_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_canvas.configure(yscrollcommand=self.left_scroll.set)
        self.left_inner_area = tk.Frame(self.left_canvas, bg="#E6F0FA")
        self.left_canvas.create_window((0, 0), window=self.left_inner_area, anchor="nw")
        self.left_inner_area.bind("<Configure>", lambda event: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all")))
        self.left_canvas.create_text(100, 20, text="Allocations", font=("Arial", 12, "bold"), fill="#2E3A59")

        # Center canvas for drag-and-drop (expandable)
        self.center_canvas = tk.Canvas(main_area, width=500, height=500)
        self.center_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.add_gradient(self.center_canvas, "#A3BFFA", "#F3F4F6", 500, 500)
        self.center_canvas.create_text(250, 20, text="Drag and Drop", font=("Arial", 12, "bold"), fill="#2E3A59")
        self.phase_label = self.center_canvas.create_text(250, 40, text="Allocation Phase: Drag resources to processes",
                                                         font=("Arial", 10), fill="#2E3A59")

        # Right panel for requests
        self.right_area = tk.Frame(main_area, width=200)
        self.right_area.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_canvas = tk.Canvas(self.right_area, width=200, height=500, bg="#E6F0FA")
        self.right_scroll = tk.Scrollbar(self.right_area, orient=tk.VERTICAL, command=self.right_canvas.yview)
        self.right_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_canvas.configure(yscrollcommand=self.right_scroll.set)
        self.right_inner_area = tk.Frame(self.right_canvas, bg="#E6F0FA")
        self.right_canvas.create_window((0, 0), window=self.right_inner_area, anchor="nw")
        self.right_inner_area.bind("<Configure>", lambda event: self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all")))
        self.right_canvas.create_text(100, 20, text="Requests", font=("Arial", 12, "bold"), fill="#2E3A59")

        self.main_canvas = self.center_canvas

        self.left_part_width = 200
        self.center_part_width = 500
        self.right_part_width = 200

        # Bind configure event to resize gradient
        self.center_canvas.bind("<Configure>", self.resize_center_canvas)

        # Initialize resources_held and resources_wanted
        self.resources_held = {}
        self.resources_wanted = {}
        for i in range(self.total_processes):
            process_name = f"P{i+1}"
            self.resources_held[process_name] = []
            self.resources_wanted[process_name] = []

        self.process_icon = "🤖"
        self.resource_icon = "🖥️"

        self.process_locations = {}
        self.resource_locations = {}
        self.process_items = {}
        self.resource_items = {}
        self.allocation_labels = []
        self.request_labels = []
        self.history_of_actions = []
        self.center_items = []

        self.current_phase = "allocation"
        self.show_allocation_phase(self.total_processes, self.total_resources)

        # Button frame for Finish, Detect, Visualize RAG, and Visualization
        button_frame = tk.Frame(self.new_window)
        button_frame.pack(pady=10)

        self.button_finish = tk.Button(button_frame, text="Finish Allocation", font=("Arial", 12),
                                       command=self.go_to_request_phase, bg="#2196F3", fg="white")
        self.button_finish.pack(side=tk.LEFT, padx=5)
        self.button_finish.bind("<Enter>", lambda e: self.button_finish.config(bg="#1976D2"))
        self.button_finish.bind("<Leave>", lambda e: self.button_finish.config(bg="#2196F3"))

        # Detect Deadlock button
        self.detect_frame = tk.Frame(button_frame, bg="#D32F2F", bd=3, relief="raised")
        self.detect_frame.pack(side=tk.LEFT, padx=5)
        self.button_detect_deadlock = tk.Label(self.detect_frame, text="🔍 Detect Deadlock",
                                               font=("Arial", 16, "bold"), bg="#D32F2F", fg="white", padx=20, pady=10)
        self.button_detect_deadlock.pack()
        self.detect_frame.bind("<Button-1>", lambda e: self.detect_deadlock())
        self.button_detect_deadlock.bind("<Button-1>", lambda e: self.detect_deadlock())
        self.detect_frame.bind("<Enter>", lambda e: self.detect_frame.config(bg="#B71C1C"))
        self.detect_frame.bind("<Leave>", lambda e: self.detect_frame.config(bg="#D32F2F"))
        self.button_detect_deadlock.bind("<Enter>", lambda e: self.detect_frame.config(bg="#B71C1C"))
        self.button_detect_deadlock.bind("<Leave>", lambda e: self.detect_frame.config(bg="#D32F2F"))

        # Visualize RAG button
        self.visualize_frame = tk.Frame(button_frame, bg="#4CAF50", bd=3, relief="raised")
        self.visualize_frame.pack(side=tk.LEFT, padx=5)
        self.button_visualize = tk.Label(self.visualize_frame, text="📊 Visualize RAG",
                                         font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", padx=15, pady=8)
        self.button_visualize.pack()
        self.visualize_frame.bind("<Button-1>", lambda e: self.visualize_rag())
        self.button_visualize.bind("<Button-1>", lambda e: self.visualize_rag())
        self.visualize_frame.bind("<Enter>", lambda e: self.visualize_frame.config(bg="#388E3C"))
        self.visualize_frame.bind("<Leave>", lambda e: self.visualize_frame.config(bg="#4CAF50"))
        self.button_visualize.bind("<Enter>", lambda e: self.visualize_frame.config(bg="#388E3C"))
        self.button_visualize.bind("<Leave>", lambda e: self.visualize_frame.config(bg="#4CAF50"))

        # Visualization button for Simulation, Narrative, and Synchronized
        self.cycle_viz_frame = tk.Frame(button_frame, bg="#FFC107", bd=3, relief="raised")
        self.cycle_viz_frame.pack(side=tk.LEFT, padx=5)
        self.button_cycle_viz = tk.Label(self.cycle_viz_frame, text="🎥 Visualization",
                                         font=("Arial", 14, "bold"), bg="#FFC107", fg="white", padx=15, pady=8)
        self.button_cycle_viz.pack()
        self.cycle_viz_frame.bind("<Button-1>", lambda e: self.open_cycle_visualization())
        self.button_cycle_viz.bind("<Button-1>", lambda e: self.open_cycle_visualization())
        self.cycle_viz_frame.bind("<Enter>", lambda e: self.cycle_viz_frame.config(bg="#FFA000"))
        self.cycle_viz_frame.bind("<Leave>", lambda e: self.cycle_viz_frame.config(bg="#FFC107"))
        self.button_cycle_viz.bind("<Enter>", lambda e: self.cycle_viz_frame.config(bg="#FFA000"))
        self.button_cycle_viz.bind("<Leave>", lambda e: self.cycle_viz_frame.config(bg="#FFC107"))

    def resize_center_canvas(self, event):
        """Resizes the center canvas gradient when the window size changes."""
        new_width = event.width
        new_height = event.height
        self.center_part_width = new_width
        self.main_canvas.delete("all")
        self.add_gradient(self.main_canvas, "#A3BFFA", "#F3F4F6", new_width, new_height)
        self.main_canvas.create_text(new_width // 2, 20, text="Drag and Drop", font=("Arial", 12, "bold"), fill="#2E3A59")
        self.phase_label = self.main_canvas.create_text(new_width // 2, 40, 
                                                        text="Allocation Phase: Drag resources to processes" if self.current_phase == "allocation" else "Request Phase: Drag processes to resources",
                                                        font=("Arial", 10), fill="#2E3A59")
        # Redraw items based on current phase
        if self.current_phase == "allocation":
            self.show_allocation_phase(self.total_processes, self.total_resources)
        else:
            self.show_request_phase(self.total_processes, self.total_resources)

    def visualize_rag(self):
        """Visualizes the Resource Allocation Graph using the visualization module."""
        detector = DeadlockDetector(self.resources_held, self.resources_wanted, self.total_resources)
        rag = detector.build_rag()
        if hasattr(self, "last_detector") and self.last_detector.cycle:
            visualize_rag(rag, self.resources_held, self.resources_wanted, self.last_detector.cycle, self.total_resources)
        else:
            visualize_rag(rag, self.resources_held, self.resources_wanted, total_resources=self.total_resources)

    def detect_deadlock(self):
        """Detects a deadlock and displays the result, including performance metrics."""
        try:
            start_time = time.time()
            detector = DeadlockDetector(self.resources_held, self.resources_wanted, self.total_resources)
            has_deadlock, message = detector.detect_deadlock()
            elapsed_time = time.time() - start_time
            message += f"\nDetection took {elapsed_time:.3f} seconds."
            self.last_detector = detector
            if has_deadlock:
                self.sound_manager.play_deadlock_sound()
                messagebox.showwarning("Deadlock Detected", message, parent=self.new_window)
            else:
                messagebox.showinfo("Deadlock Info", message, parent=self.new_window)
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self.new_window)

    def open_cycle_visualization(self):
        """Opens a new window with options for Simulation, Narrative, and Synchronized visualization."""
        try:
            # Validate input before proceeding
            detector = DeadlockDetector(self.resources_held, self.resources_wanted, self.total_resources)
            rag = detector.build_rag()
            if not rag:
                messagebox.showerror("Error", "No graph data available. Please allocate or request resources.", parent=self.new_window)
                return
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self.new_window)
            return

        # Create visualization window
        viz_window = tk.Toplevel(self.new_window)
        viz_window.title("Cycle Detection Visualization")
        viz_window.geometry("800x600")
        viz_window.grab_set()

        # Background canvas with gradient
        viz_canvas = tk.Canvas(viz_window, highlightthickness=0)
        viz_canvas.pack(fill="both", expand=True)
        self.add_gradient(viz_canvas, "#A3BFFA", "#F3F4F6", 800, 600)

        # Title
        title_label = tk.Label(viz_canvas, text="Cycle Detection Visualization",
                               font=("Helvetica", 20, "bold"), bg="#A3BFFA", fg="#2E3A59")
        title_label.place(relx=0.5, rely=0.1, anchor="center")

        # Button frame for Simulation, Narrative, and Synchronized
        button_frame = tk.Frame(viz_canvas, bg="#A3BFFA")
        button_frame.place(relx=0.5, rely=0.2, anchor="center")

        # Simulation button
        sim_frame = tk.Frame(button_frame, bg="#2196F3", bd=3, relief="raised")
        sim_frame.pack(side=tk.LEFT, padx=10)
        sim_button = tk.Label(sim_frame, text="🎞️ Simulation",
                              font=("Arial", 16, "bold"), bg="#2196F3", fg="white", padx=20, pady=10)
        sim_button.pack()
        sim_frame.bind("<Button-1>", lambda e: self.start_simulation(viz_window))
        sim_button.bind("<Button-1>", lambda e: self.start_simulation(viz_window))
        sim_frame.bind("<Enter>", lambda e: sim_frame.config(bg="#1976D2"))
        sim_frame.bind("<Leave>", lambda e: sim_frame.config(bg="#2196F3"))
        sim_button.bind("<Enter>", lambda e: sim_frame.config(bg="#1976D2"))
        sim_button.bind("<Leave>", lambda e: sim_frame.config(bg="#2196F3"))

        # Narrative button
        narr_frame = tk.Frame(button_frame, bg="#4CAF50", bd=3, relief="raised")
        narr_frame.pack(side=tk.LEFT, padx=10)
        narr_button = tk.Label(narr_frame, text="📜 Narrative",
                               font=("Arial", 16, "bold"), bg="#4CAF50", fg="white", padx=20, pady=10)
        narr_button.pack()
        narr_frame.bind("<Button-1>", lambda e: self.start_narrative(viz_window))
        narr_button.bind("<Button-1>", lambda e: self.start_narrative(viz_window))
        narr_frame.bind("<Enter>", lambda e: narr_frame.config(bg="#388E3C"))
        narr_frame.bind("<Leave>", lambda e: narr_frame.config(bg="#4CAF50"))
        narr_button.bind("<Enter>", lambda e: narr_frame.config(bg="#388E3C"))
        narr_button.bind("<Leave>", lambda e: narr_frame.config(bg="#4CAF50"))

        # Synchronized button
        sync_frame = tk.Frame(button_frame, bg="#FFC107", bd=3, relief="raised")
        sync_frame.pack(side=tk.LEFT, padx=10)
        sync_button = tk.Label(sync_frame, text="🔄 Synchronized",
                               font=("Arial", 16, "bold"), bg="#FFC107", fg="white", padx=20, pady=10)
        sync_button.pack()
        sync_frame.bind("<Button-1>", lambda e: self.start_synchronized(viz_window))
        sync_button.bind("<Button-1>", lambda e: self.start_synchronized(viz_window))
        sync_frame.bind("<Enter>", lambda e: sync_frame.config(bg="#FFA000"))
        sync_frame.bind("<Leave>", lambda e: sync_frame.config(bg="#FFC107"))
        sync_button.bind("<Enter>", lambda e: sync_frame.config(bg="#FFA000"))
        sync_button.bind("<Leave>", lambda e: sync_frame.config(bg="#FFC107"))

    def start_simulation(self, viz_window):
        """Starts the simulation visualization in a new window."""
        sim_window = tk.Toplevel(viz_window)
        sim_window.title("Cycle Detection Simulation")
        sim_window.geometry("1000x700")
        sim_window.grab_set()
        CycleVisualization(self, sim_window, "simulation")

    def start_narrative(self, viz_window):
        """Starts the narrative visualization in a new window."""
        narr_window = tk.Toplevel(viz_window)
        narr_window.title("Cycle Detection Narrative")
        narr_window.geometry("800x600")
        narr_window.grab_set()
        CycleVisualization(self, narr_window, "narrative")

    def start_synchronized(self, viz_window):
        """Starts the synchronized narrative and simulation visualization."""
        sync_window = tk.Toplevel(viz_window)
        sync_window.title("Cycle Detection Synchronized Visualization")
        sync_window.geometry("1200x700")
        sync_window.grab_set()
        SyncCycleVisualization(self, sync_window)

    def reset_everything(self):
        """Resets the canvas and all data to the initial state."""
        print("Resetting everything...")
        self.resources_held = {}
        self.resources_wanted = {}
        for i in range(self.total_processes):
            process_name = f"P{i+1}"
            self.resources_held[process_name] = []
            self.resources_wanted[process_name] = []
        print(f"Resources reset: held={self.resources_held}, wanted={self.resources_wanted}")

        self.history_of_actions = []
        self.current_phase = "allocation"
        self.center_items = []

        for label in self.left_inner_area.winfo_children():
            label.destroy()
        for label in self.right_inner_area.winfo_children():
            label.destroy()
        self.allocation_labels = []
        self.request_labels = []

        self.process_locations = {}
        self.resource_locations = {}
        self.process_items = {}
        self.resource_items = {}
        self.main_canvas.delete("all")
        self.add_gradient(self.main_canvas, "#A3BFFA", "#F3F4F6", self.center_part_width, 500)
        self.main_canvas.create_text(self.center_part_width // 2, 20, text="Drag and Drop", font=("Arial", 12, "bold"), fill="#2E3A59")
        self.phase_label = self.main_canvas.create_text(self.center_part_width // 2, 40, text="Allocation Phase: Drag resources to processes",
                                                       font=("Arial", 10), fill="#2E3A59")

        print("Showing allocation phase...")
        self.show_allocation_phase(self.total_processes, self.total_resources)
        self.button_finish.config(text="Finish Allocation", command=self.go_to_request_phase)

    def show_allocation_phase(self, num_processes, num_resources):
        """Displays the allocation phase where resources can be dragged to processes."""
        print(f"Center items before: {self.center_items}")
        if hasattr(self, "center_items"):
            for item in self.center_items:
                self.main_canvas.delete(item)
        self.center_items = []

        start_x = self.left_part_width
        if num_processes > 0:
            space_between = min(80, (self.center_part_width - 100) / num_processes)
            for i in range(num_processes):
                process_name = f"P{i+1}"
                x_position = start_x + 50 + i * space_between - self.left_part_width
                y_position = 100
                process_text = self.main_canvas.create_text(x_position, y_position, text=f"{process_name} {self.process_icon}",
                                                           font=("Arial", 14), tags=process_name, fill="#1A3C34")
                self.process_locations[process_name] = (x_position, y_position)
                self.process_items[process_name] = process_text
                self.center_items.append(process_text)
                self.main_canvas.tag_bind(process_name, "<Motion>", lambda event, p=process_name: self.show_info(event, p))

        if num_resources > 0:
            space_between = min(80, (self.center_part_width - 100) / num_resources)
            for i in range(num_resources):
                resource_name = f"R{i+1}"
                x_position = start_x + 50 + i * space_between - self.left_part_width
                y_position = 200
                resource_text = self.main_canvas.create_text(x_position, y_position, text=f"{resource_name} {self.resource_icon}",
                                                            font=("Arial", 14), tags=resource_name, fill="#1A3C34")
                self.resource_locations[resource_name] = (x_position, y_position)
                self.resource_items[resource_name] = resource_text
                self.center_items.append(resource_text)
                self.main_canvas.tag_bind(resource_name, "<Button-1>", lambda event, r=resource_name: self.start_dragging(event, r))
                self.main_canvas.tag_bind(resource_name, "<B1-Motion>", lambda event, r=resource_name: self.drag_item(event, r))
                self.main_canvas.tag_bind(resource_name, "<ButtonRelease-1>", lambda event, r=resource_name: self.drop_for_allocation(event, r))
                self.main_canvas.tag_bind(resource_name, "<Motion>", lambda event, r=resource_name: self.show_info(event, r))
        print(f"Center items after: {self.center_items}")

    def show_request_phase(self, num_processes, num_resources):
        """Displays the request phase where processes can be dragged to resources."""
        for item in self.center_items:
            self.main_canvas.delete(item)
        self.center_items = []

        self.main_canvas.delete(self.phase_label)
        self.phase_label = self.main_canvas.create_text(self.center_part_width // 2, 40, text="Request Phase: Drag processes to resources",
                                                       font=("Arial", 10), fill="#2E3A59")

        start_x = self.left_part_width
        if num_processes > 0:
            space_between = min(80, (self.center_part_width - 100) / num_processes)
            for i in range(num_processes):
                process_name = f"P{i+1}"
                x_position = start_x + 50 + i * space_between - self.left_part_width
                y_position = 100
                process_text = self.main_canvas.create_text(x_position, y_position, text=f"{process_name} {self.process_icon}",
                                                           font=("Arial", 14), tags=process_name, fill="#1A3C34")
                self.process_locations[process_name] = (x_position, y_position)
                self.process_items[process_name] = process_text
                self.center_items.append(process_text)
                self.main_canvas.tag_bind(process_name, "<Button-1>", lambda event, p=process_name: self.start_dragging(event, p))
                self.main_canvas.tag_bind(process_name, "<B1-Motion>", lambda event, p=process_name: self.drag_item(event, p))
                self.main_canvas.tag_bind(process_name, "<ButtonRelease-1>", lambda event, p=process_name: self.drop_for_request(event, p))
                self.main_canvas.tag_bind(process_name, "<Motion>", lambda event, p=process_name: self.show_info(event, p))

        if num_resources > 0:
            space_between = min(80, (self.center_part_width - 100) / num_resources)
            allocated_resources = []
            for process in self.resources_held:
                for resource in self.resources_held[process]:
                    allocated_resources.append(resource)
            for i in range(num_resources):
                resource_name = f"R{i+1}"
                x_position = start_x + 50 + i * space_between - self.left_part_width
                y_position = 200
                if resource_name in allocated_resources:
                    color = "red"
                else:
                    color = "green"
                resource_text = self.main_canvas.create_text(x_position, y_position, text=f"{resource_name} {self.resource_icon}",
                                                            font=("Arial", 14), tags=resource_name, fill=color)
                self.resource_locations[resource_name] = (x_position, y_position)
                self.resource_items[resource_name] = resource_text
                self.center_items.append(resource_text)
                self.main_canvas.tag_unbind(resource_name, "<Button-1>")
                self.main_canvas.tag_unbind(resource_name, "<B1-Motion>")
                self.main_canvas.tag_unbind(resource_name, "<ButtonRelease-1>")
                self.main_canvas.tag_bind(resource_name, "<Motion>", lambda event, r=resource_name: self.show_info(event, r))

    def show_info(self, event, item):
        """Shows a tooltip with information about a process or resource."""
        x = event.x
        y = event.y
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()

        if item.startswith("P"):
            process = item
            held = self.resources_held.get(process, [])
            wanted = self.resources_wanted.get(process, [])
            tooltip_text = f"{process}: Holds {held}, Requests {wanted}"
        else:
            resource = item
            holder = None
            for proc in self.resources_held:
                if resource in self.resources_held[proc]:
                    holder = proc
                    break
            requesters = []
            for proc in self.resources_wanted:
                if resource in self.resources_wanted[proc]:
                    requesters.append(proc)
            tooltip_text = f"{resource}: Held by {holder if holder else 'None'}, Requested by {requesters}"

        self.tooltip = tk.Toplevel(self.main_canvas)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{self.main_canvas.winfo_rootx() + x + 20}+{self.main_canvas.winfo_rooty() + y}")
        label = tk.Label(self.tooltip, text=tooltip_text, background="yellow", relief="solid", borderwidth=1)
        label.pack()
        self.main_canvas.bind("<Leave>", lambda e: self.hide_info())

    def hide_info(self):
        """Hides the tooltip."""
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()
            del self.tooltip

    def start_dragging(self, event, item):
        """Starts dragging an item (process or resource)."""
        self.item_being_dragged = item
        self.start_x = event.x
        self.start_y = event.y

    def drag_item(self, event, item):
        """Handles dragging an item on the canvas."""
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        self.main_canvas.move(item, dx, dy)
        self.start_x = event.x
        self.start_y = event.y
        if item.startswith("P"):
            old_x, old_y = self.process_locations[item]
            self.process_locations[item] = (old_x + dx, old_y + dy)
        else:
            old_x, old_y = self.resource_locations[item]
            self.resource_locations[item] = (old_x + dx, old_y + dy)

    def drop_for_allocation(self, event, resource):
        """Handles dropping a resource onto a process during the allocation phase."""
        drop_x = event.x
        drop_y = event.y
        target_process = None

        for process in self.process_locations:
            px, py = self.process_locations[process]
            if abs(drop_x - px) < 40 and abs(drop_y - py) < 40:
                target_process = process
                break

        if target_process:
            for proc in self.resources_held:
                if resource in self.resources_held[proc]:
                    messagebox.showerror("Error", f"{resource} is already allocated to {proc}.", parent=self.new_window)
                    self.reset_resource_position(resource)
                    return

            self.resources_held[target_process].append(resource)
            print(f"Allocation: {target_process} <- {resource}, History: {self.history_of_actions}")
            self.history_of_actions.append(("allocation", target_process, resource))
            self.sound_manager.play_allocate_sound()
            self.main_canvas.delete(self.resource_items[resource])
            self.center_items.remove(self.resource_items[resource])
            del self.resource_items[resource]
            self.show_allocations()
        else:
            self.reset_resource_position(resource)

    def drop_for_request(self, event, process):
        """Handles dropping a process onto a resource during the request phase."""
        drop_x = event.x
        drop_y = event.y
        target_resource = None

        for resource in self.resource_locations:
            rx, ry = self.resource_locations[resource]
            if abs(drop_x - rx) < 40 and abs(drop_y - ry) < 40:
                target_resource = resource
                break

        if target_resource:
            if target_resource in self.resources_held[process]:
                messagebox.showerror("Error", f"{process} already holds {target_resource}.", parent=self.new_window)
                self.reset_process_position(process)
                return
            if target_resource in self.resources_wanted[process]:
                messagebox.showerror("Error", f"{process} already requested {target_resource}.", parent=self.new_window)
                self.reset_process_position(process)
                return

            self.resources_wanted[process].append(target_resource)
            print(f"Request: {process} -> {target_resource}, History: {self.history_of_actions}")
            self.history_of_actions.append(("request", process, target_resource))
            self.sound_manager.play_request_sound()
            self.main_canvas.delete(self.process_items[process])
            self.center_items.remove(self.process_items[process])
            del self.process_items[process]
            self.show_requests()
        else:
            self.reset_process_position(process)

    def reset_resource_position(self, resource):
        """Resets a resource to its original position."""
        if resource in self.resource_items:
            original_x = self.left_part_width + 50 + (int(resource[1:]) - 1) * 80 - self.left_part_width
            original_y = 200
            self.main_canvas.coords(self.resource_items[resource], original_x, original_y)
            self.resource_locations[resource] = (original_x, original_y)

    def reset_process_position(self, process):
        """Resets a process to its original position."""
        if process in self.process_items:
            original_x = self.left_part_width + 50 + (int(process[1:]) - 1) * 80 - self.left_part_width
            original_y = 100
            self.main_canvas.coords(self.process_items[process], original_x, original_y)
            self.process_locations[process] = (original_x, original_y)

    def show_allocations(self):
        """Displays the current allocations in the left panel."""
        for widget in self.left_inner_area.winfo_children():
            widget.destroy()
        self.allocation_labels = []

        for process in self.resources_held:
            for resource in self.resources_held[process]:
                text = f"{self.process_icon} <------- {self.resource_icon} ({process} <- {resource})"
                label = tk.Label(self.left_inner_area, text=text, font=("Arial", 10), bg="#E6F0FA", fg="#2E3A59")
                label.pack(anchor="center", pady=5)
                self.allocation_labels.append(label)

        self.left_inner_area.update_idletasks()
        self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))

    def show_requests(self):
        """Displays the current requests in the right panel."""
        for widget in self.right_inner_area.winfo_children():
            widget.destroy()
        self.request_labels = []

        for process in self.resources_wanted:
            for resource in self.resources_wanted[process]:
                text = f"{self.process_icon} -------> {self.resource_icon} ({process} -> {resource})"
                label = tk.Label(self.right_inner_area, text=text, font=("Arial", 10), bg="#E6F0FA", fg="#2E3A59")
                label.pack(anchor="center", pady=5)
                self.request_labels.append(label)

        self.right_inner_area.update_idletasks()
        self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))

    def undo_last_action(self):
        """Undoes the last allocation or request action."""
        if not self.history_of_actions:
            messagebox.showinfo("Info", "Nothing to undo.", parent=self.new_window)
            return

        action_type, process, resource = self.history_of_actions.pop()
        print(f"Undoing: {action_type}, {process}, {resource}")
        if action_type == "allocation":
            self.resources_held[process].remove(resource)
            self.show_allocations()
            original_x = self.left_part_width + 50 + (int(resource[1:]) - 1) * 80 - self.left_part_width
            original_y = 200
            resource_text = self.main_canvas.create_text(original_x, original_y, text=f"{resource} {self.resource_icon}",
                                                        font=("Arial", 14), tags=resource, fill="#1A3C34")
            self.resource_locations[resource] = (original_x, original_y)
            self.resource_items[resource] = resource_text
            self.center_items.append(resource_text)
            if self.current_phase == "allocation":
                self.main_canvas.tag_bind(resource, "<Button-1>", lambda event, r=resource: self.start_dragging(event, r))
                self.main_canvas.tag_bind(resource, "<B1-Motion>", lambda event, r=resource: self.drag_item(event, r))
                self.main_canvas.tag_bind(resource, "<ButtonRelease-1>", lambda event, r=resource: self.drop_for_allocation(event, r))
                self.main_canvas.tag_bind(resource, "<Motion>", lambda event, r=resource: self.show_info(event, r))
        else:
            self.resources_wanted[process].remove(resource)
            self.show_requests()
            original_x = self.left_part_width + 50 + (int(process[1:]) - 1) * 80 - self.left_part_width
            original_y = 100
            process_text = self.main_canvas.create_text(original_x, original_y, text=f"{process} {self.process_icon}",
                                                       font=("Arial", 14), tags=process, fill="#1A3C34")
            self.process_locations[process] = (original_x, original_y)
            self.process_items[process] = process_text
            self.center_items.append(process_text)
            if self.current_phase == "request":
                self.main_canvas.tag_bind(process, "<Button-1>", lambda event, p=process: self.start_dragging(event, p))
                self.main_canvas.tag_bind(process, "<B1-Motion>", lambda event, p=process: self.drag_item(event, p))
                self.main_canvas.tag_bind(process, "<ButtonRelease-1>", lambda event, p=process: self.drop_for_request(event, p))
                self.main_canvas.tag_bind(process, "<Motion>", lambda event, p=process: self.show_info(event, p))
        print(f"After undo: held={self.resources_held}, wanted={self.resources_wanted}")

    def go_to_request_phase(self):
        """Switches to the request phase."""
        self.current_phase = "request"
        num_processes = len(self.resources_held)
        all_resources = set()
        for resources in self.resources_held.values():
            for r in resources:
                all_resources.add(r)
        for resources in self.resources_wanted.values():
            for r in resources:
                all_resources.add(r)
        num_resources = len(all_resources)
        self.show_request_phase(num_processes, num_resources)
        self.button_finish.config(text="Finish Request Allocation", command=self.finish_all)

    def finish_all(self):
        """Completes all phases and displays the final state."""
        print("Allocations:", self.resources_held)
        print("Requests:", self.resources_wanted)
        messagebox.showinfo("Done", "All phases completed. Check the console for details.", parent=self.new_window)

    def open_multi_window(self):
        from multi_gui import MultiInstanceDeadlockGUI
        self.new_window = tk.Toplevel(self.window)
        self.new_window.title("Multi-Instance Detection")
        app = MultiInstanceDeadlockGUI(self.new_window, self.sound_manager)
        self.new_window.grab_set()