# Background: Real-Time Quantum Error Correction

This document outlines the fundamental architecture and timing constraints of real-time Quantum Error Correction (QEC).

**Specifically focusing on Surface Codes implemented on superconducting (IBM, Google) qubit systems.**

# 1. What is QEC? Why is it needed?

![IBM_Quantum_Development_Roadmap](images/IBM_Quantum_Development_Roadmap.webp)
**Source: [IBM Quantum Roadmap 2025](https://www.ibm.com/quantum/blog/ibm-quantum-roadmap-2025)**

## Past -> Current (2025, Quantum Error Mitigation) -> Future (Quantum Error Correction)

Quantum information is fragile. Without intervention, environmental noise destroys quantum states (decoherence).

**Quantum Error Characterization**
- **Gate Error**: A deviation from the ideal quantum gate operation, causing incorrect quantum states due to noise or other imperfections. Error-rates typically in the range of **0.1-1%**.
- **Decoherence Error**: Occurs when a quantum system interacts with its environment, causing the loss of quantum information stored in superposition or entanglement. It is typically characterized by two time constants, **$T_1$ (Relaxation)** and **$T_2$ (Dephasing)** times.
- **Measurement Error**: The discrepancy between the actual quantum state and the classical outcome obtained after measurement. This includes errors from state projection failure or detector inefficiencies. State $$|1\rangle$$ more prone to errors than state $$|0\rangle$$. Error-rates typically in the range of **1-4%**.
- **Correlated Error**: Errors that affect multiple qubits simultaneously or where an error on one qubit is dependent on the state or operation of another. These errors violate the standard assumption that errors occur independently.
 1) **Spectator Error**: Errors induced on a qubit (the spectator) that is not currently being operated on, often caused by the interaction with neighboring qubits undergoing gate operations.
 2) **Crosstalk Error**: Unintended coupling between qubits or control lines, where a signal intended for one qubit affects another (e.g., driving Qubit A inadvertently rotates Qubit B).
- **Leakage Error (Not a Pauli Error)**: A type of error where the qubit transitions out of the computational subspace (states $|0\rangle$ and $|1\rangle$) into **higher energy levels (e.g., $|2\rangle$)**, rendering standard quantum error correction protocols ineffective without specific leakage reduction techniques (e.g., Leakage Reduction Circuit (LRC)).

To build useful quantum computers, we must distinctively handle errors in three ways:

**Quantum Error Suppression**
- Attempts to prevent errors before they happen.
- Quantum hardware is designed to be more resistant to noise.
- Focuses on hardware-level noise reduction.
- The most basic level of handling errors.

**Quantum Error Mitigation (used in NISQ era)**
- Attempts to reduce the effect of errors after they happen.
- Runs quantum circuits multiple times to estimate the error-free outcome.
- Focuses on post-processing.
- Useful for today's noisy quantum devices.
- E.g., Zero-noise extrapolation, Probabilistic error cancellation, Quasi-probability method, Virtual distillation method, Subspace expansion method.

**Quantum Error Correction (QEC, required for FTQC)**
- Attempts to detect and fix errors as they occur.
- Spreads a qubit's value across multiple physical qubits for redundancy.
- Focuses on real-time error detection and correction.
- More complex but necessary for fault-tolerant quantum computing.

# 2. QEC Overview & Timing Constraints
## Figure 1. 
## Figure A horizontal timeline bar representing 1µs (1000ns). Color-code the sections: [Readout] -> [Tx] -> [Decoding] -> [Feedback] -> [Frame Update]. Mark "1µs" clearly as the Deadline.

In superconducting systems, the QEC loop is a strict race against time. The system must detect and handle errors before the next batch of errors arrives.

**The 1µs Hardware Constraint**
- The syndrome extraction circuit on processors like Google Sycamore takes approximately **1µs** **[1, 2]**. If decoding takes longer than this, errors accumulate (backlog), causing the system to fail.

**The QEC Cycle (1µs Timeline)**
A single QEC Round consists of the following mandatory steps within the 1000ns budget:
- Readout & State Discrimination (300ns - 500ns): The FPGA converts analog microwave signals from the QPU into digital bits (0 or 1).
- Transmission (tens of ns): Sending syndrome data from FPGA to the Decoder.
- Decoding (200ns - 400ns): The Decoder calculates the error location using algorithms like MWPM (Minimum Weight Perfect Matching) or Union-Find.
- Feedback Transmission: Sending correction data (2 bits per data qubit) back to the FPGA.
- Frame Update: The FPGA updates the Pauli Frame record.



# References
**[1]** Google Quantum AI. 2021. Exponential suppression of bit or phase errors with cyclic error correction. Nature 595, 7867 (2021), 383. https://doi.org/10.1038/ s41586-021-03588-y
**[2]** Google Quantum AI. Accessed: June 19, 2021. Quantum Computer Datasheet. https://quantumai.google/hardware/datasheet/weber.pdf.
**[3]**




**[1]** Das, Poulami, Aditya Locharla, and Cody Jones. "Lilliput: a lightweight low-latency lookup-table decoder for near-term quantum error correction." Proceedings of the 27th ACM International Conference on Architectural Support for Programming Languages and Operating Systems. 2022.

**[2]** Vittal, Suhas, Poulami Das, and Moinuddin Qureshi. "Astrea: Accurate quantum error-decoding via practical minimum-weight perfect-matching." Proceedings of the 50th Annual International Symposium on Computer Architecture. 2023.

**[3]** Ryan-Anderson, Ciaran, et al. "Realization of real-time fault-tolerant quantum error correction." Physical Review X 11.4 (2021): 041058.

**[4]** "Suppressing quantum errors by scaling a surface code logical qubit." Nature 614, no. 7949 (2023): 676-681.

**[5]** Paler, Alexandru, et al. "Software-based pauli tracking in fault-tolerant quantum circuits." 2014 Design, Automation & Test in Europe Conference & Exhibition (DATE). IEEE, 2014.

**[6]** Chamberland, Christopher, Pavithran Iyer, and David Poulin. "Fault-tolerant quantum computing in the Pauli or Clifford frame with slow error diagnostics." Quantum 2 (2018): 43.

**[7]** Knill, Emanuel. "Quantum computing with realistically noisy devices." Nature 434.7029 (2005): 39-44.
