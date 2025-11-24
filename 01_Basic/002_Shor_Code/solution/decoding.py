from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

# Inverse of the encoding function
def decoding_func(qc): 
    # 1. Inner code decoding (Phase-flip decoding)
    # Decode |+++> -> |+> and |---> -> |->
    # Block 1: q0, q1, q2
    qc.cx(0, 2)
    qc.cx(0, 1)
    
    # Block 2: q3, q4, q5
    qc.cx(3, 5)
    qc.cx(3, 4)
    
    # Block 3: q6, q7, q8
    qc.cx(6, 8)
    qc.cx(6, 7)
    
    # Change basis from X to Z
    qc.h([0, 3, 6])

    # 2. Outer code decoding (Bit-flip decoding)
    # Decode a|000> + b|111> -> a|0> + b|1> (on q0, q3, q6)
    qc.cx(0, 6)
    qc.cx(0, 3)
    
    # Final logical state is restored to q0