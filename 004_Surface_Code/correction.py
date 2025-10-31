import rustworkx as rx
import numpy as np
import layout

# Takes a list like ['000000', '010000', '010000'] (Rounds=3)
# and finds the defect nodes (ancilla_name, round).
def get_defects_from_syndromes(syndrome_list, ancilla_names):
    num_rounds = len(syndrome_list)
    if num_rounds == 0:
        return []
        
    num_ancillas = len(syndrome_list[0])
    
    # ancilla_names = list(layout.z_stabilizers.keys())
    
    # Convert string list to int array
    syndromes_int = np.array([list(map(int, list(s))) for s in syndrome_list])
    
    # Assume syndrome at round -1 is all zeros
    prev_syndrome = np.zeros(num_ancillas, dtype=int)
    
    defect_nodes = [] # List to store (ancilla_name, round)
    
    for r in range(num_rounds):
        current_syndrome = syndromes_int[r]
        # XOR with previous round to find defects
        defects = np.logical_xor(current_syndrome, prev_syndrome)
        
        for a_idx, has_defect in enumerate(defects):
            if has_defect:
                ancilla_name = ancilla_names[a_idx]
                defect_nodes.append((ancilla_name, r))
                
        prev_syndrome = current_syndrome
        
    return defect_nodes

# Runs MWPM matching on the graph given a list of defect nodes.
def run_mwpm(graph, node_map, defect_nodes_named):
    """
    Args:
        graph (rx.PyGraph): The decoding graph.
        node_map (dict): Map from (name, round) to node_index.
        defect_nodes_named (list): List of (ancilla_name, round) tuples.
    """
    
    # Convert (name, round) tuples to graph node indices
    defect_node_indices = [node_map[name_round] for name_round in defect_nodes_named]

    if not defect_node_indices:
        return None
        
    # Run MWPM
    # This finds the MINIMUM weight matching, so weights are positive
    matching = rx.min_weight_perfect_matching(
        graph,
        weight_fn=lambda edge: float(edge), 
        nodes=defect_node_indices
    )
    
    return matching # Returns a list of (node1_idx, node2_idx) tuples