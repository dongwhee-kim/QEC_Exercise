# Lattice Surgery

[Introducing Lattice Surgery](https://pennylane.ai/demos/tutorial_lattice_surgery)

# Issues of Quantum Computing
- Scalability
- Fast Decoding
- Syndrome Extraction Fidelity
- Low Non-clifford operation overhead (Magic State Distillation is essential!!)

# Pauli-Based Computation (PBC)
- A framework to facilitate the mapping of quantum programs to surface codes.
- Conversion (Final Result): Quantum program (including **non-clifford gates**) -> Sequence consisting of **only pauli product measurements (PPMs) [1]**
- **Conclusion: PPMs are sufficient for universal computing**
- The Compilation Process
![PBC Compilation Overview](https://blog-assets.cloud.pennylane.ai/compilations/pauli-based-computation/overview.png?w=828)
    - 🟧 **Clifford operators (angles $\pm\pi/4$)**: All such operators can be commuted to the right of the circuit and merged with PPMs. **Do not need to be executed on Hardware**.
    - 🟨 **T-gates / Non-Clifford operators (angles $\pm\pi/8$)**: All such operators can be realized with a magic state injection, leaving only classically controlled Clifford and Pauli operators that can be merged into PPMs again.
    - 🟦 **Blue boxes:** Terminal measurements at the very end of the circuit.
    - 1) **Input: Circuit (Clifford + T)** -> Any circuit can always be approximated to arbitrary precision with the (Clifford + T) gate set.
    - 2) **Intermediate representation** -> Quantum circuits are represented by a small set of building blocks, namely Pauli product measurements (PPMs) $\langle P \rangle$ and Pauli product rotations (PPRs) $e^{-i\phi P}$. The angle $\phi$ dictates how they are processed:
        - **Step 1: Decomposition**: The original (Clifford + T) gates are uniformly decomposed into a mixed sequence of Clifford (🟧) and non-Clifford (🟨) operations
        - **Step 2: Commutation**: All tractable Clifford operations (🟧) are **commuted** (**pushed**) to the far right of the circuit, mathematically updating the Pauli axes of the remaining non-Clifford operations (🟨) as they pass through.
        - **Step 3: Absorption**: The clustered Clifford operations (🟧) physically disappear from the circuit as they are absorbed into the terminal measurements (🟦).
        - **Step 4: Magic State Injection**: The remaining non-Clifford operations (🟨) are replaced by **magic state injections**.
    - 3) **Final Result (Output):** All non-Clifford PPRs are completely transformed, leaving the entire circuit as a sequence consisting of **only Pauli Product Measurements (PPMs)**.
- **Magic state injection is essential**! Injection of magic states from auxiliary qubits is neede! **Otherwise, we obtain a circuit containing PPMs + non-clifford PPRs**.

> 🔲 **Pauli ($\pi/2$)**: **Do not need to be executed on Hardware**. Tracking **sign ($\pm$) flips** $\rightarrow$ Hardware measures in the **original basis**
> 🆚 
> 🟧 **Clifford ($\pi/4$)**: **Do not need to be executed on Hardware**. Tracking **basis change** $\rightarrow$ Hardware measures in the **rotated basis**

![Non_Clifford_Conversion_Clifford_Magic_State](images/Non_Clifford_Conversion_Clifford_Magic_State.png)
- Non-Clifford PPRs = Magic State + PPMs (Figure 7 of **[1]**)
- Magic State T$$|+\rangle$$ = $$|m\rangle = \frac{1}{\sqrt{2}} \left( |0\rangle + e^{i\pi/4}|1\rangle \right)$$

# Lattice Surgery [6]
- Why is it needed? To operate **transversal operations** on hardware even on **non-local physical connectivity**. (e.g., superconducting qubits -> local connectivity 하고만 상호작용 가능. 멀리 떨어진 non-local logical qubit 간에는 transversal operation 제약.)
    - 초창기 해결법: Braiding
        - surface code 일부에 detect을 뚫어서 encoding 했고, 여러 code들의 continuous deformation을 통해 non-local qubit간 transversal operation 시도.
        - Issue: Significantly more physical qubits are needed per logical qubit.
- It can enable error-corrected logical operations with significantly lower space overhead and comparable time requirements **[1, 6, 7]**.

