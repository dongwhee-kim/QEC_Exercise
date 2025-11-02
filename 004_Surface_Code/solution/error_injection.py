from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys
import random

# --- Example: Single Data Qubit Error ---
# single data qubit error 'or' single measurement error
# error injection only round_idx=0

# e.g., d[5] bit flip (X error) at round=0
# round0: c_z[2] = 0 -> 1 (change!)
# round1: c_z[2] (index 8 in 1D array) = 1 -> 1 (non-change!) [error_remain]
# round2: c_z[2] (index 14 in 1D array) = 1 -> 1 (non-change!) [error_remain]
# result: c_z[2] single event at R0 -> correct only d[5] (apply bit-flip gate)

# --- Example: Single Measurement Error ---
# e.g., sz[2] (ancilla 2) measurement error at round=0
# -> This error is applied *After* AerSimulator simulation!!!
# round0: sz[2] = 0 -> 1 (change!)
# round1: sz[8] (ancilla 2, round 1) = 1 -> 0 (change!)
# round2: sz[14] (ancilla 2, round 2) = 0 -> 0 (non-change!)
# result: sz[2], sz[8] double event -> no correction. shortest path is a time-like edge (measurement error)

def error_injection_single_qubit_error_func(qc, flip_index, error_type='X'):
    """
    Injects a single X, Y, or Z error on a specific qubit (data or ancilla)
    before the circuit runs.
    """
    if flip_index is None:
        return
    
    if error_type == 'X':
        qc.x(flip_index)
    elif error_type == 'Z':
        qc.z(flip_index)
    elif error_type == 'Y':
        qc.x(flip_index)
        qc.z(flip_index)
    else:
        print("Wrong Error Type")
        sys.exit(1)

    return

def post_process_measurement_error_func(measured_string, ancilla_flip_index, error_type, round_idx, num_z_ancillas, num_x_ancillas):
    """
    Manually injects a single measurement error (classical bit flip)
    into the 'measured_string' obtained *after* simulator execution.
    This is for single-error injection tests.
    """
    if ancilla_flip_index is None:
        return measured_string

    num_rounds = 3 # This code is fixed for d=3, 3 rounds
    num_total_sx_bits = num_rounds * num_x_ancillas
    num_total_sz_bits = num_rounds * num_z_ancillas

    # Remove spaces between registers (e.g., "000 111" -> "000111")
    cleaned_string = measured_string.replace(" ", "")
    
    # Qiskit counts string is in order: 'sx[17]...sx[0] sz[17]...sz[0] res[12]...res[0]'
    # Convert to list to make it mutable
    sx_bits = list(cleaned_string[0:num_total_sx_bits])
    sz_bits = list(cleaned_string[num_total_sx_bits : num_total_sx_bits + num_total_sz_bits])
    res_bits = list(cleaned_string[num_total_sx_bits + num_total_sz_bits:])
    
    # 'sz[5]...sz[0]' (round 0), 'sz[11]...sz[6]' (round 1) ...
    # The Qiskit string order is the reverse of little-endian indexing.
    # e.g., sx[0] bit is the 1st from the *right end* of sx_bits string (index 17 for 18 bits).
    # e.g., sx[5] bit is the 6th from the *right end* of sx_bits string (index 12 for 18 bits).
    
    if error_type == 'Z' or error_type == 'Y': # Z-stabilizer (sz) measurement error
        # Calculate the index within the total 'sz' string based on round and ancilla index
        # (num_total_sz_bits - 1) is the leftmost index (e.g., 17)
        bit_pos_in_str = (num_total_sz_bits - 1) - (round_idx * num_z_ancillas + ancilla_flip_index)
        
        # Bit flip
        current_bit = sz_bits[bit_pos_in_str]
        sz_bits[bit_pos_in_str] = '1' if current_bit == '0' else '0'
        
    elif error_type == 'X': # X-stabilizer (sx) measurement error
        # Calculate the index within the total 'sx' string
        bit_pos_in_str = (num_total_sx_bits - 1) - (round_idx * num_x_ancillas + ancilla_flip_index)
        
        # Bit flip
        current_bit = sx_bits[bit_pos_in_str]
        sx_bits[bit_pos_in_str] = '1' if current_bit == '0' else '0'

    # Rejoin the modified bit strings and return
    return "".join(sx_bits) + "".join(sz_bits) + "".join(res_bits)

def error_injection_logical_error_rate_func(qc, num_data_qubits, prob_data_x, prob_data_z):
    """
    For LER (Logical Error Rate) testing:
    Injects probabilistic X and Z errors on *all* data qubits.
    (A Y error occurs if both X and Z are applied).
    """
    # Assumes the data qubit register 'd' starts from qubit index 0
    for i in range(num_data_qubits):
        
        # Check to inject X error
        if random.random() < prob_data_x:
            qc.x(i)
        
        # Check to inject Z error
        if random.random() < prob_data_z:
            qc.z(i)
            
    return

# --- ⭐️ [Newly Added Function] ⭐️ ---
def post_process_ler_measurement_errors(measured_string, num_rounds, num_x_ancillas, num_z_ancillas, prob_meas_x, prob_meas_z):
    """
    For LER (Logical Error Rate) testing:
    After simulator execution, injects probabilistic measurement errors
    (classical bit flips) on *all* syndrome bits in 'measured_string'.
    """
    num_total_sx_bits = num_rounds * num_x_ancillas
    num_total_sz_bits = num_rounds * num_z_ancillas

    cleaned_string = measured_string.replace(" ", "")
    
    sx_bits = list(cleaned_string[0:num_total_sx_bits])
    sz_bits = list(cleaned_string[num_total_sx_bits : num_total_sx_bits + num_total_sz_bits])
    res_bits = list(cleaned_string[num_total_sx_bits + num_total_sz_bits:])
    
    # Iterate over all rounds and all ancilla qubits
    for r in range(num_rounds):
        # X-Ancillas (sx)
        for a in range(num_x_ancillas):
            if random.random() < prob_meas_x:
                # Calculate Qiskit string index (right is LSB, so we count from the left)
                bit_pos_in_str = (num_total_sx_bits - 1) - (r * num_x_ancillas + a)
                current_bit = sx_bits[bit_pos_in_str]
                sx_bits[bit_pos_in_str] = '1' if current_bit == '0' else '0'

        # Z-Ancillas (sz)
        for a in range(num_z_ancillas):
            if random.random() < prob_meas_z:
                # Calculate Qiskit string index
                bit_pos_in_str = (num_total_sz_bits - 1) - (r * num_z_ancillas + a)
                current_bit = sz_bits[bit_pos_in_str]
                sz_bits[bit_pos_in_str] = '1' if current_bit == '0' else '0'
                        
    # Rejoin all error-injected strings and return
    return "".join(sx_bits) + "".join(sz_bits) + "".join(res_bits)
