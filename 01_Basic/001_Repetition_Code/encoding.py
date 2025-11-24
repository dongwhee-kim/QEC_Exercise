from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from collections import Counter
from qiskit.circuit import Gate
import sys

# Physical qubit: |φ> = a|0> + b|1>
# Logical qubit (X Error): |φL> = a|0L>+b|1L> = a|000>+b|111>
# Logical qubit (Z Error): |φL> = a|0L>+b|1L> = a|+++>+b|--->
# Make qubits into entanglement state (e.g., Bell-State, GHZ)
def encoding_func(error_type='X'):
    qc = QuantumCircuit(5, 3) # input: 5, output: 3
    qc.x(0) # initial value: q0 = |1>

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

    return qc