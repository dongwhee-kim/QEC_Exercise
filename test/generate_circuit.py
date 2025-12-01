from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def generate_circuit_func():
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

    # Register
    # 13 Data Qubits
    d = QuantumRegister(13, 'd')
    # 6 Z-ancilla Qubits
    cz = QuantumRegister(6, 'cz')
    # 6 X-ancilla Qubits
    cx = QuantumRegister(6, 'cx')

    # 13 Data Qubit measurement results
    res = ClassicalRegister(13, 'res')
    # 3 round x 6 Z-syndrome bits
    sz = ClassicalRegister(18, 'sz')
    # 3 round x 6 X-syndrome bits
    sx = ClassicalRegister(18, 'sx')

    qc = QuantumCircuit(d, cz, cx, res, sz, sx)

    return qc