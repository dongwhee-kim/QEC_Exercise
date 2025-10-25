from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from collections import Counter
from qiskit.circuit import Gate
import sys

def decoding_func (qc, error_type='X'):
    if error_type=='X':
        qc.cx(0,2)
        qc.cx(0,1)
    elif error_type=='Z':
        qc.h([0, 1, 2]) # applying hadamard gate on q0, q1, q2
        qc.cx(0,2)
        qc.cx(0,1)
    else:
        print("Wrong Error Type")
        sys.exit(1)

    return qc