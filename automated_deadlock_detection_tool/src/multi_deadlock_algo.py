class MultiInstanceDeadlockDetector:
    """A class to detect deadlocks in a multi-instance resource system using the Banker's Algorithm.

    Args:
        allocation (dict): Dict of process -> resource -> allocated instances.
        max_matrix (dict): Dict of process -> resource -> maximum required instances.
        available (dict): Dict of resource -> available instances.
        total_resources (dict): Dict of resource -> total instances in the system.
    """
    def __init__(self, allocation, max_matrix, available, total_resources):
        self.allocation = allocation
        self.max_matrix = max_matrix
        self.available = available.copy()  # Make a copy to avoid modifying the original
        self.total_resources = total_resources
        self.processes = list(allocation.keys())
        self.resources = list(total_resources.keys())
        self.has_deadlock = False
        self.safe_sequence = []

    def get_need(self):
        """Computes the Need matrix (Max - Allocation).

        Returns:
            dict: Dict of process -> resource -> needed instances.
        """
        need = {}
        for p in self.processes:
            need[p] = {}
            for r in self.resources:
                max_val = self.max_matrix[p].get(r, 0)
                alloc_val = self.allocation[p].get(r, 0)
                need_val = max_val - alloc_val
                if need_val < 0:
                    raise ValueError(f"Invalid data: Allocation ({alloc_val}) exceeds Max ({max_val}) for {p} and {r}")
                need[p][r] = need_val
        return need

    def can_process_run(self, process, need, work):
        """Checks if a process can run with the current available resources.

        Args:
            process (str): The process to check.
            need (dict): The Need matrix.
            work (dict): The current available resources.

        Returns:
            bool: True if the process can run, False otherwise.
        """
        for r in self.resources:
            if need[process][r] > work[r]:
                return False
        return True

    def detect_deadlock(self):
        """Detects if the system is in a deadlock or unsafe state using the Banker's Algorithm.

        Returns:
            tuple: (bool, str) where bool is True if there's a deadlock/unsafe state, and str is the message.
        """
        need = self.get_need()
        work = self.available.copy()
        finish = {p: False for p in self.processes}
        self.safe_sequence = []

        remaining_processes = self.processes.copy()
        while remaining_processes:
            found = False
            for p in remaining_processes[:]:  # Copy to avoid modifying during iteration
                if not finish[p] and self.can_process_run(p, need, work):
                    # Simulate running the process by releasing its allocated resources
                    for r in self.resources:
                        work[r] += self.allocation[p].get(r, 0)
                    finish[p] = True
                    self.safe_sequence.append(p)
                    remaining_processes.remove(p)
                    found = True
                    break
            if not found:
                # No process can run with current resources
                break

        if len(self.safe_sequence) == len(self.processes):
            self.has_deadlock = False
            return False, f"Safe sequence: {self.safe_sequence}"
        else:
            self.has_deadlock = True
            unfinished = [p for p in self.processes if not finish[p]]
            return True, f"No safe sequence found. System MAY be in an unsafe state or deadlocked. Unfinished processes: {unfinished}"