# circuit_builder.py
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import layout

# Creates the Qiskit circuit for one round of syndrome extraction
def create_syndrome_round():
    # Initialize registers based on layout.py definitions
    data_qr = QuantumRegister(layout.NUM_DATA_QUBITS, name='d')
    x_ancilla_qr = QuantumRegister(layout.NUM_X_ANCILLAS, name='cx')
    z_ancilla_qr = QuantumRegister(layout.NUM_Z_ANCILLAS, name='cz')
    
    # Classical registers for ancilla measurement
    x_ancilla_cr = ClassicalRegister(layout.NUM_X_ANCILLAS, name='crx')
    z_ancilla_cr = ClassicalRegister(layout.NUM_Z_ANCILLAS, name='crz')
    
    qc = QuantumCircuit(data_qr, x_ancilla_qr, z_ancilla_qr, 
                        x_ancilla_cr, z_ancilla_cr)

    # --- X-Stabilizer Measurement (XX) ---
    # Detect Phase flip (Z) error
    qc.h(x_ancilla_qr[0]) # c_x[0]
    qc.h(x_ancilla_qr[1]) # c_x[1]
    qc.h(x_ancilla_qr[2]) # c_x[2]
    qc.h(x_ancilla_qr[3]) # c_x[3]
    qc.h(x_ancilla_qr[4]) # c_x[4]
    qc.h(x_ancilla_qr[5]) # c_x[5]

    qc.cx(x_ancilla_qr[0], data_qr[0]) # (c_x[0] -> d[0])
    qc.cx(x_ancilla_qr[0], data_qr[3]) # (c_x[0] -> d[3])
    qc.cx(x_ancilla_qr[0], data_qr[5]) # (c_x[0] -> d[5])

    qc.cx(x_ancilla_qr[1], data_qr[1])
    qc.cx(x_ancilla_qr[1], data_qr[3])
    qc.cx(x_ancilla_qr[1], data_qr[4])
    qc.cx(x_ancilla_qr[1], data_qr[6])

    qc.cx(x_ancilla_qr[2], data_qr[2])
    qc.cx(x_ancilla_qr[2], data_qr[4])
    qc.cx(x_ancilla_qr[2], data_qr[7])

    qc.cx(x_ancilla_qr[3], data_qr[5])
    qc.cx(x_ancilla_qr[3], data_qr[8])
    qc.cx(x_ancilla_qr[3], data_qr[10])

    qc.cx(x_ancilla_qr[4], data_qr[6])
    qc.cx(x_ancilla_qr[4], data_qr[8])
    qc.cx(x_ancilla_qr[4], data_qr[9])
    qc.cx(x_ancilla_qr[4], data_qr[11])

    qc.cx(x_ancilla_qr[5], data_qr[7])
    qc.cx(x_ancilla_qr[5], data_qr[9])
    qc.cx(x_ancilla_qr[5], data_qr[12])

    qc.h(x_ancilla_qr[0]) # c_x[0]
    qc.h(x_ancilla_qr[1]) # c_x[1]
    qc.h(x_ancilla_qr[2]) # c_x[2]
    qc.h(x_ancilla_qr[3]) # c_x[3]
    qc.h(x_ancilla_qr[4]) # c_x[4]
    qc.h(x_ancilla_qr[5]) # c_x[5]
    
    qc.barrier()

    # --- Z-Stabilizer Measurement (ZZ) ---
    # Detect Bit flip (X) error
    qc.cx(data_qr[0],z_ancilla_qr[0]) # d[0] -> c_z[0]
    qc.cx(data_qr[1],z_ancilla_qr[0]) # d[1] -> c_z[0]
    qc.cx(data_qr[3],z_ancilla_qr[0]) # d[3] -> c_z[0]

    qc.cx(data_qr[1],z_ancilla_qr[1])
    qc.cx(data_qr[2],z_ancilla_qr[1])
    qc.cx(data_qr[4],z_ancilla_qr[1])

    qc.cx(data_qr[3],z_ancilla_qr[2])
    qc.cx(data_qr[5],z_ancilla_qr[2])
    qc.cx(data_qr[6],z_ancilla_qr[2])
    qc.cx(data_qr[8],z_ancilla_qr[2])

    qc.cx(data_qr[4],z_ancilla_qr[3])
    qc.cx(data_qr[6],z_ancilla_qr[3])
    qc.cx(data_qr[7],z_ancilla_qr[3])
    qc.cx(data_qr[9],z_ancilla_qr[3])

    qc.cx(data_qr[8],z_ancilla_qr[4])
    qc.cx(data_qr[10],z_ancilla_qr[4])
    qc.cx(data_qr[11],z_ancilla_qr[4])

    qc.cx(data_qr[9],z_ancilla_qr[5])
    qc.cx(data_qr[11],z_ancilla_qr[5])
    qc.cx(data_qr[12],z_ancilla_qr[5])

    qc.barrier()

    # --- Ancilla Measurement ---
    qc.measure(x_ancilla_qr, x_ancilla_cr) # ZZ
    qc.measure(z_ancilla_qr, z_ancilla_cr) # XX
    
    return qc