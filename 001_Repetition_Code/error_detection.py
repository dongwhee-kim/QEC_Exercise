from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from collections import Counter
from qiskit.circuit import Gate
import sys

# Can't get syndrome value now
# Why? Qiskit seperates (1) circuit build and (2) circuit run phases.
# The 'error_detection_func' is part of the (1) circuit build phase. Just add measurements
# The measurement (syndrome) can only be obtained after this function completes
# and the entire circuit is run on a simulator or actual device (2).

def error_detection_func (qc, error_type='X'):

    if error_type=='X':
        # S0 = Z0 Z1
        qc.cx(0,3)
        qc.cx(1,3)

        # S1 = Z1 Z2
        qc.cx(1,4)
        qc.cx(2,4)

        qc.measure(3,0) # c0
        qc.measure(4,1) # c1

    elif error_type=='Z':
        qc.h([3, 4]) # applying hadamard gate on q3, q4
        # S0 = X0 X1
        qc.cx(0,3)
        qc.cx(1,3)

        # S1 = X1 X2
        qc.cx(1,4)
        qc.cx(2,4)

        qc.h([3, 4]) # applying hadamard gate on q3, q4

        qc.measure(3,0) # c0
        qc.measure(4,1) # c1

    else:
        print("Wrong Error Type")
        sys.exit(1)

    return