![Lattice_Surgery_Merge_Split](images/Lattice_Surgery_Merge_Split.png)
- Fundamental operations - **Lattice Merging and Lattice Splitting (Figure 3 of [9])**
- 핵심: **"두 큐비트 (logical qubit) 패치 사이의 경계를 물리적으로 연결(Merge)하면, 그 사이에서 파울리 연산자의 고유값(결과값)을 읽어낼 수 있다."**

## 격자 수술(Lattice Surgery)만 할 줄 알면 왜 세상의 모든 양자 프로그램(범용 양자 컴퓨팅)을 다 돌릴 수 있는가?
- Top-down 설명: PPMs가능. 즉, All circuit -> Clifford + T (PPRs) circuit -> PPM + Magic State -> Only PPMs

Homological Measurement (위상학적 측정): "길을 측정하라"
논리적 큐비트를 측정할 때, 패치 안에 있는 수많은 물리적 큐비트를 전부 다 측정하는 것이 아닙니다.

핵심: 패치의 한쪽 경계(Edge)에서 반대쪽 경계까지 연결된 '측정 라인(String)' 하나만 찾아내어 측정하면 됩니다.

![Logical_X_Z_Operator](https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/logical_X_Z.png?w=828)

topological equivalence class (Homological measurement): 이 라인이 정확히 어떤 큐비트를 거쳐가는지는 중요하지 않습니다. 양쪽 끝을 연결만 하고 있다면, 어떤 경로를 선택하든 결과는 모두 동일한 논리적 정보를 담고 있습니다. 위상학적으로 동일.

Edge (Boundary) 이름,가지고 있는 아치(Arch) 타입,측정 시 얻는 결과 (Logical Operator)
Z-edge,X-arches (X-stabilizers),Logical Z (ZL​) -> |+> 로 초기화.
X-edge,Z-arches (Z-stabilizers),Logical X (XL​) -> |0> 으로 초기화.

## 예시 - Measuring XL 'x' XL (Merge & Split two logical qubits on their X edges)
![Logical_X_Z_Operator_Preparation](https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/XX1.png?w=828)
1단계: 준비 (Preparation / Initialization)배치: 두 패치의 X-edge가 마주 보게 정렬합니다. 그사이에는 비어있는(unused) 데이터 큐비트 열이 있습니다.초기화: 중간 데이터 큐비트들을 **$|0\rangle$** 상태로 초기화합니다.왜 $|0\rangle$인가요? $X_L \otimes X_L$을 측정한다는 것은, X-string(위상학적 선)을 잇는다는 뜻입니다. 중간 다리를 $|0\rangle$으로 채운다는 것은 그곳에 Z-basis의 정보(제약조건)를 심어놓는 것과 같습니다. 이 제약이 들어간 통로가 있어야 에러 정정 회로가 X-parity 정보를 엮어낼 수 있습니다.

![Logical_X_Z_Operator_Merging](https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/XX2.png?w=828)
2단계: 병합 (Merging)통합: 이제 에러 정정 주기(Stabilizer cycles)를 돌릴 때, 중간의 데이터 큐비트들을 에러 정정 연산(Stabilizer measurements)에 포함시킵니다.효과: 독립적이었던 두 개의 패치가 하나로 합쳐집니다. 이 통합된 패치 안에서 에러 정정을 계속 수행하면, 새로 합쳐진 경계면의 안정화 연산자들이 값을 내놓습니다. 이 안정화 연산자들의 총 곱(Product)이 곧 우리가 구하려는 $X_L \otimes X_L$의 값입니다. (Conveniently, the product of all stabilizers between the two logical XL operators, indicated by the red dots below, corresponds to the eigenvalue of XL 'x' XL)

![Logical_X_Z_Operator_Merging](https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/XX3.png?w=828)
Now that we retrieved our measurement result XL 'x' XL, we want to restore the two qubits, which is achieved by lattice splitting. This, on the other hand, is done by measuring the intermediate data qubits in the **Z basis**.

![Logical_X_Z_Operator_Splitting](https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/XX4.png?w=828)
3단계: 분리 (Splitting)복구: 정보(패리티)를 얻었으니, 이제 다시 두 개의 독립적인 큐비트로 돌려놓아야 합니다.측정: 합쳐질 때 사용했던 중간 데이터 큐비트들을 X-basis로 측정하여 다시 쪼갭니다.보정 (Correction): 분리하는 과정에서 발생한 측정값(Sign)이 있다면, 원래 두 큐비트의 정보에 이 값을 곱해 최종 결과를 확정합니다.

