from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from collections import Counter
from qiskit.circuit import Gate
import sys

def error_correction_func (qc, syndrome_value, error_type='X'):

    if error_type=='X':
        qc.cx(0,1)
        qc.cx(0,2)
    elif error_type=='Z':
        qc.cx(0,1)
        qc.cx(0,2)
        qc.h([0, 1, 2]) # applying hadamard gate on q0, q1, q2
    else:
        print("Wrong Error Type")
        sys.exit(1)

    return