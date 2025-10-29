from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

# Inverse of the encoding function
def decoding_func(qc):
    """
    Applies the inverse of the encoding circuit to disentangle the
    logical state back onto q[0].
    """
    
    # Apply gates in reverse order of encoding
    qc.h(3)
    qc.h(5)
    qc.h(6)

    qc.cx(2, 6)
    qc.cx(2, 5)
    qc.cx(2, 4)
    
    qc.cx(1, 6)
    qc.cx(1, 4)
    qc.cx(1, 3)
    
    qc.cx(0, 6)
    qc.cx(0, 5)
    qc.cx(0, 3)

    qc.h(3)
    qc.h(5)
    qc.h(6)
    
    return