import networkx as nx
import numpy as np
import itertools 

def get_stabilizer_and_decoding_maps():
    """
    Defines the stabilizer connectivity and the mapping for the decoding graph.
    This corresponds to a specific surface code layout (e.g., rotated surface code 13-qubit).
    """
    z_stabilizers = {
        'c_z[0]': ('d[0]', 'd[1]', 'd[3]'),
        'c_z[1]': ('d[1]', 'd[2]', 'd[4]'),
        'c_z[2]': ('d[3]', 'd[5]', 'd[6]', 'd[8]'),
        'c_z[3]': ('d[4]', 'd[6]', 'd[7]', 'd[9]'),
        'c_z[4]': ('d[8]', 'd[10]', 'd[11]'),
        'c_z[5]': ('d[9]', 'd[11]', 'd[12]')
    }
    x_stabilizers = {
        'c_x[0]': ('d[0]', 'd[3]', 'd[5]'),
        'c_x[1]': ('d[1]', 'd[3]', 'd[4]', 'd[6]'),
        'c_x[2]': ('d[2]', 'd[4]', 'd[7]'),
        'c_x[3]': ('d[5]', 'd[8]', 'd[10]'),
        'c_x[4]': ('d[6]', 'd[8]', 'd[9]', 'd[11]'),
        'c_x[5]': ('d[7]', 'd[9]', 'd[12]')
    }
    
    # Maps spatial edges (ancilla pairs) to the corresponding data qubit index for Z-graph (X-errors)
    z_spatial_map = {
        (0, 1): 1, (0, 2): 3, (1, 3): 4, (2, 3): 6, 
        (2, 4): 8, (3, 5): 9, (4, 5): 11
    }
    # Maps boundary ancilla indices to their corresponding data qubit index for Z-graph
    z_boundary_map = {0: 0, 1: 2, 2: 5, 3: 7, 4: 10, 5: 12}
    
    # Maps spatial edges (ancilla pairs) to the corresponding data qubit index for X-graph (Z-errors)
    x_spatial_map = {
        (0, 1): 3, (0, 3): 5, (1, 2): 4, (1, 4): 6, 
        (2, 5): 7, (3, 4): 8, (4, 5): 9
    }
    # Maps boundary ancilla indices to their corresponding data qubit index for X-graph
    x_boundary_map = {0: 0, 1: 1, 2: 2, 3: 10, 4: 11, 5: 12}

    return (
        z_stabilizers, x_stabilizers, 
        z_spatial_map, z_boundary_map, 
        x_spatial_map, x_boundary_map
    )

# --- Create Decoding Graph (with a single boundary node) ---
def create_decoding_graph(num_rounds, num_ancillas, spatial_edges, boundary_map, p_data, p_meas):
    """
    Creates the space-time decoding graph for MWPM.
    
    Args:
        num_rounds (int): Number of syndrome measurement rounds (T).
        num_ancillas (int): Number of ancilla qubits (N_a).
        spatial_edges (list): List of tuples (a_i, a_j) representing spatial connections.
        boundary_map (dict): Map from boundary ancilla index to data qubit index.
        p_data (float): Data qubit error probability.
        p_meas (float): Measurement error probability.
        
    Returns:
        nx.Graph: The decoding graph.
    """
    G = nx.Graph()
    w_spatial = -np.log(p_data) if p_data > 0 else float('inf')
    w_temporal = -np.log(p_meas) if p_meas > 0 else float('inf')
    w_boundary_edge = -np.log(p_data) if p_data > 0 else float('inf') # Boundary edge weight
    
    num_nodes_per_round = num_ancillas
    
    # 1. Spatial edges
    # Add edges within each time slice (round)
    for r in range(num_rounds):
        offset = r * num_nodes_per_round
        for u_raw, v_raw in spatial_edges:
            u, v = min(u_raw, v_raw), max(u_raw, v_raw)
            G.add_edge(u + offset, v + offset, weight=w_spatial, type='spatial', qubits=((u_raw, v_raw),))
            
    # 2. Temporal edges
    # Add edges connecting the same ancilla across different time slices
    for r in range(num_rounds - 1):
        offset1 = r * num_nodes_per_round
        offset2 = (r + 1) * num_nodes_per_round
        for a in range(num_ancillas):
            G.add_edge(a + offset1, a + offset2, weight=w_temporal, type='temporal', qubits=())

    # 3. Boundary edges
    # Connect nodes in the final round to a single boundary node
    final_round_offset = (num_rounds - 1) * num_nodes_per_round
    boundary_node = num_rounds * num_nodes_per_round # The single boundary node
    G.add_node(boundary_node) 
    
    for a_idx in range(num_ancillas):
        if a_idx in boundary_map: 
            # Find the corresponding node in the final measurement round
            node_in_final_round = a_idx + final_round_offset
            G.add_edge(
                node_in_final_round, 
                boundary_node, 
                weight=w_boundary_edge, 
                type='boundary', 
                qubits=((a_idx,),) # Store which ancilla this boundary edge corresponds to
            )
        
    return G

