from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# Syndrome Measurement
def syndrome_extraction_func(qc, round_idx):
    d = next(reg for reg in qc.qregs if reg.name == 'd')
    cz = next(reg for reg in qc.qregs if reg.name == 'cz')
    cx = next(reg for reg in qc.qregs if reg.name == 'cx')
    sz = next(reg for reg in qc.cregs if reg.name == 'sz')
    sx = next(reg for reg in qc.cregs if reg.name == 'sx')
    res = next(reg for reg in qc.cregs if reg.name == 'res')

    # --- X-Stabilizer Measurement (XX) ---
    # Detect Phase flip (Z) error
    qc.h(cx[0]) # c_x[0]
    qc.h(cx[1]) # c_x[1]
    qc.h(cx[2]) # c_x[2]
    qc.h(cx[3]) # c_x[3]
    qc.h(cx[4]) # c_x[4]
    qc.h(cx[5]) # c_x[5]

    qc.cx(cx[0], d[0]) # (c_x[0] -> d[0])
    qc.cx(cx[0], d[3]) # (c_x[0] -> d[3])
    qc.cx(cx[0], d[5]) # (c_x[0] -> d[5])

    qc.cx(cx[1], d[1])
    qc.cx(cx[1], d[3])
    qc.cx(cx[1], d[4])
    qc.cx(cx[1], d[6])

    qc.cx(cx[2], d[2])
    qc.cx(cx[2], d[4])
    qc.cx(cx[2], d[7])

    qc.cx(cx[3], d[5])
    qc.cx(cx[3], d[8])
    qc.cx(cx[3], d[10])

    qc.cx(cx[4], d[6])
    qc.cx(cx[4], d[8])
    qc.cx(cx[4], d[9])
    qc.cx(cx[4], d[11])

    qc.cx(cx[5], d[7])
    qc.cx(cx[5], d[9])
    qc.cx(cx[5], d[12])

    qc.h(cx[0]) # c_x[0]
    qc.h(cx[1]) # c_x[1]
    qc.h(cx[2]) # c_x[2]
    qc.h(cx[3]) # c_x[3]
    qc.h(cx[4]) # c_x[4]
    qc.h(cx[5]) # c_x[5]
    
    qc.barrier()

    # --- Z-Stabilizer Measurement (ZZ) ---
    # Detect Bit flip (X) error
    qc.cx(d[0],cz[0]) # d[0] -> cz[0]
    qc.cx(d[1],cz[0]) # d[1] -> cz[0]
    qc.cx(d[3],cz[0]) # d[3] -> cz[0]

    qc.cx(d[1],cz[1])
    qc.cx(d[2],cz[1])
    qc.cx(d[4],cz[1])

    qc.cx(d[3],cz[2])
    qc.cx(d[5],cz[2])
    qc.cx(d[6],cz[2])
    qc.cx(d[8],cz[2])

    qc.cx(d[4],cz[3])
    qc.cx(d[6],cz[3])
    qc.cx(d[7],cz[3])
    qc.cx(d[9],cz[3])

    qc.cx(d[8],cz[4])
    qc.cx(d[10],cz[4])
    qc.cx(d[11],cz[4])

    qc.cx(d[9],cz[5])
    qc.cx(d[11],cz[5])
    qc.cx(d[12],cz[5])

    qc.barrier()

    # --- Ancilla Measurement ---
    if round_idx==0:
        qc.measure(cx, sx[0:6]) # XX (0, 1, 2, 3, 4, 5)
        qc.measure(cz, sz[0:6]) # ZZ (0, 1, 2, 3, 4, 5)
        qc.reset(cx)
        qc.reset(cz)
    elif round_idx==1:
        qc.measure(cx, sx[6:12]) # XX (6, 7, 8, 9, 10, 11)
        qc.measure(cz, sz[6:12]) # ZZ (6, 7, 8, 9, 10, 11)
        qc.reset(cx)
        qc.reset(cz)
    else: # final round
        qc.measure(cx, sx[12:18]) # XX
        qc.measure(cz, sz[12:18]) # ZZ
        qc.reset(cx)
        qc.reset(cz)
    
    return