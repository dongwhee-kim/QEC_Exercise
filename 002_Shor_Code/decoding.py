from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

def decoding_func(qc):
    """
    Shor code decoding function
    Inverse of the encoding function
    """
    
    # 1. Inner code decoding (Bit-flip decoding)
    # Block 1: q0, q1, q2
    qc.cx(0, 2)
    qc.cx(0, 1)
    
    # Block 2: q3, q4, q5
    qc.cx(3, 5)
    qc.cx(3, 4)
    
    # Block 3: q6, q7, q8
    qc.cx(6, 8)
    qc.cx(6, 7)
    
    # 2. Outer code decoding (Phase-flip decoding)
    qc.h([0, 3, 6])
    
    qc.cx(0, 6)
    qc.cx(0, 3)

