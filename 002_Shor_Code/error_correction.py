from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Gate
import sys

# Correct a 3-qubit bit-flip code block (X errors)
def error_correction_bit_flip_block(qc, c, q_indices, c_indices):
    # Block 1 [0, 1, 2] / Syndromes [0, 1]
    # Block 2 [3, 4, 5] / Syndromes [2, 3]
    # Block 3 [6, 7, 8] / Syndromes [4, 5]
    c_s0, c_s1 = c_indices
    q_a, q_b, q_c = q_indices

    # Syndrome table
    # c0c1 = '10' q0 X error correction / '11' q1 X error correction / '01' q2 X error correction
    # c2c3 = '10' q3 X error correction / '11' q4 X error correction / '01' q5 X error correction
    # c4c5 = '10' q6 X error correction / '11' q7 X error correction / '01' q8 X error correction

    with qc.if_test((c[c_s0], 1)):
        with qc.if_test((c[c_s1], 0)):
            qc.x(q_a)
    
    with qc.if_test((c[c_s0], 1)):
        with qc.if_test((c[c_s1], 1)):
            qc.x(q_b)
            
    with qc.if_test((c[c_s0], 0)):
        with qc.if_test((c[c_s1], 1)):
            qc.x(q_c)

# Shor code error correction function
# Applies corrections based on the 8 syndrome bits
def error_correction_func(qc):
    c = qc.cregs[0] # 9-bit classical register (c0-c7 syndrome, c8 result)

    # --- 1. Bit-flip Correction ---
    # Apply X gates based on c0~c5 syndrome bits (ZZ)
    
    # Block 1 (q0, q1, q2) / Syndromes (c0, c1)
    error_correction_bit_flip_block(qc, c, [0, 1, 2], [0, 1])
    
    # Block 2 (q3, q4, q5) / Syndromes (c2, c3)
    error_correction_bit_flip_block(qc, c, [3, 4, 5], [2, 3])
    
    # Block 3 (q6, q7, q8) / Syndromes (c4, c5)
    error_correction_bit_flip_block(qc, c, [6, 7, 8], [4, 5])

    qc.barrier() # Separate X correction from Z correction

    # --- 2. Phase-flip Correction ---
    # Apply Z gates based on c6, c7 syndrome bits (XX)
    # This corrects errors on a block-level.
    
    # Syndrome table
    # c6c7 = '10' q0 Z error correction / '11' q3 Z error correction / '01' q6 Z error correction

    with qc.if_test((c[6], 1)):
        with qc.if_test((c[7], 0)):
            qc.z(0) # Apply Z_L = Z to Block 1
            
    with qc.if_test((c[6], 1)):
        with qc.if_test((c[7], 1)):
            qc.z(3) # Apply Z_L = Z to Block 2
            
    with qc.if_test((c[6], 0)):
        with qc.if_test((c[7], 1)):
            qc.z(6) # Apply Z_L = Z to Block 3

    return