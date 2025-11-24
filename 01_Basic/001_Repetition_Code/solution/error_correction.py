from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from collections import Counter
from qiskit.circuit import Gate
import sys

def error_correction_func (qc, error_type='X'):
    # QuantumCircuit(5,3)
    # 3bit classical register -> c[0] = c0, c[1] = c1, c[2] = final result (q0)
    c = qc.cregs[0]

    if error_type=='X':
        with qc.if_test((c,1)): qc.x(0) # syndrome 01
        with qc.if_test((c,3)): qc.x(1) # syndrome 11
        with qc.if_test((c,2)): qc.x(2) # syndrome 10
    elif error_type=='Z':
        with qc.if_test((c,1)): qc.z(0) # syndrome 01
        with qc.if_test((c,3)): qc.z(1) # syndrome 11
        with qc.if_test((c,2)): qc.z(2) # syndrome 10
    else:
        print("Wrong Error Type")
        sys.exit(1)

    return