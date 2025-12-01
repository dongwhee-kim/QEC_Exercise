from qiskit import QuantumCircuit
import sys

def result_report_func(qc):
    d = next(reg for reg in qc.qregs if reg.name == 'd')
    cz = next(reg for reg in qc.qregs if reg.name == 'cz')
    cx = next(reg for reg in qc.qregs if reg.name == 'cx')
    sz = next(reg for reg in qc.cregs if reg.name == 'sz')
    sx = next(reg for reg in qc.cregs if reg.name == 'sx')
    res = next(reg for reg in qc.cregs if reg.name == 'res')

    qc.measure(d, res)

    return
