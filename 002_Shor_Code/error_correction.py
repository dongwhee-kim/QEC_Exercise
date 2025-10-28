from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Gate
import sys

def _correct_bit_flip_block(qc, c, q_indices, c_indices):
    """
    Helper function to correct a 3-qubit bit-flip code block
    q_indices: [q_a, q_b, q_c] (data qubit indices)
    c_indices: [c_s0, c_s1] (syndrome bit indices)
    """
    c_s0, c_s1 = c_indices
    q_a, q_b, q_c = q_indices

    # Syndrome c_s1 c_s0
    # 01 (c_s0=1, c_s1=0) -> X error on q_a
    with qc.if_test((c[c_s0], 1)):
        with qc.if_test((c[c_s1], 0)):
            qc.x(q_a)
    
    # 11 (c_s0=1, c_s1=1) -> X error on q_b
    with qc.if_test((c[c_s0], 1)):
        with qc.if_test((c[c_s1], 1)):
            qc.x(q_b)
            
    # 10 (c_s0=0, c_s1=1) -> X error on q_c
    with qc.if_test((c[c_s0], 0)):
        with qc.if_test((c[c_s1], 1)):
            qc.x(q_c)

def error_correction_func(qc):
    """
    Shor code error correction function
    Apply correction gates to 9 data qubits (q0~q8) based on c0~c7 syndrome bits
    """
    c = qc.cregs[0] # 9-bit classical register

    # --- 1. Bit-flip Correction (X errors) ---
    # Use c0~c5 syndrome bits
    
    # Block 1 (q0, q1, q2) / Syndromes (c0, c1)
    _correct_bit_flip_block(qc, c, [0, 1, 2], [0, 1])
    
    # Block 2 (q3, q4, q5) / Syndromes (c2, c3)
    _correct_bit_flip_block(qc, c, [3, 4, 5], [2, 3])
    
    # Block 3 (q6, q7, q8) / Syndromes (c4, c5)
    _correct_bit_flip_block(qc, c, [6, 7, 8], [4, 5])

    qc.barrier() # Barrier after X error correction

    # --- 2. Phase-flip Correction (Z errors) ---
    # Use c6, c7 syndrome bits
    
    # Syndrome c7 c6
    # 01 (c6=1, c7=0) -> Z error on Block 1 (q0, q1, q2)
    with qc.if_test((c[6], 1)):
        with qc.if_test((c[7], 0)):
            qc.z([0, 1, 2])
            
    # 11 (c6=1, c7=1) -> Z error on Block 2 (q3, q4, q5)
    with qc.if_test((c[6], 1)):
        with qc.if_test((c[7], 1)):
            qc.z([3, 4, 5])
            
    # 10 (c6=0, c7=1) -> Z error on Block 3 (q6, q7, q8)
    with qc.if_test((c[6], 0)):
        with qc.if_test((c[7], 1)):
            qc.z([6, 7, 8])

    return