## Y measurements
- 왜 Y measurement가 어려운가? $X$와 $Z$를 동시에 측정해야 합니다. $X$와 $Z$ 측정 기저를 하나의 패치에 동시에 적용하려고 하면 안정화 연산자(Stabilizer)들과의 교환 법칙(Commutation)이 깨지게 됩니다. 시스템이 이를 '에러'로 인식하여 큐비트를 코드 공간 밖으로 튕겨내 버리기 때문에, 일반적인 방식으로는 측정이 불가능합니다.
$Y$ 측정이 문제를 일으키는 이유 -> ($XZ \neq ZX$)논리적 $Y$ 연산자는 수학적으로 $Y = iXZ$입니다. 즉, $X$ 연산과 $Z$ 연산을 동시에 수행한다는 뜻이죠.$X$만 측정할 때: $X$는 표면 부호의 $X$-안정화 연산자들과 다 교환(Commute)되도록 설계되어 있습니다. 그래서 $X$를 써도 시스템은 "오, 정상적인 논리 연산이네!"라고 넘어갑니다.$Z$만 측정할 때: $Z$ 역시 $Z$-안정화 연산자들과 다 교환(Commute)됩니다. 그래서 $Z$를 써도 시스템은 정상으로 봅니다.$X$와 $Z$를 동시에 측정할 때 ($Y$): * 파울리 연산자의 가장 유명한 성질은 **$XZ = -ZX$** (반교환, Anti-commute)입니다. $Y$를 측정하려고 $X$와 $Z$ 성분을 동시에 강제로 삽입하면, 패치 경계에 있는 안정화 연산자들과 $-1$의 부호 차이가 발생하게 됩니다.

X, Z 측정 방식: 단순한 경계면을 병합해 $X$ 또는 $Z$를 측정.
$Y$ 측정 방식: 1. 패치를 늘리고 엣지를 돌려서 트위스트(Twist) 결함을 만든다. (공간적 구조 변경) 2. 이 꼬인 상태를 보조 큐비트와 병합한다(Merge). 3. 섞여버린 안정화 연산자들을 통해 $Y$ 값을 추출한다.

![Logical_X_Z_Extension1](https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/extend1.png?w=828)

![Logical_X_Z_Extension2](https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/extend2.png?w=828)

![Logical_X_Z_Extension3](https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/extend3.png?w=828)

- 패치 확장 (Patch Extension): 큐비트 영역 넓히기
- 예시 (Z-edge 확장): * 가로로 긴 사각형 패치가 있다고 가정합시다. 오른쪽 Z-edge 옆에 새로운 데이터 큐비트 열을 추가합니다.초기화: 이 새로운 열의 큐비트들을 $|0\rangle$ 상태로 초기화합니다. (Z-edge니까 $|0\rangle$이 기준입니다.)과정: $d$ (부호 거리)만큼의 에러 정정 주기를 돌립니다. 그러면 시스템은 새로운 큐비트들을 자신의 '영토'로 받아들입니다.결과: 이제 기존의 논리적 정보는 더 넓어진 영역에 걸쳐 존재하게 됩니다. 즉, 큐비트를 오른쪽으로 한 칸 '슬라이딩' 시킨 것입니다.

![Logical_X_Z_Corner_Moving](https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/corner_moving.png?w=828)

- 엣지 회전 (Edge Reorientation/Rotation): 성격 바꾸기
- 논리적 정보(Bulk)는 그대로 둔 채, 경계면의 성질만 바꾸는 것입니다.왜 필요한가? $Y$ 측정을 하려면 한 패치에 $X$와 $Z$ 엣지가 다 있어야 하는데, 현재 내 패치는 전부 다 $X$-edge일 수 있습니다. 이때 $X$-edge의 일부를 $Z$-edge로 성격만 바꿔주는 작업입니다.어떻게 하는가? * 패치의 특정 엣지를 따라 측정하는 안정화 연산자(Stabilizer)의 종류를 바꿉니다 (예: X-stabilizer 측정하던 곳을 Z-stabilizer 측정으로 변경).이때 '삼각형 모양의 안정화 연산자(Triangle-shaped stabilizers)'가 등장하는데, 이는 기존 $X$ 엣지와 새로운 $Z$ 엣지가 서로 조화롭게 교환(Commute)되도록 이어주는 완충 지대 역할을 합니다.결과적으로 물리적 큐비트 구성은 바뀌지 않지만, 시스템은 이제 그 경계를 $Z$-edge로 인식하기 시작합니다.


![Logical_X_Z_Y_Measurement](https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/y_measurement.png?w=828)

