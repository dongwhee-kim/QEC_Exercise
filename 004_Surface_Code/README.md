# Regular Surface Code

# Objective
- Understand the Regular Surface Code, a topological error correction code that uses a two-dimensional lattice of qubits to encode logical qubits.
- It has a high error correction threshold and is considered one of the most promising techniques for large-scale, fault-tolerant quantum computing.
- The surface code is used by the [Azure Quantum Resource Estimator](https://learn.microsoft.com/en-us/azure/quantum/overview-resources-estimator#quantum-error-correction-schemes).

# Prerequisite
- Read the foundational paper for the Regular Surface Code **[1]**.

# To do
- Complete the code in the sections marked **Fill the code**.

# Getting Started
- $ python main.py

# Answer (Solution Folder)

# Hint
- 

# Additioanl Information
- The key difference is that the Steane code is a **block code**, where all 7 qubits are treated as a single, static block. The circuit you showed ($[[7, 1, 3]]$) nicely fits on one diagram.
- The surface code is a **topological code**. Its circuit is defined by its 2D grid layout and, most importantly, it's not a single "encode-detect-decode" circuit. Instead, it's a repeating cycle of measurements.
- IBM: Heavy hex lattice architecture
- Google: Surface Code

# References
- **[1]** Fowler, Austin G., et al. "Surface codes: Towards practical large-scale quantum computation." Physical Review A—Atomic, Molecular, and Optical Physics 86.3 (2012): 032324.
