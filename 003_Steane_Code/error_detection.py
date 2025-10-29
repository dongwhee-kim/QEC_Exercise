from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

def error_detection_func(qc):
    """
    Measures the 6 stabilizers of the Steane code.
    - Z-error syndrome (from X-stabilizers g1, g2, g3) is measured into c[0], c[1], c[2]
    - X-error syndrome (from Z-stabilizers g4, g5, g6) is measured into c[3], c[4], c[5]
    
    Uses ancilla qubits q[7]...q[12].
    
    Stabilizers (matching correction logic):
    g1 = X0 X3 X5 X6
    g2 = X1 X3 X4 X6
    g3 = X2 X4 X5 X6
    
    g4 = Z0 Z3 Z5 Z6
    g5 = Z1 Z3 Z4 Z6
    g6 = Z2 Z4 Z5 Z6
    """
    
    # --- Z-Error Syndrome Measurement (X-Stabilizers) ---
    # Ancillas: q[7] -> g1, q[8] -> g2, q[9] -> g3
    # Syndrome Bits: c[0] <- g1, c[1] <- g2, c[2] <- g3
    
    qc.h([7, 8, 9])
    
    # g1 = X0 X3 X5 X6
    qc.cx(0, 7)
    qc.cx(3, 7)
    qc.cx(5, 7)
    qc.cx(6, 7)
    
    # g2 = X1 X3 X4 X6
    qc.cx(1, 8)
    qc.cx(3, 8)
    qc.cx(4, 8)
    qc.cx(6, 8)
    
    # g3 = X2 X4 X5 X6
    qc.cx(2, 9)
    qc.cx(4, 9)
    qc.cx(5, 9)
    qc.cx(6, 9)

    qc.h([7, 8, 9])
    
    qc.measure(7, 0) # g1 syndrome
    qc.measure(8, 1) # g2 syndrome
    qc.measure(9, 2) # g3 syndrome

    # --- X-Error Syndrome Measurement (Z-Stabilizers) ---
    # Ancillas: q[10] -> g4, q[11] -> g5, q[12] -> g6
    # Syndrome Bits: c[3] <- g4, c[4] <- g5, c[5] <- g6
    
    # Ancillas are already in |0> state, no H gates needed
    
    # g4 = Z0 Z3 Z5 Z6
    qc.cx(0, 10)
    qc.cx(3, 10)
    qc.cx(5, 10)
    qc.cx(6, 10)
    
    # g5 = Z1 Z3 Z4 Z6
    qc.cx(1, 11)
    qc.cx(3, 11)
    qc.cx(4, 11)
    qc.cx(6, 11)
    
    # g6 = Z2 Z4 Z5 Z6
    qc.cx(2, 12)
    qc.cx(4, 12)
    qc.cx(5, 12)
    qc.cx(6, 12)
    
    qc.measure(10, 3) # g4 syndrome
    qc.measure(11, 4) # g5 syndrome
    qc.measure(12, 5) # g6 syndrome
    
    return