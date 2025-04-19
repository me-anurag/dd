import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
from multi_deadlock_algo import MultiInstanceDeadlockDetector
from multi_visualization import visualize_multi_rag  # Import the new visualization

class MultiInstanceDeadlockGUI:
    """A GUI for detecting deadlocks in a system with multi-instance resources.

    Args:
        window (tk.Tk): The main Tkinter window.
        sound_manager (SoundManager): The sound manager for playing audio feedback.
    """
    def __init__(self, window, sound_manager):
        self.window = window
        self.sound_manager = sound_manager
        self.window.title("Multi-Instance Deadlock Detection")
        self.window.geometry("500x300")
        self.window.minsize(400, 200)

        # Background canvas with gradient
        self.background_canvas = tk.Canvas(self.window, highlightthickness=0)
        self.background_canvas.pack(fill="both", expand=True)
        self.add_gradient(self.background_canvas, "#A3BFFA", "#F3F4F6", 500, 300)

        # Title
        self.title_text = tk.Label(self.background_canvas, text="Multi-Instance Deadlock Detection",
                                   font=("Helvetica", 20, "bold"), bg="#A3BFFA", fg="#2E3A59")
        self.title_text.place(relx=0.5, rely=0.15, anchor="center")
        self.fade_in_title(0)

        # Initial input frame
        self.input_frame = tk.Frame(self.background_canvas, bg="#A3BFFA")
        self.input_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.input_frame, text="Processes:", font=("Arial", 12), bg="#A3BFFA").pack(side=tk.LEFT, padx=10, pady=5)
        self.entry_processes = tk.Entry(self.input_frame, width=5)
        self.entry_processes.pack(side=tk.LEFT, padx=5)

        tk.Label(self.input_frame, text="Resources:", font=("Arial", 12), bg="#A3BFFA").pack(side=tk.LEFT, padx=10, pady=5)
        self.entry_resources = tk.Entry(self.input_frame, width=5)
        self.entry_resources.pack(side=tk.LEFT, padx=5)

        self.create_button = tk.Button(self.input_frame, text="Create Input Fields", font=("Arial", 12),
                                       command=self.open_input_window, bg="#4CAF50", fg="white")
        self.create_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.create_button.bind("<Enter>", lambda e: self.create_button.config(bg="#45A049"))
        self.create_button.bind("<Leave>", lambda e: self.create_button.config(bg="#4CAF50"))

        self.allocation = {}
        self.max_matrix = {}
        self.available = {}
        self.total_resources = {}
        self.tooltips = []
        self.last_detector = None  # Store the last detector for visualization

        # Bind window resize
        self.window.bind("<Configure>", self.on_window_resize)

    def on_window_resize(self, event):
        """Handles window resizing by updating the canvas."""
        new_width = self.window.winfo_width()
        new_height = self.window.winfo_height()
        self.background_canvas.config(width=new_width, height=new_height)
        self.background_canvas.delete("all")
        self.add_gradient(self.background_canvas, "#A3BFFA", "#F3F4F6", new_width, new_height)
        self.title_text.place(relx=0.5, rely=0.15, anchor="center")
        self.input_frame.place(relx=0.5, rely=0.5, anchor="center")

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

    def open_input_window(self):
        """Opens a new window for input fields."""
        try:
            self.num_processes = int(self.entry_processes.get())
            self.num_resources = int(self.entry_resources.get())
            if self.num_processes <= 0 or self.num_resources <= 0:
                raise ValueError("Please enter positive numbers.")
            if self.num_processes > 10 or self.num_resources > 10:
                raise ValueError("Maximum 10 processes and resources allowed.")
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self.window)
            return

        # Create a new window
        self.input_window = tk.Toplevel(self.window)
        self.input_window.title("Multi-Instance Deadlock Detection - Input")
        self.input_window.geometry("1000x700")
        self.input_window.minsize(800, 600)
        self.input_window.grab_set()

        # Background canvas with gradient
        self.input_canvas = tk.Canvas(self.input_window, highlightthickness=0)
        self.input_canvas.pack(fill="both", expand=True)
        self.add_gradient(self.input_canvas, "#A3BFFA", "#F3F4F6", 1000, 700)

        # Title
        self.input_title = tk.Label(self.input_canvas, text="Multi-Instance Deadlock Detection",
                                    font=("Helvetica", 20, "bold"), bg="#A3BFFA", fg="#2E3A59")
        self.input_title.place(relx=0.5, rely=0.05, anchor="center")
        self.fade_in_title(0)

        # Main frame with scrollable canvas
        self.main_frame = tk.Frame(self.input_canvas, bg="#F3F4F6")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.75)

        self.canvas = tk.Canvas(self.main_frame, bg="#F3F4F6", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#F3F4F6")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Total resources input
        self.total_frame = tk.Frame(self.scrollable_frame, bg="#E6F0FA", bd=2, relief="groove")
        self.total_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(self.total_frame, text="Total Resources", font=("Helvetica", 14, "bold"), bg="#E6F0FA", fg="#2E3A59").grid(row=0, column=0, columnspan=self.num_resources*2, pady=5)
        self.total_entries = {}
        for j in range(self.num_resources):
            r = f"R{j+1}"
            tk.Label(self.total_frame, text=f"{r}:", font=("Arial", 12), bg="#E6F0FA").grid(row=1, column=j*2, padx=10, pady=5)
            entry = tk.Entry(self.total_frame, width=5)
            entry.grid(row=1, column=j*2+1, padx=10, pady=5)
            entry.bind("<Enter>", lambda e, t=f"Enter total instances for {r}": self.show_tooltip(e, t))
            entry.bind("<Leave>", self.hide_tooltip)
            entry.bind("<KeyRelease>", lambda e: self.validate_entry(e.widget))
            self.total_entries[r] = entry

        # Allocation table
        self.alloc_frame = tk.Frame(self.scrollable_frame, bg="#C8E6C9", bd=2, relief="groove")
        self.alloc_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(self.alloc_frame, text="Allocation", font=("Helvetica", 14, "bold"), bg="#C8E6C9", fg="#2E3A59").grid(row=0, column=0, columnspan=self.num_resources+1, pady=5)
        self.alloc_entries = {}
        for j in range(self.num_resources):
            r = f"R{j+1}"
            tk.Label(self.alloc_frame, text=f"{r}", font=("Arial", 12), bg="#C8E6C9").grid(row=1, column=j+1, padx=10, pady=5)
        for i in range(self.num_processes):
            p = f"P{i+1}"
            tk.Label(self.alloc_frame, text=f"{p}", font=("Arial", 12), bg="#C8E6C9").grid(row=i+2, column=0, padx=10, pady=5)
            self.alloc_entries[p] = {}
            for j in range(self.num_resources):
                r = f"R{j+1}"
                entry = tk.Entry(self.alloc_frame, width=5)
                entry.grid(row=i+2, column=j+1, padx=10, pady=5)
                entry.insert(0, "0")
                entry.bind("<Enter>", lambda e, t=f"Enter allocated instances of {r} for {p}": self.show_tooltip(e, t))
                entry.bind("<Leave>", self.hide_tooltip)
                entry.bind("<KeyRelease>", lambda e: self.validate_entry(e.widget))
                self.alloc_entries[p][r] = entry

        # Max table
        self.max_frame = tk.Frame(self.scrollable_frame, bg="#BBDEFB", bd=2, relief="groove")
        self.max_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(self.max_frame, text="Max", font=("Helvetica", 14, "bold"), bg="#BBDEFB", fg="#2E3A59").grid(row=0, column=0, columnspan=self.num_resources+1, pady=5)
        self.max_entries = {}
        for j in range(self.num_resources):
            r = f"R{j+1}"
            tk.Label(self.max_frame, text=f"{r}", font=("Arial", 12), bg="#BBDEFB").grid(row=1, column=j+1, padx=10, pady=5)
        for i in range(self.num_processes):
            p = f"P{i+1}"
            tk.Label(self.max_frame, text=f"{p}", font=("Arial", 12), bg="#BBDEFB").grid(row=i+2, column=0, padx=10, pady=5)
            self.max_entries[p] = {}
            for j in range(self.num_resources):
                r = f"R{j+1}"
                entry = tk.Entry(self.max_frame, width=5)
                entry.grid(row=i+2, column=j+1, padx=10, pady=5)
                entry.insert(0, "0")
                entry.bind("<Enter>", lambda e, t=f"Enter maximum instances of {r} for {p}": self.show_tooltip(e, t))
                entry.bind("<Leave>", self.hide_tooltip)
                entry.bind("<KeyRelease>", lambda e: self.validate_entry(e.widget))
                self.max_entries[p][r] = entry

        # Unified table (initially hidden)
        self.unified_frame = tk.Frame(self.scrollable_frame, bg="#F3F4F6", bd=2, relief="groove")
        self.unified_labels = {}

        # Buttons
        self.button_frame = tk.Frame(self.input_canvas, bg="#F3F4F6")
        self.button_frame.place(relx=0.5, rely=0.95, anchor="center")

        self.complete_button = tk.Button(self.button_frame, text="📋 Complete Table", font=("Arial", 12, "bold"),
                                         command=self.complete_table, bg="#2196F3", fg="white", padx=15, pady=5)
        self.complete_button.pack(side=tk.LEFT, padx=10)
        self.complete_button.bind("<Enter>", lambda e: self.complete_button.config(bg="#1976D2"))
        self.complete_button.bind("<Leave>", lambda e: self.complete_button.config(bg="#2196F3"))

        self.detect_button = tk.Button(self.button_frame, text="🔍 Detect Deadlock", font=("Arial", 12, "bold"),
                                       command=self.detect_deadlock, bg="#D32F2F", fg="white", padx=15, pady=5)
        self.detect_button.pack(side=tk.LEFT, padx=10)
        self.detect_button.bind("<Enter>", lambda e: self.detect_button.config(bg="#B71C1C"))
        self.detect_button.bind("<Leave>", lambda e: self.detect_button.config(bg="#D32F2F"))

        self.visualize_button = tk.Button(self.button_frame, text="📊 Visualize RAG", font=("Arial", 12, "bold"),
                                          command=self.visualize_rag, bg="#4CAF50", fg="white", padx=15, pady=5)
        self.visualize_button.pack(side=tk.LEFT, padx=10)
        self.visualize_button.bind("<Enter>", lambda e: self.visualize_button.config(bg="#388E3C"))
        self.visualize_button.bind("<Leave>", lambda e: self.visualize_button.config(bg="#4CAF50"))

        self.reset_button = tk.Button(self.button_frame, text="🔄 Reset", font=("Arial", 12, "bold"),
                                      command=self.reset, bg="#FF9800", fg="white", padx=15, pady=5)
        self.reset_button.pack(side=tk.LEFT, padx=10)
        self.reset_button.bind("<Enter>", lambda e: self.reset_button.config(bg="#F57C00"))
        self.reset_button.bind("<Leave>", lambda e: self.reset_button.config(bg="#FF9800"))

        # Bind resize for the new window
        self.input_window.bind("<Configure>", self.on_input_window_resize)

    def on_input_window_resize(self, event):
        """Handles resizing of the input window."""
        new_width = self.input_window.winfo_width()
        new_height = self.input_window.winfo_height()
        self.input_canvas.config(width=new_width, height=new_height)
        self.input_canvas.delete("all")
        self.add_gradient(self.input_canvas, "#A3BFFA", "#F3F4F6", new_width, new_height)
        self.input_title.place(relx=0.5, rely=0.05, anchor="center")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.75)
        self.button_frame.place(relx=0.5, rely=0.95, anchor="center")

    def show_tooltip(self, event, text):
        """Shows a tooltip with the given text."""
        x = event.widget.winfo_rootx() + 20
        y = event.widget.winfo_rooty() + 20
        self.tooltip = tk.Toplevel(event.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
        label.pack()
        self.tooltips.append(self.tooltip)

    def hide_tooltip(self, event):
        """Hides the tooltip."""
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()
            del self.tooltip
        for tooltip in self.tooltips:
            tooltip.destroy()
        self.tooltips.clear()

    def validate_entry(self, entry):
        """Validates the entry to ensure it's a non-negative integer."""
        value = entry.get()
        try:
            if value == "":
                entry.config(bg="white")
                return
            val = int(value)
            if val < 0:
                entry.config(bg="#FFCDD2")
            else:
                entry.config(bg="white")
        except ValueError:
            entry.config(bg="#FFCDD2")

    def complete_table(self):
        """Computes the Need matrix and Available resources, then displays a unified table."""
        try:
            self._collect_data()
            detector = MultiInstanceDeadlockDetector(self.allocation, self.max_matrix, self.available, self.total_resources)
            need = detector.get_need()

            # Hide input sections
            self.total_frame.pack_forget()
            self.alloc_frame.pack_forget()
            self.max_frame.pack_forget()

            # Create unified table
            tk.Label(self.unified_frame, text="Unified Resource Table", font=("Helvetica", 14, "bold"), bg="#F3F4F6", fg="#2E3A59").grid(row=0, column=0, columnspan=(self.num_resources*4)+1, pady=5)

            # Headers
            tk.Label(self.unified_frame, text="", font=("Arial", 12), bg="#F3F4F6").grid(row=1, column=0, padx=10, pady=5)
            # Allocation headers
            tk.Label(self.unified_frame, text="Allocation", font=("Helvetica", 12, "bold"), bg="#C8E6C9").grid(row=1, column=1, columnspan=self.num_resources, padx=10, pady=5)
            for j in range(self.num_resources):
                r = f"R{j+1}"
                tk.Label(self.unified_frame, text=f"{r}", font=("Arial", 12), bg="#C8E6C9").grid(row=2, column=j+1, padx=10, pady=5)
            # Separator after Allocation
            tk.Label(self.unified_frame, text="", font=("Arial", 12), bg="#000000", width=1).grid(row=1, column=self.num_resources+1, rowspan=self.num_processes+3, sticky="ns")
            # Max headers
            tk.Label(self.unified_frame, text="Max", font=("Helvetica", 12, "bold"), bg="#BBDEFB").grid(row=1, column=self.num_resources+2, columnspan=self.num_resources, padx=10, pady=5)
            for j in range(self.num_resources):
                r = f"R{j+1}"
                tk.Label(self.unified_frame, text=f"{r}", font=("Arial", 12), bg="#BBDEFB").grid(row=2, column=j+self.num_resources+2, padx=10, pady=5)
            # Separator after Max
            tk.Label(self.unified_frame, text="", font=("Arial", 12), bg="#000000", width=1).grid(row=1, column=(self.num_resources*2)+2, rowspan=self.num_processes+3, sticky="ns")
            # Need headers
            tk.Label(self.unified_frame, text="Need", font=("Helvetica", 12, "bold"), bg="#FFECB3").grid(row=1, column=(self.num_resources*2)+3, columnspan=self.num_resources, padx=10, pady=5)
            for j in range(self.num_resources):
                r = f"R{j+1}"
                tk.Label(self.unified_frame, text=f"{r}", font=("Arial", 12), bg="#FFECB3").grid(row=2, column=j+(self.num_resources*2)+3, padx=10, pady=5)
            # Separator after Need
            tk.Label(self.unified_frame, text="", font=("Arial", 12), bg="#000000", width=1).grid(row=1, column=(self.num_resources*3)+3, rowspan=self.num_processes+3, sticky="ns")
            # Available headers with values
            tk.Label(self.unified_frame, text="Available", font=("Helvetica", 12, "bold"), bg="#D1C4E9").grid(row=1, column=(self.num_resources*3)+4, columnspan=self.num_resources, padx=10, pady=5)
            for j in range(self.num_resources):
                r = f"R{j+1}"
                tk.Label(self.unified_frame, text=f"{r}", font=("Arial", 12), bg="#D1C4E9").grid(row=2, column=j+(self.num_resources*3)+4, padx=10, pady=5)
                label_avail = tk.Label(self.unified_frame, text=str(self.available[r]), font=("Arial", 12), bg="#D1C4E9", width=5, relief="sunken")
                label_avail.grid(row=3, column=j+(self.num_resources*3)+4, padx=10, pady=5)

            # Process rows
            self.unified_labels = {}
            for i in range(self.num_processes):
                p = f"P{i+1}"
                tk.Label(self.unified_frame, text=f"{p}", font=("Arial", 12), bg="#F3F4F6").grid(row=i+3, column=0, padx=10, pady=5)
                self.unified_labels[p] = {}
                for j in range(self.num_resources):
                    r = f"R{j+1}"
                    # Allocation
                    label_alloc = tk.Label(self.unified_frame, text=str(self.allocation[p][r]), font=("Arial", 12), bg="#C8E6C9", width=5, relief="sunken")
                    label_alloc.grid(row=i+3, column=j+1, padx=10, pady=5)
                    self.unified_labels[p][f"alloc_{r}"] = label_alloc
                    # Max
                    label_max = tk.Label(self.unified_frame, text=str(self.max_matrix[p][r]), font=("Arial", 12), bg="#BBDEFB", width=5, relief="sunken")
                    label_max.grid(row=i+3, column=j+self.num_resources+2, padx=10, pady=5)
                    self.unified_labels[p][f"max_{r}"] = label_max
                    # Need
                    label_need = tk.Label(self.unified_frame, text=str(need[p][r]), font=("Arial", 12), bg="#FFECB3", width=5, relief="sunken")
                    label_need.grid(row=i+3, column=j+(self.num_resources*2)+3, padx=10, pady=5)
                    self.unified_labels[p][f"need_{r}"] = label_need

            # Show unified table
            self.unified_frame.pack(fill=tk.X, padx=10, pady=10)

        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self.input_window)

    def detect_deadlock(self):
        """Detects deadlock or unsafe state and displays the result."""
        try:
            self._collect_data()
            start_time = time.time()
            detector = MultiInstanceDeadlockDetector(self.allocation, self.max_matrix, self.available, self.total_resources)
            has_deadlock, message = detector.detect_deadlock()
            elapsed_time = time.time() - start_time
            message += f"\nDetection took {elapsed_time:.3f} seconds."
            self.last_detector = detector  # Store the detector for visualization
            if has_deadlock:
                self.sound_manager.play_deadlock_sound()
                messagebox.showwarning("Unsafe State Detected", message, parent=self.input_window)
            else:
                self.sound_manager.play_safe_sound()  # Play sound for safe state
                messagebox.showinfo("Safe State", message, parent=self.input_window)
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self.input_window)

    def visualize_rag(self):
        """Visualizes the RAG for a multi-instance system."""
        try:
            self._collect_data()
            if self.last_detector is None:
                detector = MultiInstanceDeadlockDetector(self.allocation, self.max_matrix, self.available, self.total_resources)
                has_deadlock, _ = detector.detect_deadlock()
                self.last_detector = detector
            else:
                detector = self.last_detector

            rag = self._build_rag(detector.get_need())
            flat_allocation = self._flatten_allocation()
            need = detector.get_need()
            safe_sequence = detector.safe_sequence if not detector.has_deadlock else []
            visualize_multi_rag(rag, flat_allocation, need, safe_sequence)
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self.input_window)

    def reset(self):
        """Resets all input fields."""
        for r in self.total_entries:
            self.total_entries[r].delete(0, tk.END)
            self.total_entries[r].config(bg="white")
        for p in self.alloc_entries:
            for r in self.alloc_entries[p]:
                self.alloc_entries[p][r].delete(0, tk.END)
                self.alloc_entries[p][r].insert(0, "0")
                self.alloc_entries[p][r].config(bg="white")
        for p in self.max_entries:
            for r in self.max_entries[p]:
                self.max_entries[p][r].delete(0, tk.END)
                self.max_entries[p][r].insert(0, "0")
                self.max_entries[p][r].config(bg="white")
        self.unified_frame.pack_forget()
        self.total_frame.pack(fill=tk.X, padx=10, pady=10)
        self.alloc_frame.pack(fill=tk.X, padx=10, pady=10)
        self.max_frame.pack(fill=tk.X, padx=10, pady=10)
        self.allocation.clear()
        self.max_matrix.clear()
        self.available.clear()
        self.total_resources.clear()
        self.last_detector = None

    def _collect_data(self):
        """Collects data from input fields, treating empty fields as 0."""
        self.total_resources = {}
        for r in self.total_entries:
            value = self.total_entries[r].get()
            self.total_resources[r] = int(value) if value.strip() else 0

        self.allocation = {}
        for p in self.alloc_entries:
            self.allocation[p] = {}
            for r in self.alloc_entries[p]:
                value = self.alloc_entries[p][r].get()
                self.allocation[p][r] = int(value) if value.strip() else 0

        self.max_matrix = {}
        for p in self.max_entries:
            self.max_matrix[p] = {}
            for r in self.max_entries[p]:
                value = self.max_entries[p][r].get()
                self.max_matrix[p][r] = int(value) if value.strip() else 0

        total_allocated = {r: sum(self.allocation[p].get(r, 0) for p in self.allocation) 
                          for r in self.total_resources}
        self.available = {r: self.total_resources[r] - total_allocated[r] for r in self.total_resources}

    def _build_rag(self, need):
        """Builds the RAG for visualization (multi-instance)."""
        rag = {}
        processes = list(self.allocation.keys())
        resources = list(self.total_resources.keys())

        # Initialize nodes
        for p in processes:
            rag[p] = []
        for r in resources:
            rag[r] = []

        # Add request edges (Process -> Resource) based on Need
        for p in processes:
            for r in resources:
                if need[p][r] > 0:  # Process needs this resource
                    rag[p].append(r)

        # Add allocation edges (Resource -> Process) based on Allocation
        for p in processes:
            for r in resources:
                if self.allocation[p][r] > 0:  # Resource is allocated to this process
                    rag[r].append(p)

        return rag

    def _flatten_allocation(self):
        """Flattens multi-instance allocation to a list of resources for visualization."""
        flat_allocation = {}
        for p in self.allocation:
            flat_allocation[p] = []
            for r in self.allocation[p]:
                # Add the resource to the list as many times as the number of instances allocated
                instances = self.allocation[p][r]
                flat_allocation[p].extend([r] * instances)
        return flat_allocation