# --- Calculate Syndrome from Final Result Bits ---
def calculate_syndrome_from_res(res_bits, stabilizers_map, num_ancillas):
    """
    Calculates the final syndrome by measuring stabilizers on the final data qubit state (res_bits).
    """
    final_syndrome = np.zeros(num_ancillas, dtype=int)
    
    for a_idx, (a_name, data_qubits) in enumerate(stabilizers_map.items()):
        parity = 0
        for dq_str in data_qubits: 
            dq_idx = int(dq_str[2:-1]) # e.g., 'd[0]' -> 0
            parity ^= res_bits[dq_idx]
        final_syndrome[a_idx] = parity
        
    return final_syndrome

# --- Main Reporting Function ---
def run_error_correction_and_reporting(
    measured_string, num_rounds, num_data_qubits, num_x_ancillas, num_z_ancillas,
    spatial_edges_z, spatial_edges_x, prob_data_x, prob_data_z, prob_meas_z, prob_meas_x,
    injected_error_group, injected_data_flip_index, injected_ancilla_flip_index,
    enable_debug_printing=False): 
    
    (z_stabilizers, x_stabilizers, 
     z_spatial_map, z_boundary_map, 
     x_spatial_map, x_boundary_map) = get_stabilizer_and_decoding_maps()
    
    # --- 1. Parsing ---
    # Parse the long measurement string into separate arrays
    num_sx = num_rounds * num_x_ancillas
    num_sz = num_rounds * num_z_ancillas
    cleaned_string = measured_string.replace(" ", "")
    
    # [::-1] reverses the bits to match the order (e.g., R0, R1, R2...)
    sx_bits = [int(bit) for bit in cleaned_string[0:num_sx]][::-1]
    sz_bits = [int(bit) for bit in cleaned_string[num_sx : num_sx + num_sz]][::-1]
    res_bits = [int(bit) for bit in cleaned_string[num_sx + num_sz:]][::-1]

    # --- 2. 2D Transformation ---
    # Reshape the 1D syndrome arrays into 2D (round, ancilla_index)
    sz_syndromes = np.array(sz_bits).reshape((num_rounds, num_z_ancillas))
    sx_syndromes = np.array(sx_bits).reshape((num_rounds, num_x_ancillas))
    
    # --- 3. Defect Calculation (Bulk) ---
    # Defects are the XOR between consecutive syndrome measurements
    z_defects = np.zeros((num_rounds, num_z_ancillas), dtype=int)
    z_defects[0, :] = sz_syndromes[0, :] # R0 defect is just R0 syndrome
    for r in range(1, num_rounds):
        z_defects[r, :] = np.bitwise_xor(sz_syndromes[r, :], sz_syndromes[r-1, :])
        
    x_defects = np.zeros((num_rounds, num_x_ancillas), dtype=int)
    x_defects[0, :] = sx_syndromes[0, :] # R0 defect is just R0 syndrome
    for r in range(1, num_rounds):
        x_defects[r, :] = np.bitwise_xor(sx_syndromes[r, :], sx_syndromes[r-1, :])

    # --- 4. Boundary Defect Calculation ---
    # Calculate the "final" syndrome based on the measured data qubits (res_bits)
    final_z_syndrome = calculate_syndrome_from_res(res_bits, z_stabilizers, num_z_ancillas)
    # Note: X-syndrome from res_bits is assumed 0 as we only correct Z-errors on res_bits
    final_x_syndrome = np.zeros(num_x_ancillas, dtype=int) 
    
    # The final defect is the XOR between the last measurement (R_T-1) and the final calculated syndrome
    final_z_defects = np.bitwise_xor(sz_syndromes[num_rounds-1, :], final_z_syndrome)
    final_x_defects = np.bitwise_xor(sx_syndromes[num_rounds-1, :], final_x_syndrome)

    # --- 5. MWPM Graph Creation (Total Parity Check) ---
    
    # Z-Graph (for correcting X-errors)
    z_graph = create_decoding_graph(num_rounds, num_z_ancillas, spatial_edges_z, z_boundary_map, prob_data_x, prob_meas_z)
    z_defect_nodes = []
    z_boundary_node = num_rounds * num_z_ancillas # Index of the single boundary node
    
    # 1. Add bulk defects (from R0, R1, ..., R_T-1)
    for r in range(num_rounds):
        for a in range(num_z_ancillas):
            if z_defects[r, a] == 1:
                z_defect_nodes.append(r * num_z_ancillas + a)
    
    # 2. Add final boundary defects
    # (final_z_defects are the defects between R_T-1 and res_bits)
    final_z_defect_count = 0
    for a in range(num_z_ancillas):
        if final_z_defects[a] == 1:
            # This defect is located at the node in the *final* round (R_T-1 slice)
            z_defect_nodes.append((num_rounds - 1) * num_z_ancillas + a)
            final_z_defect_count += 1
            
    # Check parity of *all* defects. If odd, pair one with the boundary.
    if len(z_defect_nodes) % 2 == 1:
        z_defect_nodes.append(z_boundary_node)
    
    # Create the complete graph K_z for matching
    K_z = nx.Graph()
    for u, v in itertools.combinations(z_defect_nodes, 2):
        path_weight = nx.shortest_path_length(z_graph, source=u, target=v, weight='weight')
        K_z.add_edge(u, v, weight=path_weight)
        
    # Find the minimum weight perfect matching
    z_matching_edges = nx.min_weight_matching(K_z)
    
    # Convert the matching on K_z back to a set of edges on the original z_graph
    z_matching = set()
    for u, v in z_matching_edges:
        path = nx.shortest_path(z_graph, source=u, target=v, weight='weight')
        for i in range(len(path) - 1):
            z_matching.add(tuple(sorted((path[i], path[i+1]))))

    # X-Graph (for correcting Z-errors)
    x_graph = create_decoding_graph(num_rounds, num_x_ancillas, spatial_edges_x, x_boundary_map, prob_data_z, prob_meas_x)
    x_defect_nodes = []
    x_boundary_node = num_rounds * num_x_ancillas 

    # 1. Add bulk defects (R0, R1, ...)
    for r in range(num_rounds):
        for a in range(num_x_ancillas):
            if x_defects[r, a] == 1:
                x_defect_nodes.append(r * num_x_ancillas + a)

    # 2. Add final boundary defects
    final_x_defect_count = 0
    for a in range(num_x_ancillas):
        if final_x_defects[a] == 1:
            # This defect is located at the node in the *final* round (R_T-1 slice)
            x_defect_nodes.append((num_rounds - 1) * num_x_ancillas + a)
            final_x_defect_count += 1
            
    # Check parity. If odd, pair one with the boundary.
    if len(x_defect_nodes) % 2 == 1:
        x_defect_nodes.append(x_boundary_node)

    # Create the complete graph K_x for matching
    K_x = nx.Graph()
    for u, v in itertools.combinations(x_defect_nodes, 2):
        path_weight = nx.shortest_path_length(x_graph, source=u, target=v, weight='weight')
        K_x.add_edge(u, v, weight=path_weight)
        
    # Find the minimum weight perfect matching
    x_matching_edges = nx.min_weight_matching(K_x)
    
    # Convert the matching on K_x back to a set of edges on the original x_graph
    x_matching = set()
    for u, v in x_matching_edges:
        path = nx.shortest_path(x_graph, source=u, target=v, weight='weight')
        for i in range(len(path) - 1):
            x_matching.add(tuple(sorted((path[i], path[i+1]))))

    # --- 6. Apply Correction ---
    
    corrected_res_bits = np.array(res_bits)
    # We apply Z-error corrections to the *syndrome* (or defect), not the res_bits
    corrected_final_x_syndrome = np.array(final_x_defects) 
    
    # Z-Graph (X-Error) Correction -> Flips res_bits
    for u, v in z_matching:
        edge_data = z_graph.get_edge_data(u, v)
        if edge_data is None: continue
        edge_type = edge_data['type']
        
        if edge_type == 'spatial':
            # This edge corresponds to a data qubit flip
            ancilla_pair = edge_data['qubits'][0] 
            key = tuple(sorted(ancilla_pair)) 
            qubit_to_flip = z_spatial_map.get(key)
            if qubit_to_flip is not None:
                corrected_res_bits[qubit_to_flip] = 1 - corrected_res_bits[qubit_to_flip]
                
        elif edge_type == 'boundary':
            # This edge corresponds to a data qubit flip at the boundary
            ancilla_idx = edge_data['qubits'][0][0] 
            qubit_to_flip = z_boundary_map.get(ancilla_idx)
            if qubit_to_flip is not None:
                corrected_res_bits[qubit_to_flip] = 1 - corrected_res_bits[qubit_to_flip]

    # X-Graph (Z-Error) Correction -> Flips the final_x_syndrome
    # We are tracking the *logical* Z error, which is detected by the final X-stabilizers
    for u, v in x_matching:
        edge_data = x_graph.get_edge_data(u, v)
        if edge_data is None: continue
        edge_type = edge_data['type']
        
        if edge_type == 'spatial':
            ancilla_pair = edge_data['qubits'][0]
            key = tuple(sorted(ancilla_pair))
            qubit_to_flip = x_spatial_map.get(key) # This is a Z-error on d[qubit_to_flip]
            
            if qubit_to_flip is not None: 
                # Find all X-stabilizers that measure this data qubit
                for a_idx, data_qubits in enumerate(x_stabilizers.values()):
                    if f'd[{qubit_to_flip}]' in data_qubits:
                        # Flip the corresponding syndrome bit
                        corrected_final_x_syndrome[a_idx] = 1 - corrected_final_x_syndrome[a_idx]

        elif edge_type == 'boundary':
            ancilla_idx = edge_data['qubits'][0][0]
            qubit_to_flip = x_boundary_map.get(ancilla_idx) # Z-error on d[qubit_to_flip]

            if qubit_to_flip is not None: 
                # Find all X-stabilizers that measure this data qubit
                for a_idx, data_qubits in enumerate(x_stabilizers.values()):
                    if f'd[{qubit_to_flip}]' in data_qubits:
                        # Flip the corresponding syndrome bit
                        corrected_final_x_syndrome[a_idx] = 1 - corrected_final_x_syndrome[a_idx]

    # --- 7. Error Reporting ---
    
    no_error_injected = (injected_error_group == 'Data' and injected_data_flip_index is None) or \
                          (injected_error_group == 'Measurement' and injected_ancilla_flip_index is None)

    # 1. Recalculate Z-stabilizers with the *corrected* res_bits
    corrected_final_z_syndrome = calculate_syndrome_from_res(corrected_res_bits, z_stabilizers, num_z_ancillas)
    
    # 2. Check for Logical-X error
    # This is the parity of the logical Z-operator (e.g., Z_L = d[2]d[7]d[12])
    logical_x_error_parity = corrected_res_bits[2] ^ corrected_res_bits[7] ^ corrected_res_bits[12]
    
    # 3. Detect Logical-X error
    # A logical-X error is detected if:
    # a) Any Z-stabilizer is unsatisfied OR
    # b) The logical-Z operator parity is 1
    logical_x_error_detected = any(corrected_final_z_syndrome) or (logical_x_error_parity == 1)
    
    # 4. Detect Logical-Z error
    # A logical-Z error is detected if any (corrected) X-stabilizer is unsatisfied
    logical_z_error_detected = any(corrected_final_x_syndrome)
    
    logical_error_detected = logical_x_error_detected or logical_z_error_detected
    
    # --- Debug Printing ---
    if enable_debug_printing and logical_error_detected:
        print("--- 🐞 DECODER INTERNAL DUMP (UE) 🐞 ---")
        
        injected_error_details = "None"
        if injected_error_group == 'Data' and injected_data_flip_index is not None:
            injected_error_details = f"Data d[{injected_data_flip_index}]"
        elif injected_error_group == 'Measurement' and injected_ancilla_flip_index is not None:
            # Assuming measurement error is always injected at R0 for this debug print
            injected_error_details = f"Meas (R0) Anc[{injected_ancilla_flip_index}]"
        print(f"DEBUG: Injected Error: {injected_error_details}")

        print(f"Parsed sx_bits (R0...R{num_rounds-1}): {sx_bits}")
        print(f"Parsed sz_bits (R0...R{num_rounds-1}): {sz_bits}")
        print(f"Parsed res_bits: {res_bits}")
        print(f"X-Defects (R0..R{num_rounds-1}): {x_defects.T}")
        print(f"Z-Defects (R0..R{num_rounds-1}): {z_defects.T}")
        print(f"Final X-Defects: {final_x_defects}")
        print(f"Final Z-Defects: {final_z_defects}")

        # Recalculate defect nodes for printing (as they were modified by parity check)
        debug_x_nodes = []
        for r in range(num_rounds):
            for a in range(num_x_ancillas):
                if x_defects[r, a] == 1: debug_x_nodes.append(r*num_x_ancillas+a)
        for a in range(num_x_ancillas):
            if final_x_defects[a] == 1: debug_x_nodes.append((num_rounds-1)*num_x_ancillas+a)
        if len(debug_x_nodes) % 2 == 1: debug_x_nodes.append(x_boundary_node)
        
        debug_z_nodes = []
        for r in range(num_rounds):
            for a in range(num_z_ancillas):
                if z_defects[r, a] == 1: debug_z_nodes.append(r*num_z_ancillas+a)
        for a in range(num_z_ancillas):
            if final_z_defects[a] == 1: debug_z_nodes.append((num_rounds-1)*num_z_ancillas+a)
        if len(debug_z_nodes) % 2 == 1: debug_z_nodes.append(z_boundary_node)

        print(f"X-Defect Nodes (for MWPM): {debug_x_nodes}")
        print(f"Z-Defect Nodes (for MWPM): {debug_z_nodes}")
        
        print(f"X-Matching (edges): {x_matching}")
        print(f"Z-Matching (edges): {z_matching}")
        print(f"Original res_bits: {np.array(res_bits)}")
        print(f"Corrected res_bits: {corrected_res_bits}")
        print(f"Corrected X-Syndrome: {corrected_final_x_syndrome} (Any={any(corrected_final_x_syndrome)})")
        print(f"Corrected Z-Syndrome: {corrected_final_z_syndrome} (Any={any(corrected_final_z_syndrome)})")
        print(f"Logical X Parity (Z_L): {logical_x_error_parity}")
        print(f"-> Result: logical_x_error: {logical_x_error_detected}, logical_z_error: {logical_z_error_detected}")
        print("---------------------------------------")
    # --- [END DEBUG] ---

    
    if no_error_injected and not logical_error_detected:
        return 'NE' # No Error (No error injected, no logical error detected)
    elif not no_error_injected and not logical_error_detected:
        return 'CE' # Correctable Error (Error injected, no logical error detected)
    elif logical_error_detected:
        return 'UE' # Uncorrectable Error (Logical error detected, regardless of injection)
    else:
        # This case (no_error_injected and logical_error_detected) should be covered by 'UE'
        return 'UE' 
