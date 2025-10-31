from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit

# 1. Get a backend to simulate (using a fake backend is faster)
# To use a real backend, get it via IBMProvider()
backend = FakeManilaV2()

# 2. From the backend's calibration data (T1, T2, gate error rates, measurement error rates),
#    automatically create a noise model.
noise_model = NoiseModel.from_backend(backend)

print(f"Errors included in the noise model: {noise_model.basis_gates}")

# 3. Create an AerSimulator and specify the noise_model.
simulator = AerSimulator(noise_model=noise_model)

# 4. We assume a circuit (qc) is created here.
# (As a random example, we create a Bell state circuit)
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

print("\n--- Generated Test Circuit (Bell State) ---")
print(qc.draw())
print("-------------------------------------\n")


# 5. Run the simulation.
# Aer will automatically apply the errors from the noise_model
# to all gates, measurements, and idle times in the circuit.
result = simulator.run(qc, shots=1000).result()
counts = result.get_counts()

print("--- Noise Simulation Result (Counts) ---")
print(counts)
print("-------------------------------------")