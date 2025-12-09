# QLDPC Code ([[144, 12, 12]] BB Code)

# Objective
- Understand the **Quantum Low-Density Parity Check (QLDPC) Code**, which requires a **fewer physical qubits** than Surface Code.
- Perform **Monte-Carlo Simulation**: Analyze the **threshold** by plotting the **Logical Error Rate (LER)** against the **Physical Error Rate (p)**.
- Compare the LER and physical qubit resource requirements against Surface Codes.

# Overview
![BB_Code](images/BB_Code.png)

# Configuration
- **QEC Code**: [[144, 12, 12]] Bivariate Bicycle (BB) Code **[5]** (also known as Gross Code).
- **Decoder**: BP-OSD (Belief Propagation + Ordered Statistics Decoding) **[3]**
- **Error Correction Capability**: Distance $d=12$. Guarantees correction of any weight $\lfloor (d-1)/2 \rfloor = 5$ errors. (Simulation performance may vary).
- **Shots**: $10^6$
- **# of data qubits**: 144
- **# of ancilla qubits**: 144 (72 X-checks, 72 Z-checks)
- **# of logical qubits**: 12 (Note: A Surface Code uses similar resources to encode only 1 logical qubit).

# Getting Started
- $ python main.py

# Answer (gross_code_ler_stim.png)

# Additioanl Information (History)
- Origins: QLDPC codes are derived from classical Low-Density Parity Check (LDPC) codes **[1]**.
- Early Decoding: Initially, QLDPC codes (e.g., Toric Code **[4]**) attempted to utilize Belief Propagation (BP) as a decoding method **[2]**, similar to classical inference engines **[6]**.
- The Challenge: Standard BP struggles with quantum codes due to degeneracy (multiple errors corresponding to the same syndrome) and short cycles (loops in the Tanner graph) which prevent convergence.
- The Solution: To address these convergence issues, Ordered Statistics Decoding (OSD) **[7]** was combined with BP as a post-processing step.
- Current Standard: This led to the development of the BP-OSD decoder **[3]**, which provides high-performance decoding for finite-length QLDPC codes.

# References
- **[1]** Gallager, R. G., "Low-density parity-check codes," IRE Transactions on Information Theory, Vol. 8, No. 1, pp. 21–28, 1962.
- **[2]** Poulin, D. and Chung, Y., "On the iterative decoding of sparse quantum codes," Quantum Information & Computation, Vol. 8, No. 10, pp. 987–1000, 2008.
- **[3]** Panteleev, Pavel, and Gleb Kalachev. "Degenerate quantum LDPC codes with good finite length performance." Quantum 5 (2021): 585.
- **[4]** Kitaev, A. Yu. "Fault-tolerant quantum computation by anyons." Annals of physics 303.1 (2003): 2-30.
- **[5]** Bravyi, Sergey, et al. "High-threshold and low-overhead fault-tolerant quantum memory." Nature 627.8005 (2024): 778-782.
- **[6]** J. Pearl, "Reverend Bayes on inference engines: A distributed hierarchical approach," in Proceedings of the Second National Conference on Artificial Intelligence (AAAI-82), Pittsburgh, PA, 1982, pp. 133–136.
- **[7]** Fossorier, Marc PC, and Shu Lin. "Soft-decision decoding of linear block codes based on ordered statistics." IEEE Transactions on information Theory 41.5 (1995): 1379-1396.