- Y measurement
    - 한 패치의 한쪽에 $X$-edge와 $Z$-edge가 동시에 존재하도록 만듭니다. (이 경계선에서 꼬임이 시작됩니다.)
    - 보조 큐비트(Auxiliary qubit) 하나를 준비하여 $|0\rangle$로 초기화하고 옆에 붙입니다.
    - 병합 (Lattice Merging): * 이 두 패치를 합칩니다. 이때 경계의 성질(X와 Z)이 다르기 때문에 시스템은 매우 당황합니다. 안정화 연산자들이 양쪽 큐비트의 정보를 잇는 과정에서, 물리적인 '트위스트(Twist)'가 발생합니다. (보라색으로 강조된 지점)
    - 측정 결과 ($Y$):합쳐진 패치에서 나오는 새로운 안정화 연산자들을 보세요. 신기하게도 $Z \otimes X$ 같은 섞인 형태의 연산자들이 튀어나옵니다.이것이 바로 $Y$ 연산자의 성질입니다. 튜토리얼에서 [ZZ, XY] = 0 등을 언급한 것은, 이 꼬인 공간 안에서는 $X$와 $Z$를 동시에 측정해도 수학적으로 에러가 나지 않고(교환 가능하고) 정확히 $Y$ 값을 내뱉는다는 증거입니다.


![Logical_X_Z_Twist_Boundaries](https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/twist_boundaries.png?w=828)


## Terms

**Measurement**
- Readout information from a quantum state causes the superposition state to collapse/project to one of its basis states randomly.
    - Measurement along **x basis (Hadamard basis)**: |+>, |->
    - Measurement along **z basis (Standard basis 'or' Computational basis)**: |0>, |1>

**Joint Measurement [2]**
- Measures shared information of multiple entangled qubits at once without revealing their individual states, preserving delicate quantum information.
- **Bell State Measurement (BSM)**: One of the most representative examples. It identifies which of the four perfect entangled states two qubits share, acting as the core engine for quantum teleportation.
    - All quantum gates are **reversible**.
    - **We can know the input based on output**.
    - **We can know the information of entangled data qubits.**

[1. Entanglement Creation]             [2. Bell State Measurement]

           ┌───┐                                 ┌───┐   ┌───┐   ┌─┐
Qubit A: ──┤ H ├───■─────────────────────────────┤ ■ ├───┤ H ├───┤M├── (Bit A)
           └───┘   │                             │ │ │   └───┘   └╥┘
Qubit B: ──────────⊕─────────────────────────────┤ ⊕ ├────────────╫─── (Bit B)
                                                 └───┘            ║

Note: The superposition states generated by the Hadamard gate are defined as:
**$|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$**
**$|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$**

| Initial Entangled State | Step 1: CNOT(A,B) | Step 2: H(A) (Fully Expanded) | Output |
| :--- | :--- | :--- | :--- |
| **$|\Phi^+\rangle$** = $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$ | $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$ | $\frac{1}{2}(|00\rangle + |10\rangle + |00\rangle - |10\rangle)$ | $|00\rangle$ |
| **$|\Psi^+\rangle$** = $\frac{1}{\sqrt{2}}(|01\rangle + |10\rangle)$ | $\frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$ | $\frac{1}{2}(|01\rangle + |11\rangle + |01\rangle - |11\rangle)$ | $|01\rangle$ |
| **$|\Phi^-\rangle$** = $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$ | $\frac{1}{\sqrt{2}}(|00\rangle - |10\rangle)$ | $\frac{1}{2}(|00\rangle + |10\rangle - |00\rangle + |10\rangle)$ | $|10\rangle$ |
| **$|\Psi^-\rangle$** = $\frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$ | $\frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$ | $\frac{1}{2}(|01\rangle + |11\rangle - |01\rangle + |11\rangle)$ | $|11\rangle$ |

- **Syndrome Extraction**: A process in superconducting systems -> Quantum Error Correction (QEC) relies on parity qubits to periodically extract information from data qubits via Z- or X-type stabilizer circuits (Surface Code has **degree-4**, four data qubits mapped to one parity qubit).
  - **What you do**: Perform standard single-qubit measurements on many individual ancilla (parity) qubits simultaneously.
  - **What it means**: Because each ancilla is entangled with its neighboring data qubits via stabilizer circuits (e.g., degree-4 in surface codes), these parallel single measurements effectively execute numerous **joint measurements** on the data qubits at once.
