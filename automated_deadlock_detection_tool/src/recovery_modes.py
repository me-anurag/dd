import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import copy
import logging
from multi_deadlock_algo import MultiInstanceDeadlockDetector
from multi_visualization import visualize_multi_rag

class RecoveryModes:
    """Handles recovery modes for deadlock situations.

    Args:
        window (tk.Tk): The Tkinter window for the recovery modes.
        sound_manager (SoundManager): The sound manager for playing audio feedback.
        detector (MultiInstanceDeadlockDetector): The deadlock detector instance.
        allocation (dict): Allocation matrix.
        max_matrix (dict): Maximum resource requirement matrix.
        available (dict): Available resources.
        total_resources (dict): Total resources in the system.
    """
    def __init__(self, window, sound_manager, detector, allocation, max_matrix, available, total_resources):
        self.window = window
        self.sound_manager = sound_manager
        self.detector = detector
        self.allocation = copy.deepcopy(allocation)
        self.max_matrix = copy.deepcopy(max_matrix)
        self.available = copy.deepcopy(available)
        self.total_resources = copy.deepcopy(total_resources)
        self.processes = list(allocation.keys())
        self.resources = list(total_resources.keys())

        self.window.title("Deadlock Recovery Modes")
        self.window.geometry("600x400")
        self.window.minsize(500, 300)
        self.window.grab_set()

        # Background canvas with gradient
        self.canvas = tk.Canvas(self.window, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.add_gradient(self.canvas, "#A3BFFA", "#F3F4F6", 600, 400)

        # Title
        self.title_label = tk.Label(self.canvas, text="Deadlock Recovery Options",
                                    font=("Helvetica", 20, "bold"), bg="#A3BFFA", fg="#2E3A59")
        self.title_label.place(relx=0.5, rely=0.1, anchor="center")

        # Buttons for recovery modes
        self.button_frame = tk.Frame(self.canvas, bg="#F3F4F6")
        self.button_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.narrative_button = tk.Button(self.button_frame, text="📖 Narrative", font=("Arial", 12, "bold"),
                                         command=self.narrative_mode, bg="#2196F3", fg="white", padx=15, pady=10)
        self.narrative_button.pack(pady=10)
        self.narrative_button.bind("<Enter>", lambda e: self.narrative_button.config(bg="#1976D2"))
        self.narrative_button.bind("<Leave>", lambda e: self.narrative_button.config(bg="#2196F3"))

        self.preemption_button = tk.Button(self.button_frame, text="🔄 Resource Preemption", font=("Arial", 12, "bold"),
                                           command=self.resource_preemption_mode, bg="#FF5722", fg="white", padx=15, pady=10)
        self.preemption_button.pack(pady=10)
        self.preemption_button.bind("<Enter>", lambda e: self.preemption_button.config(bg="#E64A19"))
        self.preemption_button.bind("<Leave>", lambda e: self.preemption_button.config(bg="#FF5722"))

        self.termination_button = tk.Button(self.button_frame, text="🛑 Process Termination", font=("Arial", 12, "bold"),
                                            command=self.process_termination_mode, bg="#D32F2F", fg="white", padx=15, pady=10)
        self.termination_button.pack(pady=10)
        self.termination_button.bind("<Enter>", lambda e: self.termination_button.config(bg="#B71C1C"))
        self.termination_button.bind("<Leave>", lambda e: self.termination_button.config(bg="#D32F2F"))

        # Bind window resize
        self.window.bind("<Configure>", self.on_window_resize)

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

    def on_window_resize(self, event):
        """Handles window resizing by updating the canvas."""
        new_width = self.window.winfo_width()
        new_height = self.window.winfo_height()
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.delete("all")
        self.add_gradient(self.canvas, "#A3BFFA", "#F3F4F6", new_width, new_height)
        self.title_label.place(relx=0.5, rely=0.1, anchor="center")
        self.button_frame.place(relx=0.5, rely=0.5, anchor="center")

    def narrative_mode(self):
        """Narrates the Banker's Algorithm steps with vivid, voiceover-style commentary."""
        if not self.detector.has_deadlock and not self.detector.safe_sequence:
            self.detector.detect_deadlock()  # Ensure detector has run

        narrative_window = tk.Toplevel(self.window)
        narrative_window.title("Detective's Log: Deadlock Investigation")
        narrative_window.geometry("800x600")
        narrative_window.grab_set()

        text_area = tk.Text(narrative_window, wrap=tk.WORD, font=("Arial", 12), height=20)
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(narrative_window, command=text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.config(yscrollcommand=scrollbar.set)

        def append_text(message, sound_action="check", callback=None):
            """Appends text to the text area, plays the specified sound, and schedules the next step."""
            text_area.insert(tk.END, message + "\n\n")
            text_area.see(tk.END)
            if self.sound_manager.sound_enabled:
                try:
                    if sound_action == "start":
                        self.sound_manager.play_sound_with_fadeout("radar", 1500)
                        logging.info("Playing start detection sound: radar_ping.wav with 1.5s fadeout")
                    elif sound_action == "check":
                        self.sound_manager.play_sound_with_fadeout("click", 1500)
                        logging.info("Playing process check sound: click.wav")
                    elif sound_action == "pop":
                        self.sound_manager.play_sound_with_fadeout("pop", 1500)
                        logging.info("Playing input display sound: pop.wav")
                    elif sound_action == "allocate":
                        self.sound_manager.play_sound_with_fadeout("chime", 1500)
                        logging.info("Playing resource allocation sound: chime.wav")
                    elif sound_action == "wait":
                        self.sound_manager.play_sound_with_fadeout("suspense", 1500)
                        logging.info("Playing wait detected sound: suspense_hum.wav")
                    elif sound_action == "deadlock":
                        self.sound_manager.play_sound_with_fadeout("deadlock", 1500)
                        logging.info("Playing deadlock detected sound: deadlock_alarm.wav")
                    elif sound_action == "safe":
                        self.sound_manager.play_sound_with_fadeout("safe", 1500)
                        logging.info("Playing safe state sound: safe_chime.wav")
                    elif sound_action == "retry":
                        self.sound_manager.play_sound_with_fadeout("rewind", 1500)
                        logging.info("Playing retry/backtrack sound: rewind_whoosh.wav")
                except Exception as e:
                    logging.error(f"Error playing sound {sound_action}: {e}")
            narrative_window.update()
            if callback:
                narrative_window.after(1500, callback)  # Schedule next step after 1.5 seconds

        def step_intro():
            """Step 1: Introduction to the investigation."""
            append_text(
                "📡 *Bzzzt!* This is the Deadlock Detective Agency, on the case of a resource allocation mystery! I’m your lead detective, ready to crack open this system’s secrets. Are the processes playing nice, or are we staring down a deadlock? Let’s dive in!",
                sound_action="start",
                callback=step_display_data
            )

        def step_display_data():
            """Step 2: Display input data (total and available resources, process allocations, max demands)."""
            append_text(
                "🗳️ First, let’s check the evidence locker. Here’s the system’s resource inventory:",
                sound_action="check",
                callback=lambda: display_total_resources()
            )

        def display_total_resources():
            total_res = ", ".join([f"{r}: {self.total_resources[r]}" for r in self.resources])
            append_text(
                f"Total Resources: {total_res}",
                sound_action="pop",
                callback=lambda: display_available_resources()
            )

        def display_available_resources():
            avail_res = ", ".join([f"{r}: {self.available[r]}" for r in self.resources])
            append_text(
                f"Available Resources (ready for allocation): {avail_res}",
                sound_action="pop",
                callback=lambda: display_process_data()
            )

        def display_process_data():
            append_text(
                "🕵️‍♂️ Now, let’s grill our suspects—the processes. What resources are they holding, and what are they after?",
                sound_action="check",
                callback=lambda: display_process(0)
            )

        def display_process(index):
            if index < len(self.processes):
                p = self.processes[index]
                alloc = ", ".join([f"{r}: {self.allocation[p][r]}" for r in self.resources])
                max_m = ", ".join([f"{r}: {self.max_matrix[p][r]}" for r in self.resources])
                append_text(
                    f"Process {p}: Holding [{alloc}], Demanding up to [{max_m}]",
                    sound_action="check",
                    callback=lambda: display_process(index + 1)
                )
            else:
                step_compute_need()

        def step_compute_need():
            """Step 3: Compute and display the Need matrix."""
            append_text(
                "📊 Time to do some detective math. We need to figure out what each process still craves. Need = Max - Allocation. Let’s crunch the numbers!",
                sound_action="check",
                callback=lambda: compute_need(0)
            )

        def compute_need(index):
            need = self.detector.get_need()
            if index < len(self.processes):
                p = self.processes[index]
                need_str = []
                for r in self.resources:
                    max_val = self.max_matrix[p][r]
                    alloc_val = self.allocation[p][r]
                    need_val = max_val - alloc_val
                    need_str.append(f"{r}: {need_val} ({max_val} - {alloc_val})")
                append_text(
                    f"Process {p} needs: [{', '.join(need_str)}]",
                    sound_action="check",
                    callback=lambda: compute_need(index + 1)
                )
            else:
                step_bankers_algorithm()

        def step_bankers_algorithm():
            """Step 4: Run the Banker's Algorithm with detailed narration."""
            append_text(
                "🕵️‍♂️ Now, the main event! We’re deploying the Banker’s Algorithm to find a safe path through this resource jungle. Deadlocks are like a standoff where everyone’s waiting for someone else. This algorithm checks if we can satisfy all processes safely, avoiding a resource trap!",
                sound_action="check",
                callback=lambda: run_bankers(0, self.available.copy(), {p: False for p in self.processes}, [], self.processes.copy())
            )

        def run_bankers(step, work, finish, safe_sequence, remaining_processes):
            """Step 5: Iterate through the Banker's Algorithm steps."""
            if not remaining_processes:
                step_conclusion(finish, safe_sequence)
                return

            append_text(
                f"🔎 Step {step + 1}: Scanning for a process that can run with our current Work Pool: [{', '.join([f'{r}: {work[r]}' for r in self.resources])}]",
                sound_action="check",
                callback=lambda: check_process(0, step, work, finish, safe_sequence, remaining_processes.copy())
            )

        def check_process(proc_index, step, work, finish, safe_sequence, remaining_processes):
            need = self.detector.get_need()
            if proc_index >= len(remaining_processes):
                if not any(not finish[p] for p in remaining_processes):
                    step_conclusion(finish, safe_sequence)
                else:
                    append_text(
                        "🔁 Dead end! No process can proceed with the current Work Pool. Time to backtrack and reassess!",
                        sound_action="retry",
                        callback=lambda: step_conclusion(finish, safe_sequence)
                    )
                return

            p = remaining_processes[proc_index]
            if finish[p]:
                check_process(proc_index + 1, step, work, finish, safe_sequence, remaining_processes)
                return

            append_text(
                f"🔎 Checking Process {p}... Can it get the resources it needs to finish?",
                sound_action="check",
                callback=lambda: evaluate_process(p, proc_index, step, work, finish, safe_sequence, remaining_processes)
            )

        def evaluate_process(p, proc_index, step, work, finish, safe_sequence, remaining_processes):
            need = self.detector.get_need()
            can_run = True
            comparisons = []
            for r in self.resources:
                if need[p][r] > work[r]:
                    can_run = False
                    comparisons.append(f"{r}: Needs {need[p][r]} but only {work[r]} available (Not enough!)")
                else:
                    comparisons.append(f"{r}: Needs {need[p][r]} ≤ {work[r]} (We’ve got this!)")
            append_text(
                f"Clues for {p}: [{', '.join(comparisons)}]",
                sound_action="wait" if not can_run else "check",
                callback=lambda: process_result(p, can_run, proc_index, step, work, finish, safe_sequence, remaining_processes)
            )

        def process_result(p, can_run, proc_index, step, work, finish, safe_sequence, remaining_processes):
            if can_run and not finish[p]:
                append_text(
                    f"🔔 Success! Process {p} can run with Needs [{', '.join([f'{r}: {need[p][r]}' for r in self.resources])}]. It’s cleared to finish!",
                    sound_action="allocate",
                    callback=lambda: release_resources(p, proc_index, step, work, finish, safe_sequence, remaining_processes)
                )
            else:
                append_text(
                    f"⚠️ Hold up! Process {p} is stuck waiting for more resources. Moving to the next suspect...",
                    sound_action="wait",
                    callback=lambda: check_process(proc_index + 1, step, work, finish, safe_sequence, remaining_processes)
                )

        def release_resources(p, proc_index, step, work, finish, safe_sequence, remaining_processes):
            for r in self.resources:
                work[r] += self.allocation[p].get(r, 0)
            finish[p] = True
            safe_sequence.append(p)
            remaining_processes.remove(p)
            # Optional: Visualize updated RAG (uncomment to enable)
            # rag = self._build_rag(self.detector.get_need())
            # flat_allocation = self._flatten_allocation(self.allocation)
            # visualize_multi_rag(rag, flat_allocation, self.detector.get_need(), safe_sequence)
            # append_text("📊 Updated the Resource Allocation Graph to show our progress!", sound_action="check")
            append_text(
                f"Process {p} completes and returns its resources. New Work Pool: [{', '.join([f'{r}: {work[r]}' for r in self.resources])}]",
                sound_action="allocate",
                callback=lambda: run_bankers(step + 1, work, finish, safe_sequence, remaining_processes)
            )

        def step_conclusion(finish, safe_sequence):
            """Step 6: Conclude the investigation based on results."""
            if len(safe_sequence) == len(self.processes):
                append_text(
                    f"🌤️ Case solved! We found a safe sequence: {safe_sequence}! Every process can finish without a hitch. Great work, detectives!",
                    sound_action="safe",
                    callback=step_outro
                )
            else:
                unfinished = [p for p in self.processes if not finish[p]]
                append_text(
                    f"🚨 Emergency! We’ve hit a deadlock—or at least an unsafe state. Processes {unfinished} are stuck in a resource tangle!",
                    sound_action="deadlock",
                    callback=step_outro
                )

        def step_outro():
            """Step 7: Outro with appropriate sound based on outcome."""
            if len(self.detector.safe_sequence) == len(self.processes):
                append_text(
                    "🎬 Case closed! We navigated the resource maze and emerged victorious. Until the next mystery, stay sharp, detectives!",
                    sound_action="safe",
                    callback=finalize
                )
            else:
                append_text(
                    "🎬 Case closed, but the mystery persists. A deadlock looms—time to call in the heavy artillery for preemption or termination. Stay vigilant, detectives!",
                    sound_action="deadlock",
                    callback=finalize
                )

        def finalize():
            """Finalize the narration by disabling the text area."""
            text_area.config(state=tk.DISABLED)

        try:
            # Start the narration sequence
            step_intro()
        except Exception as e:
            logging.error(f"Error in narrative mode: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}", parent=narrative_window)
            text_area.config(state=tk.DISABLED)

    def resource_preemption_mode(self):
        """Simulates resource preemption with detailed, detective-themed narration."""
        if not self.detector.has_deadlock:
            messagebox.showinfo("No Deadlock", "The system is already in a safe state!", parent=self.window)
            return

        preemption_window = tk.Toplevel(self.window)
        preemption_window.title("Deadlock Detective: Resource Preemption")
        preemption_window.geometry("800x600")
        preemption_window.grab_set()

        text_area = tk.Text(preemption_window, wrap=tk.WORD, font=("Arial", 12), height=20)
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(preemption_window, command=text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.config(yscrollcommand=scrollbar.set)

        def append_text(message, sound_action="check", callback=None):
            """Appends text to the text area, plays the specified sound, and schedules the next step."""
            text_area.insert(tk.END, message + "\n\n")
            text_area.see(tk.END)
            if self.sound_manager.sound_enabled:
                try:
                    self.sound_manager.play_sound_with_fadeout(sound_action, 1500)
                    logging.info(f"Playing {sound_action} sound: {sound_action}.wav")
                except Exception as e:
                    logging.error(f"Error playing sound {sound_action}: {e}")
            preemption_window.update()
            if callback:
                preemption_window.after(1500, callback)

        def step_intro():
            """Step 1: Introduction to preemption."""
            append_text(
                "📡 *Bzzzt!* Deadlock Detective Agency, back on the case! The system’s tangled in a deadlock, and we’re gonna bust it open by preempting resources. We’ll snatch resources from processes to free up the grid—let’s get to work!",
                sound_action="radar",
                callback=step_analyze
            )

        def step_analyze():
            """Step 2: Start the preemption process."""
            append_text(
                "🔎 The mission: break the deadlock by reallocating resources. We’ll identify resource hogs and redirect their assets to clear the path. Let’s scan the system!",
                sound_action="check",
                callback=lambda: process_step(1, copy.deepcopy(self.allocation), copy.deepcopy(self.available), [], self.detector.get_need())
            )

        def select_victim(unfinished, need, available):
            """Selects the process to preempt based on resource criticality."""
            if not unfinished:
                return None
            # Score processes based on how many scarce resources they hold
            scores = {}
            for p in unfinished:
                score = 0
                for r in self.resources:
                    if need[p][r] > 0 and available[r] < need[p][r]:
                        score += self.allocation[p][r] * (need[p][r] - available[r])
                scores[p] = score if score > 0 else sum(self.allocation[p][r] for r in self.resources)
            return max(scores, key=scores.get) if scores else None

        def process_step(step, allocation, available, preempted_processes, need):
            """Step 3: Process each preemption step."""
            append_text(
                f"🕵️‍♂️ Step {step}: Scanning the resource grid for our next target...",
                sound_action="check",
                callback=lambda: check_system(step, allocation, available, preempted_processes, need)
            )

        def check_system(step, allocation, available, preempted_processes, need):
            unfinished = [p for p in self.processes if p not in preempted_processes and any(need[p][r] > 0 for r in self.resources)]
            if not unfinished:
                append_text(
                    "🌤️ Breakthrough! All processes can proceed. The system’s safe!",
                    sound_action="safe",
                    callback=step_outro
                )
                return

            victim = select_victim(unfinished, need, available)
            if not victim:
                append_text(
                    "⚠️ No more resource hogs to preempt! We’re out of moves.",
                    sound_action="deadlock",
                    callback=step_outro
                )
                return

            append_text(
                f"👀 Got a suspect! Process {victim} is hogging critical resources. Let’s seize their assets to untangle this mess!",
                sound_action="suspense",
                callback=lambda: display_victim(step, allocation, available, preempted_processes, need, victim)
            )

        def display_victim(step, allocation, available, preempted_processes, need, victim):
            alloc_str = ", ".join([f"{r}: {allocation[victim][r]}" for r in self.resources])
            avail_str = ", ".join([f"{r}: {available[r]}" for r in self.resources])
            append_text(
                f"📋 Evidence on {victim}: Holding [{alloc_str}] | Available Resources: [{avail_str}]",
                sound_action="pop",
                callback=lambda: preempt_resources(step, allocation, available, preempted_processes, need, victim)
            )

        def preempt_resources(step, allocation, available, preempted_processes, need, victim):
            released = {}
            has_resources = False
            for r in self.resources:
                if allocation[victim][r] > 0:
                    released[r] = allocation[victim][r]
                    available[r] += allocation[victim][r]
                    allocation[victim][r] = 0
                    need[victim][r] = self.max_matrix[victim][r]
                    has_resources = True
            if has_resources:
                released_str = ", ".join([f"{r}: {released[r]}" for r in released])
                new_avail_str = ", ".join([f"{r}: {available[r]}" for r in self.resources])
                append_text(
                    f"🔄 Seized resources from {victim}: [{released_str}] | New Available Resources: [{new_avail_str}]",
                    sound_action="rewind",
                    callback=lambda: update_rag(step, allocation, available, preempted_processes, need, victim)
                )
            else:
                append_text(
                    f"⚠️ Process {victim} has no resources to seize! Moving on...",
                    sound_action="wait",
                    callback=lambda: finalize_step(step, allocation, available, preempted_processes + [victim], need)
                )

        def update_rag(step, allocation, available, preempted_processes, need, victim):
            append_text(
                "📊 Updating the Resource Allocation Graph to reflect our progress...",
                sound_action="check",
                callback=lambda: check_safety(step, allocation, available, preempted_processes, need, victim)
            )
            # Optional: Visualize RAG (uncomment to enable)
            # rag = self._build_rag(need)
            # flat_allocation = self._flatten_allocation(allocation)
            # visualize_multi_rag(rag, flat_allocation, need, unfinished_processes=[p for p in self.processes if p not in preempted_processes])

        def check_safety(step, allocation, available, preempted_processes, need, victim):
            detector = MultiInstanceDeadlockDetector(allocation, self.max_matrix, available, self.total_resources)
            has_deadlock, message = detector.detect_deadlock()
            append_text(
                f"🔍 Running the Banker’s Algorithm with Available: [{', '.join([f'{r}: {available[r]}' for r in self.resources])}]",
                sound_action="check",
                callback=lambda: display_safety_result(step, allocation, available, preempted_processes, need, victim, has_deadlock, detector)
            )

        def display_safety_result(step, allocation, available, preempted_processes, need, victim, has_deadlock, detector):
            if not has_deadlock:
                append_text(
                    f"🌟 Case cracked! The system is safe with sequence: {detector.safe_sequence}! Process {victim}’s resources saved the day!",
                    sound_action="safe",
                    callback=step_outro
                )
            else:
                append_text(
                    f"😕 Still tangled: {message}. Process {victim} wasn’t enough. Let’s find another target...",
                    sound_action="wait",
                    callback=lambda: finalize_step(step, allocation, available, preempted_processes + [victim], need)
                )

        def finalize_step(step, allocation, available, preempted_processes, need):
            if step >= len(self.processes):
                append_text(
                    "🚨 Deadlock persists! We’ve run out of processes to preempt. The case remains unsolved!",
                    sound_action="deadlock",
                    callback=step_outro
                )
            else:
                process_step(step + 1, allocation, available, preempted_processes, need)

        def step_outro():
            """Final step: Conclude the preemption process."""
            append_text(
                "🎬 Case closed! Whether we broke the deadlock or not, you’ve seen the art of resource preemption in action. Stay sharp, detectives!",
                sound_action="safe",
                callback=finalize
            )

        def finalize():
            """Disable the text area to end the mode."""
            text_area.config(state=tk.DISABLED)

        try:
            step_intro()
        except Exception as e:
            logging.error(f"Error in resource preemption mode: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}", parent=preemption_window)
            text_area.config(state=tk.DISABLED)

    def process_termination_mode(self):
        """Simulates process termination with detailed, detective-themed narration."""
        if not self.detector.has_deadlock:
            messagebox.showinfo("No Deadlock", "The system is already in a safe state!", parent=self.window)
            return

        termination_window = tk.Toplevel(self.window)
        termination_window.title("Deadlock Detective: Process Termination")
        termination_window.geometry("800x600")
        termination_window.grab_set()

        text_area = tk.Text(termination_window, wrap=tk.WORD, font=("Arial", 12), height=20)
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(termination_window, command=text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.config(yscrollcommand=scrollbar.set)

        def append_text(message, sound_action="check", callback=None):
            """Appends text to the text area, plays the specified sound, and schedules the next step."""
            text_area.insert(tk.END, message + "\n\n")
            text_area.see(tk.END)
            if self.sound_manager.sound_enabled:
                try:
                    self.sound_manager.play_sound_with_fadeout(sound_action, 1500)
                    logging.info(f"Playing {sound_action} sound: {sound_action}.wav")
                except Exception as e:
                    logging.error(f"Error playing sound {sound_action}: {e}")
            termination_window.update()
            if callback:
                termination_window.after(1500, callback)

        def step_intro():
            """Step 1: Introduction to termination."""
            append_text(
                "📡 *Bzzzt!* Deadlock Detective Agency, reporting in! The system’s locked tight in a deadlock. Time to take drastic measures: we’re terminating processes to cut the knot. This is a last resort, so let’s do it clean!",
                sound_action="radar",
                callback=step_analyze
            )

        def step_analyze():
            """Step 2: Start the termination process."""
            append_text(
                "🔎 The plan: eliminate processes holding critical resources to free up the system. Each termination is a tough call, but it’s the only way to break this deadlock. Let’s find our first target!",
                sound_action="check",
                callback=lambda: process_step(1, copy.deepcopy(self.allocation), copy.deepcopy(self.available), self.processes.copy(), self.detector.get_need())
            )

        def select_victim(processes, need, available):
            """Selects the process to terminate based on resource criticality."""
            if not processes:
                return None
            # Score processes based on how many scarce resources they hold
            scores = {}
            for p in processes:
                score = 0
                for r in self.resources:
                    if need[p][r] > 0 and available[r] < need[p][r]:
                        score += self.allocation[p][r] * (need[p][r] - available[r])
                scores[p] = score if score > 0 else sum(self.allocation[p][r] for r in self.resources)
            return max(scores, key=scores.get) if scores else None

        def process_step(step, allocation, available, processes, need):
            """Step 3: Process each termination step."""
            append_text(
                f"🕵️‍♂️ Step {step}: Scouring the system for the process causing the most trouble...",
                sound_action="check",
                callback=lambda: check_system(step, allocation, available, processes, need)
            )

        def check_system(step, allocation, available, processes, need):
            if not processes:
                append_text(
                    "🚨 No processes left to terminate! The deadlock’s too tough to crack.",
                    sound_action="deadlock",
                    callback=step_outro
                )
                return

            victim = select_victim(processes, need, available)
            if not victim:
                append_text(
                    "⚠️ No viable targets left! We’re out of options.",
                    sound_action="deadlock",
                    callback=step_outro
                )
                return

            append_text(
                f"👀 Target acquired! Process {victim} is clogging the system. Time to shut it down to free up resources!",
                sound_action="suspense",
                callback=lambda: display_victim(step, allocation, available, processes, need, victim)
            )

        def display_victim(step, allocation, available, processes, need, victim):
            alloc_str = ", ".join([f"{r}: {allocation[victim][r]}" for r in self.resources])
            avail_str = ", ".join([f"{r}: {available[r]}" for r in self.resources])
            append_text(
                f"📋 Evidence on {victim}: Holding [{alloc_str}] | Available Resources: [{avail_str}]",
                sound_action="pop",
                callback=lambda: terminate_process(step, allocation, available, processes, need, victim)
            )

        def terminate_process(step, allocation, available, processes, need, victim):
            released = {}
            for r in self.resources:
                if allocation[victim][r] > 0:
                    released[r] = allocation[victim][r]
                    available[r] += allocation[victim][r]
                    allocation[victim][r] = 0
                    need[victim][r] = 0
            released_str = ", ".join([f"{r}: {released[r]}" for r in released]) if released else "None"
            new_avail_str = ", ".join([f"{r}: {available[r]}" for r in self.resources])
            append_text(
                f"🛑 Process {victim} terminated! Released: [{released_str}] | New Available Resources: [{new_avail_str}]",
                sound_action="rewind",
                callback=lambda: update_rag(step, allocation, available, processes, need, victim)
            )

        def update_rag(step, allocation, available, processes, need, victim):
            append_text(
                "📊 Updating the Resource Allocation Graph to reflect the termination...",
                sound_action="check",
                callback=lambda: check_safety(step, allocation, available, processes, need, victim)
            )
            # Optional: Visualize RAG (uncomment to enable)
            # rag = self._build_rag(need)
            # flat_allocation = self._flatten_allocation(allocation)
            # visualize_multi_rag(rag, flat_allocation, need, unfinished_processes=processes)

        def check_safety(step, allocation, available, processes, need, victim):
            detector = MultiInstanceDeadlockDetector(allocation, self.max_matrix, available, self.total_resources)
            has_deadlock, message = detector.detect_deadlock()
            append_text(
                f"🔍 Running the Banker’s Algorithm with Available: [{', '.join([f'{r}: {available[r]}' for r in self.resources])}]",
                sound_action="check",
                callback=lambda: display_safety_result(step, allocation, available, processes, need, victim, has_deadlock, detector)
            )

        def display_safety_result(step, allocation, available, processes, need, victim, has_deadlock, detector):
            if not has_deadlock:
                append_text(
                    f"🌟 Case cracked! After terminating {victim}, the system is safe with sequence: {detector.safe_sequence}! A tough call, but it worked!",
                    sound_action="safe",
                    callback=step_outro
                )
            else:
                append_text(
                    f"😕 Still locked: {message}. Termination of {victim} wasn’t enough. We need another target...",
                    sound_action="wait",
                    callback=lambda: finalize_step(step, allocation, available, processes, need, victim)
                )

        def finalize_step(step, allocation, available, processes, need, victim):
            processes.remove(victim)
            append_text(
                f"✅ Process {victim} is out of the game. Checking if the system’s clear...",
                sound_action="check",
                callback=lambda: process_step(step + 1, allocation, available, processes, need)
            )

        def step_outro():
            """Final step: Conclude the termination process."""
            append_text(
                "🎬 Case closed! Termination is a heavy price, but sometimes it’s the only way. Keep those systems safe, detectives!",
                sound_action="safe",
                callback=finalize
            )

        def finalize():
            """Disable the text area to end the mode."""
            text_area.config(state=tk.DISABLED)

        try:
            step_intro()
        except Exception as e:
            logging.error(f"Error in process termination mode: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}", parent=termination_window)
            text_area.config(state=tk.DISABLED)

    def _build_rag(self, need):
        """Builds the RAG for visualization."""
        rag = {}
        for p in self.processes:
            rag[p] = []
        for r in self.resources:
            rag[r] = []

        for p in self.processes:
            for r in self.resources:
                if need[p][r] > 0:
                    rag[p].append(r)
        for p in self.processes:
            for r in self.resources:
                if self.allocation[p][r] > 0:
                    rag[r].append(p)
        return rag

    def _flatten_allocation(self, allocation):
        """Flattens allocation for visualization."""
        flat_allocation = {}
        for p in allocation:
            flat_allocation[p] = []
            for r in allocation[p]:
                instances = allocation[p][r]
                flat_allocation[p].extend([r] * instances)
        return flat_allocation