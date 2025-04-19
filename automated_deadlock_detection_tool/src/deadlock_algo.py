class DeadlockDetector:
    """A class to detect deadlocks in a system with single-instance resources using a Resource Allocation Graph (RAG).

    Args:
        resources_held (dict): A dictionary mapping processes (e.g., 'P1') to a list of resources they hold (e.g., ['R1']).
        resources_wanted (dict): A dictionary mapping processes to a list of resources they are requesting.
        total_resources (int): The total number of resources in the system.

    Raises:
        ValueError: If the input data is invalid (e.g., invalid resource names, duplicate allocations).
    """
    def __init__(self, resources_held, resources_wanted, total_resources):
        if total_resources <= 0:
            raise ValueError("Total resources must be positive.")
        self.resources_held = resources_held
        self.resources_wanted = resources_wanted
        self.total_resources = total_resources
        self.cycle = None  # To store the detected cycle
        self._validate_input()

    def _validate_input(self):
        """Validates the input data for consistency and correctness."""
        valid_resources = {f"R{i+1}" for i in range(self.total_resources)}
        # Validate resources_held
        for process, resources in self.resources_held.items():
            if not process.startswith("P"):
                raise ValueError(f"Invalid process name: {process}")
            for resource in resources:
                if resource not in valid_resources:
                    raise ValueError(f"Invalid resource {resource} in resources_held for {process}")
        # Validate resources_wanted
        for process, resources in self.resources_wanted.items():
            if not process.startswith("P"):
                raise ValueError(f"Invalid process name: {process}")
            for resource in resources:
                if resource not in valid_resources:
                    raise ValueError(f"Invalid resource {resource} in resources_wanted for {process}")
        # Check for duplicate allocations
        allocated_resources = set()
        for process, resources in self.resources_held.items():
            for resource in resources:
                if resource in allocated_resources:
                    raise ValueError(f"Resource {resource} is allocated to multiple processes")
                allocated_resources.add(resource)
        # Check for invalid requests (requesting a resource that is already held)
        for process in self.resources_wanted:
            for resource in self.resources_wanted[process]:
                if resource in self.resources_held.get(process, []):
                    raise ValueError(f"Invalid state: {process} requests {resource} which it already holds.")

    def build_rag(self):
        """Builds a Resource Allocation Graph (RAG) as an adjacency list.

        Returns:
            dict: A graph where keys are nodes (processes or resources) and values are lists of neighboring nodes.
        """
        graph = {}
        # Initialize nodes for processes
        for process in self.resources_held:
            graph[process] = []
        # Initialize nodes for resources
        for i in range(self.total_resources):
            resource = f"R{i+1}"
            graph[resource] = []
        # Add edges: Resource -> Process (allocation)
        for process, resources in self.resources_held.items():
            for resource in resources:
                if resource in graph:
                    graph[resource].append(process)
        # Add edges: Process -> Resource (request)
        for process, resources in self.resources_wanted.items():
            for resource in resources:
                if resource in graph:
                    graph[process].append(resource)
        return graph

    def detect_cycle(self, graph):
        """Detects if there is a cycle in the RAG, indicating a deadlock.

        Args:
            graph (dict): The RAG as an adjacency list.

        Returns:
            bool: True if a cycle is found, False otherwise.
        """
        visited = set()
        recursion_stack = set()
        parent = {}  # To reconstruct the cycle

        def dfs(node):
            visited.add(node)
            recursion_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    parent[neighbor] = node
                    if dfs(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    # Found a cycle, reconstruct it
                    cycle = []
                    current = node
                    while current != neighbor:
                        cycle.append(current)
                        current = parent[current]
                    cycle.append(neighbor)
                    cycle.append(node)  # Close the cycle
                    self.cycle = cycle
                    return True
            recursion_stack.remove(node)
            return False

        self.cycle = None
        for node in graph:
            if node.startswith("P") and node not in visited:
                if dfs(node):
                    return True
        return False

    def detect_deadlock(self):
        """Detects if a deadlock exists in the system.

        Returns:
            tuple: (bool, str) where the bool indicates if a deadlock was found, and the str is a message.
        """
        if not self.resources_held and not self.resources_wanted:
            return False, "Please allocate and request resources before detecting deadlock."
        if not self.resources_held:
            return False, "No resources are allocated. Please allocate resources before detecting deadlock."
        if not self.resources_wanted:
            return False, "No resources are requested. Please request resources before detecting deadlock."
        rag = self.build_rag()
        has_deadlock = self.detect_cycle(rag)
        if has_deadlock:
            return True, f"A deadlock has been detected involving: {self.cycle}"
        else:
            return False, "No deadlock detected in the system."