- **Examples:**
  - Performing a BSM on two qubits to read out their shared quantum correlation rather than their individual 0 or 1 values.
  - Measuring $Z \otimes Z \otimes Z \otimes Z$ parity in a surface code to detect if an error occurred, without ever asking if the individual qubits are $|0\rangle$ or $|1\rangle$.

**Codespace**
- A strictly defined "safe zone" (mathematical subspace) where valid, error-free quantum information is allowed to exist.
- Forces the system to only accept specific states, making errors stand out.
- **E.g.,** In a 2-qubit system, artificially restricting the valid states to only even parity ($a|00\rangle + b|11\rangle$) and treating odd parity ($|01\rangle, |10\rangle$) as errors.

**Encoding**
- The process of mapping fragile quantum information into the protected **Codespace**.
- Achieved by entangling multiple physical qubits together to form a single logical unit.
- If a physical error occurs, the state is kicked *out* of the codespace, triggering detection.
- **E.g.,** Translating a single logical $|0\rangle_L$ into a complex, entangled grid of many physical qubits on a surface code patch.

**Pauli Product Measurements (PPM) [1]**
- A macroscopic **Joint Measurement** that checks the parity of a multi-qubit Pauli operator (e.g., $X \otimes Z \otimes Y$) across several logical qubits.
- A **physically executable** operation.
- The **only physical operation** that can be executed directly and fault-tolerantly on surface code hardware.

**Pauli Product Rotations (PPR) [1]**
- A quantum rotation that uses a Pauli operator as its axis to rotate qubits by a specific angle.
- **Clifford PPRs** (e.g., multiples of $\pi/4$ rotations, multipples of $\pi/2$ rotations) can be easily handled by classical bookkeeping without physical hardware operations.
- **Non-Clifford PPRs** (e.g., $\pi/8$ rotations) are physically impossible to execute directly on surface code hardware. 
- e.g., **T gate** (a representative non-Clifford operation) -> multiples of $\pi/8$ rotations. Can be realized with a magic state injection + clifford gate
- **Non-Clifford PPR = PPM + Magic State** (Figure 7 of **[4]**).
- So, if **magic states are available**, the only operations required for universal quantum computing are **Pauli product measurements**.

**Magic State [3]**
- **Definition:** A specially prepared, pure quantum state (resource) injected from outside the system to achieve Universal Quantum Computation (UQC).
    - Typical examples include T-type and H-type magic states.
- **Why 'Magic'?**: They enable the execution of complex non-Clifford gates by using only simple Clifford gates and measurements. 
- They are precisely set at a specific angle.
    - e.g., $\pi/8$ rotated Pauli eigenstates $$|m\rangle = |0\rangle + e^{i\pi/4}|1\rangle$$
    - Normalized format: $$|m\rangle = \frac{1}{\sqrt{2}} \left( |0\rangle + e^{i\pi/4}|1\rangle \right)$$
- **Purpose:** To bypass the physical limitations of surface codes. They are absolutely essential for **universal quantum computation**!

**Magic State Distillation [4]**
- **Definition:** A protocol that takes multiple noisy, imperfect magic states and **purifies** them into a few **high-fidelity magic states**, using only fault-tolerant basic operations (Clifford gates and measurements).
- **Why is it needed?**: Due to realistic physical limitations, magic states prepared in external "factories" inevitably contain impurities/errors ($\rho$). Using these noisy states directly would ruin the computation.
- **The Threshold Rule (Crucial):** Distillation only works if the initial magic state's fidelity is above a certain threshold (e.g., > 91% for T-type). If the initial state is too noisy, the distillation fails and ruins the state completely.
- **How it works:** 
  1. Gather multiple imperfect magic states (e.g., 5 states for T-type, or 15 states for H-type distillation codes).
  2. Check for errors using reliable hardware operations (syndrome measurements).
  3. Discard the states entirely if any error signs are detected; keep only the ones that successfully pass the check.
  4. The surviving states are entangled to produce a single, higher-purity magic state with significantly reduced noise.
  5. Repeat this process (recursive iteration) to obtain magic states of the desired absolute purity.

**Non-clifford opearation**
- **Gottesman-Knill theorem**
    - All the gates (X, Y, Z, H, S, CNOT ...) are members of a special gorup of gates known as the Clifford group.
    - These gates can be simulated efficiently on a classical computer.
    - So, **the Clifford group is not universal on its own.**
