# Stim - Inspection Surface Code Structure

This project generates and inspects the structure of an ideal (noise-free) rotated surface code circuit using Google's Stim library.

# Contents [ideal_surface_code.stim]

The generated `.stim` file contains the full definition of a quantum error correction circuit. Its key components include:

- **QUBIT_COORDS**: Defines the 2D layout coordinates for each physical qubit, used for visualization.
- **R / RX (Reset)**: Initializes qubits into a specific state ($|0\rangle$ or $|+\rangle$).
- **TICK**: Represents a time step barrier. Operations between two TICKs are executed in parallel.
- **H / CX (Gates)**: Clifford gates (Hadamard and CNOT) used for syndrome extraction cycles.
- **M (Measure)**: Physical measurement of qubits at the end of a round or for syndrome extraction.
- **DETECTOR**: Defines parity constraints between measurement outcomes. In an ideal circuit, these help verify the stabilizer structure.
- **OBSERVABLE_INCLUDE**: Defines the logical observable (Logical X) for the memory experiment.

# Getting Started
- $ python Stim_Structure.py