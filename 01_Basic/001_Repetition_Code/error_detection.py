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