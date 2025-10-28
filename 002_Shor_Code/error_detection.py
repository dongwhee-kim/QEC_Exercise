from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

def error_detection_func(qc):
    """
    Shor code syndrome measurement
    Uses 8 ancilla qubits (q9~q16) to measure 8 syndrome bits (c0~c7)
    """
    
    # --- 1. Bit-flip Syndromes (Z-stabilizers) ---
    # Ancilla qubits q9 ~ q14, classical bits c0 ~ c5
    
    # Block 1 (q0, q1, q2)
    # S0 (c0) = Z0 Z1 (ancilla q9)
    qc.cx(0, 9)
    qc.cx(1, 9)
    # S1 (c1) = Z1 Z2 (ancilla q10)
    qc.cx(1, 10)
    qc.cx(2, 10)
    
    # Block 2 (q3, q4, q5)
    # S2 (c2) = Z3 Z4 (ancilla q11)
    qc.cx(3, 11)
    qc.cx(4, 11)
    # S3 (c3) = Z4 Z5 (ancilla q12)
    qc.cx(4, 12)
    qc.cx(5, 12)
    
    # Block 3 (q6, q7, q8)
    # S4 (c4) = Z6 Z7 (ancilla q13)
    qc.cx(6, 13)
    qc.cx(7, 13)
    # S5 (c5) = Z7 Z8 (ancilla q14)
    qc.cx(7, 14)
    qc.cx(8, 14)
    
    # Measure Bit-flip syndromes (q9-q14 -> c0-c5)
    qc.measure([9, 10, 11, 12, 13, 14], [0, 1, 2, 3, 4, 5])
    
    # --- 2. Phase-flip Syndromes (X-stabilizers) ---
    # Ancilla qubits q15 ~ q16, classical bits c6 ~ c7
    
    # Initialize ancilla qubits to |+> state
    qc.h([15, 16])
    
    # S6 (c6) = X0*X1*X2 * X3*X4*X5 (ancilla q15)
    qc.cx(0, 15)
    qc.cx(1, 15)
    qc.cx(2, 15)
    qc.cx(3, 15)
    qc.cx(4, 15)
    qc.cx(5, 15)
    
    # S7 (c7) = X3*X4*X5 * X6*X7*X8 (ancilla q16)
    qc.cx(3, 16)
    qc.cx(4, 16)
    qc.cx(5, 16)
    qc.cx(6, 16)
    qc.cx(7, 16)
    qc.cx(8, 16)
    
    # Apply Hadamard again to complete X measurement
    qc.h([15, 16])
    
    # Measure Phase-flip syndromes (q15-q16 -> c6-c7)
    qc.measure([15, 16], [6, 7])

    return