- e.g., (T Gate, Toffoli gate, )
    - **T Gate**: A single-qubit gate that applies a **$\pi$/4 phase rotation ($\pi/8$ physical rotation)**. It **breaks the symmetry of the Clifford group** (does not map Puali operators back to Pauli operators) and enables **universal quantum computation** by allowing circuits to reach arbitrary states on the Bloch sphere.
    - **Why is a $\pi/4$ rotation called a $\pi/8$ gate?**
    - $$|\psi\rangle = \cos\left(\frac{\theta}{2}\right)|0\rangle + e^{i\phi}\sin\left(\frac{\theta}{2}\right)|1\rangle$$
    - **Actual Rotation ($\pi/4$)**: In the standard qubit state equation $|\psi\rangle = \cos\left(\frac{\theta}{2}\right)|0\rangle + e^{i\phi}\sin\left(\frac{\theta}{2}\right)|1\rangle$, the phase $\phi$ physically rotates by exactly **$\pi/4$ (45 degrees)**.
    - **Mathematical Expression ($\pi/8$)**: The standard formula for a Z-axis rotation matrix incorporates a half-angle ($\alpha/2$) in its exponents. When we plug in our actual rotation angle $\alpha = \pi/4$, the fraction **$\pi/8$** appears in the matrix elements, which is why it is conventionally called the $\pi/8$ gate.

$$
R_z(\alpha) = \left[ \begin{array}{cc}
e^{-i\frac{\alpha}{2}} & 0 \\
0 & e^{i\frac{\alpha}{2}}
\end{array} \right]
$$

$$
R_z\left(\frac{\pi}{4}\right) = \left[ \begin{array}{cc}
e^{-i\frac{\pi}{8}} & 0 \\
0 & e^{i\frac{\pi}{8}}
\end{array} \right]
$$

### Comparison Table: Clifford vs. Non-Clifford Gates

| Feature | Clifford Gates | Non-Clifford Gates (e.g., T, Toffoli) |
| --- | --- | --- |
| **Classical Simulation** | Efficient (Polynomial time) | Inefficient (Exponential time) |
| **Mathematical Role** | Maps Pauli to Pauli | "Escapes" the Pauli group |
| **Common Examples** | H, S, CNOT, Pauli X, Y, Z | T, Toffoli (CCNOT) |
| **Error Correction** | Easy to implement via stabilizer codes | Difficult; requires magic state distillation |
| **Universality** | Not universal on their own | Required for a universal gate set |

**Transversal Gate [5]**
- A logical gate that doesn't propagate errors within each code block (e.g., don't propagate errors within each surface codes)
![Transversal Gates (CNOTs between corresponding qubits on two code blocks)](https://arthurpesah.me/assets/img/blog/transversal-gates/transversal-cnot.png)
- Logical CNOTs between two logical qubits (surface code blocks) do not propagate errors within the each surface code block.

## References
**[1]** Litinski, Daniel. "A game of surface codes: Large-scale quantum computing with lattice surgery." Quantum 3 (2019): 128.

**[2]** Ding, Y. (2025). Lecture 6: Quantum Measurements [Lecture notes, CPSC 4470/5470]. Department of Computer Science, Yale University. https://www.yongshanding.com/cpsc447-f25/Lec6-f25.pdf

**[3]** Bravyi, Sergey, and Alexei Kitaev. "Universal quantum computation with ideal Clifford gates and noisy ancillas." Physical Review A—Atomic, Molecular, and Optical Physics 71.2 (2005): 022316.

**[4]** Litinski, Daniel. "A game of surface codes: Large-scale quantum computing with lattice surgery." Quantum 3 (2019): 128.

**[5]** Pesah, A. (2023, December 25). Computing with quantum codes using transversal gates. https://arthurpesah.me/blog/2023-12-25-transversal-gates/

**[6]** (1,2) Dominic Horsman, Austin G. Fowler, Simon Devitt, Rodney Van Meter, “Surface code quantum computing by lattice surgery”, arXiv:1111.4022, 2011

**[7]** (1,2) Christopher Chamberland, Earl T. Campbell “Universal quantum computing with twist-free and temporally encoded lattice surgery”, arXiv:2109.02746, 2021

**[8]** Austin G. Fowler, Craig Gidney “Low overhead quantum computation using lattice surgery” arXiv:1808.06709, 2018.

**[9]** Vuillot, Christophe, et al. "Code deformation and lattice surgery are gauge fixing." New Journal of Physics 21.3 (2019): 033028.