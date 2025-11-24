from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from collections import Counter
from qiskit.circuit import Gate
import sys

def error_correction_func (qc, error_type='X'):
    # QuantumCircuit(5,3)
    # 3bit classical register -> c[0] = c0, c[1] = c1, c[2] = final result (q0)
    c = qc.cregs[0]

    if error_type=='X':
        ######################################
        ######################################


        ############# Fill the code ##########


        ######################################
        ######################################
    elif error_type=='Z':
        ######################################
        ######################################


        ############# Fill the code ##########


        ######################################
        ######################################
    else:
        print("Wrong Error Type")
        sys.exit(1)

    return