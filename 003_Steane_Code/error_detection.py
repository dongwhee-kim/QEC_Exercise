from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

# Measures the 6 stabilizers of the Steane code
def error_detection_func(qc):
    # --- X-Error Syndrome Measurement (ZZ) ---
    
    # c0 = Z0 Z2 Z4 Z6
    qc.cx(0, 7)
    qc.cx(2, 7)
    qc.cx(4, 7)
    qc.cx(6, 7)
    
    # c1 = Z1 Z2 Z5 Z6
    qc.cx(1, 8)
    qc.cx(2, 8)
    qc.cx(5, 8)
    qc.cx(6, 8)
    
    # c2 = Z3 Z4 Z5 Z6
    qc.cx(3, 9)
    qc.cx(4, 9)
    qc.cx(5, 9)
    qc.cx(6, 9)
    
    qc.measure(7, 0) # c0 syndrome
    qc.measure(8, 1) # c1 syndrome
    qc.measure(9, 2) # c2 syndrome

    # --- Z-Error Syndrome Measurement (XX) ---
    qc.h([10, 11, 12])
    
    # c3 = X0 X2 X4 X6
    qc.cx(10, 0)
    qc.cx(10, 2)
    qc.cx(10, 4)
    qc.cx(10, 6)
    
    # c4 = X1 X2 X5 X6
    qc.cx(11, 1)
    qc.cx(11, 2)
    qc.cx(11, 5)
    qc.cx(11, 6)
    
    # c5 = X3 X4 X5 X6
    qc.cx(12, 3)
    qc.cx(12, 4)
    qc.cx(12, 5)
    qc.cx(12, 6)

    qc.h([10, 11, 12])
    
    qc.measure(10, 3) # c3 syndrome
    qc.measure(11, 4) # c4 syndrome
    qc.measure(12, 5) # c5 syndrome
    
    return