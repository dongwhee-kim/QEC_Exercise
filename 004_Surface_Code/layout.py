# layout.py
"""
Defines the layout for the d=3 Surface Code
"""

d = 3
NUM_DATA_QUBITS = 13
NUM_X_ANCILLAS = 6
NUM_Z_ANCILLAS = 6

# Z-stabilizers (Ancilla -> Data Qubits)
z_stabilizers = {
    'c_z[0]': ['d[0]', 'd[1]', 'd[3]'],
    'c_z[1]': ['d[1]', 'd[2]', 'd[4]'],
    'c_z[2]': ['d[3]', 'd[5]', 'd[6]', 'd[8]'],
    'c_z[3]': ['d[4]', 'd[6]', 'd[7]', 'd[9]'],
    'c_z[4]': ['d[8]', 'd[10]', 'd[11]'],
    'c_z[5]': ['d[9]', 'd[11]', 'd[12]']
}

# X-stabilizers (Ancilla -> Data Qubits)
x_stabilizers = {
    'c_x[0]': ['d[0]', 'd[3]', 'd[5]'],
    'c_x[1]': ['d[1]', 'd[3]', 'd[4]', 'd[6]'],
    'c_x[2]': ['d[2]', 'd[4]', 'd[7]'],
    'c_x[3]': ['d[5]', 'd[8]', 'd[10]'],
    'c_x[4]': ['d[6]', 'd[8]', 'd[9]', 'd[11]'],
    'c_x[5]': ['d[7]', 'd[9]', 'd[12]']
}

# Optional: Maps for easy qubit indexing
# data_map = {'d[0]': 0, 'd[1]': 1, ...}
# ancilla_map = {'c_z[0]': 13, ...}
