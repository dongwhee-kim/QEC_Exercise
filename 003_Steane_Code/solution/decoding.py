from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

# Inverse of the encoding function
def decoding_func(qc):
    qc.cx(4,1)
    qc.cx(4,2)
    qc.cx(4,3)

    qc.cx(5,0)
    qc.cx(5,2)
    qc.cx(5,3)

    qc.cx(6,0)
    qc.cx(6,1)
    qc.cx(6,3)
    
    qc.cx(0,1)
    qc.cx(0,2)
    
    qc.h(4)
    qc.h(5)
    qc.h(6)

    return