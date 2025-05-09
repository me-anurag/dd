import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def visualize_multi_rag(rag, flat_allocation, need, safe_sequence=None, unfinished_processes=None):
    """Visualizes the Resource Allocation Graph (RAG) for a multi-instance system.

    Args:
        rag (dict): Dict mapping nodes (processes/resources) to their neighbors.
        flat_allocation (dict): Flattened allocation matrix for visualization.
        need (dict): Need matrix for determining request edges.
        safe_sequence (list, optional): The safe sequence determined by the deadlock detector.
        unfinished_processes (list, optional): List of processes that couldn't finish (involved in deadlock).
    """
    G_rag = nx.DiGraph()
    processes = [node for node in rag if node.startswith("P")]
    resources = [node for node in rag if node.startswith("R")]

    # Add nodes
    for p in processes:
        G_rag.add_node(p, type="process")
    for r in resources:
        G_rag.add_node(r, type="resource")

    # Add edges with instance counts
    for p in processes:
        for r in rag[p]:  # Request edges (P -> R)
            instances_needed = need[p][r]
            if instances_needed > 0:
                G_rag.add_edge(p, r, type="request", instances=instances_needed)
    for r in resources:
        for p in rag[r]:  # Allocation edges (R -> P)
            instances_allocated = flat_allocation[p].count(r)
            if instances_allocated > 0:
                G_rag.add_edge(r, p, type="allocation", instances=instances_allocated)

    # Determine status
    if safe_sequence and len(safe_sequence) > 0:
        status = f"Safe Sequence: {safe_sequence}"
        status_color = "green"
    else:
        status = "No Safe Execution Sequence Found"
        status_color = "red"
        if unfinished_processes:
            status = f"Deadlock Found: Processes Involved: {unfinished_processes}"
            status_color = "red"

    # Visualization
    fig, ax = plt.subplots(figsize=(10, 8))
    pos = {}

    # Position processes (circles) at the bottom
    for i, p in enumerate(processes):
        pos[p] = (i * 1.5, 0)

    # Position resources (rectangles) at the top
    for i, r in enumerate(resources):
        pos[r] = (i * 1.5, 2)

    # Draw process nodes (circles)
    process_nodes = [n for n in G_rag.nodes() if G_rag.nodes[n]["type"] == "process"]
    nx.draw_networkx_nodes(G_rag, pos, nodelist=process_nodes, node_shape='o', node_color="lightblue", 
                           node_size=800, ax=ax)

    # Draw resource nodes (rectangles) with dots
    resource_nodes = [n for n in G_rag.nodes() if G_rag.nodes[n]["type"] == "resource"]
    for r in resource_nodes:
        x, y = pos[r]
        # Draw rectangle
        rect = Rectangle((x - 0.4, y - 0.2), 0.8, 0.4, fill=True, color="lightgreen", ec="black")
        ax.add_patch(rect)
        # Add dots based on total instances
        total_instances = sum(need[p][r] + flat_allocation[p].count(r) for p in processes)
        max_dots = 5  # Maximum number of dots to display
        for dot in range(min(int(total_instances), max_dots)):
            ax.plot(x - 0.3 + (dot * 0.15), y, 'o', color="black", markersize=5)
        # If total_instances > max_dots, add a label to indicate additional instances
        if total_instances > max_dots:
            ax.text(x + 0.4, y, f"+{int(total_instances - max_dots)}", fontsize=8, color="black", va="center")

    # Draw edges
    for edge in G_rag.edges(data=True):
        src, dst, data = edge
        instances = data["instances"]
        if data["type"] == "request":
            # Request edge: solid arrow
            ax.annotate("", xy=pos[dst], xytext=pos[src], 
                        arrowprops=dict(arrowstyle="->", color="red", lw=2))
            ax.text((pos[src][0] + pos[dst][0]) / 2, (pos[src][1] + pos[dst][1]) / 2 + 0.1,
                    f"R({instances})", fontsize=10, color="red", ha="center")
        else:
            # Allocation edge: dashed arrow
            ax.annotate("", xy=pos[dst], xytext=pos[src], 
                        arrowprops=dict(arrowstyle="->", color="blue", lw=2, linestyle="--"))
            ax.text((pos[src][0] + pos[dst][0]) / 2, (pos[src][1] + pos[dst][1]) / 2 - 0.1,
                    f"H({instances})", fontsize=10, color="blue", ha="center")

    # Draw labels
    nx.draw_networkx_labels(G_rag, pos, font_size=12, ax=ax)

    # Set title
    ax.set_title("Multi-Instance Resource Allocation Graph", pad=20)
    ax.axis("off")

    # Add legend at bottom-left corner
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=10, label='Process'),
        plt.Rectangle((0, 0), 1, 1, facecolor='lightgreen', edgecolor='black', label='Resource'),
        plt.Line2D([0], [0], color='red', lw=2, label='Request Edge (R)'),
        plt.Line2D([0], [0], color='blue', lw=2, linestyle='--', label='Held Edge (H)')
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=10, frameon=True, bbox_to_anchor=(0, 0))

    # Add status text below the legend
    plt.figtext(0.05, 0.05, status, ha="left", fontsize=12, color=status_color, wrap=True)

    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    plt.show()