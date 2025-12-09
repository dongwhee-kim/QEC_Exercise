import numpy as np
from scipy.sparse import csr_matrix, eye, hstack, kron
from bposd.css import css_code
from ldpc import bposd_decoder
import stim
import sinter
import matplotlib.pyplot as plt
import time
import multiprocessing
import networkx as nx
import warnings
from typing import List

# 경고 무시
warnings.filterwarnings("ignore")

# ==============================================================================
# 1. Gross Code [[144, 12, 12]] Implementation
# ==============================================================================
class GrossCode144:
    def __init__(self):
        self.L_dim = 12
        self.M_dim = 6
        self.N = 2 * self.L_dim * self.M_dim # 144
        self.hx, self.hz = self._construct_matrices()
        self.css = css_code(self.hx, self.hz)
        self.lx = self.css.lx
        self.lz = self.css.lz
        
        # 스케줄링 (Graph Coloring) - 회로 Depth 최적화
        self.z_schedule = self._build_schedule(self.hz)
        self.x_schedule = self._build_schedule(self.hx)

    def _get_cyclic_shift(self, size, shift):
        data = np.ones(size)
        rows = np.arange(size)
        cols = (rows + shift) % size
        return csr_matrix((data, (rows, cols)), shape=(size, size))

    def _construct_matrices(self):
        I_l = eye(self.L_dim); I_m = eye(self.M_dim)
        S_l = self._get_cyclic_shift(self.L_dim, 1)
        S_m = self._get_cyclic_shift(self.M_dim, 1)
        
        x = kron(S_l, I_m)
        y = kron(I_l, S_m)

        A = (x ** 3) + y + (y ** 2)
        B = (y ** 3) + x + (x ** 2)
        A = A.toarray().astype(int) % 2
        B = B.toarray().astype(int) % 2

        Hx = np.hstack([A, B])
        Hz = np.hstack([B.T, A.T])
        return csr_matrix(Hx), csr_matrix(Hz)

    def _build_schedule(self, H):
        num_checks, num_data = H.shape
        G = nx.Graph()
        G.add_nodes_from(range(num_checks))
        
        rows, cols = H.nonzero()
        qubit_to_checks = {}
        for r, c in zip(rows, cols):
            if c not in qubit_to_checks: qubit_to_checks[c] = []
            qubit_to_checks[c].append(r)
            
        for q in qubit_to_checks:
            checks = qubit_to_checks[q]
            for i in range(len(checks)):
                for j in range(i+1, len(checks)):
                    G.add_edge(checks[i], checks[j])
        
        coloring = nx.coloring.greedy_color(G, strategy='largest_first')
        
        schedule = {}
        for check_idx, color in coloring.items():
            if color not in schedule: schedule[color] = []
            schedule[color].append(check_idx)
        return list(schedule.values())

def build_noisy_gross_circuit_z_memory(gross, p):
    """
    Constructs a Stim circuit for Z-basis Memory Experiment.
    Init |0> -> Noise -> Measure Syndromes -> Check Logical Z
    """
    circuit = stim.Circuit()
    
    # Ancilla Map: Z-checks (144~215), X-checks (216~287)
    
    # 1. Z-Check Cycle (Hz measures Z-operators -> Detects X Errors)
    ancilla_offset_z = 144
    for batch in gross.z_schedule:
        targets_init = [a + ancilla_offset_z for a in batch]
        circuit.append("R", targets_init)
        circuit.append("DEPOLARIZE1", targets_init, p)
        
        for check_idx in batch:
            row = gross.hz[check_idx]
            data_qubits = row.nonzero()[1]
            ancilla = check_idx + ancilla_offset_z
            for dq in data_qubits:
                circuit.append("CNOT", [dq, ancilla])
                circuit.append("DEPOLARIZE2", [dq, ancilla], p)
        
        circuit.append("X_ERROR", targets_init, p) 
        circuit.append("M", targets_init)

    # 2. X-Check Cycle (Hx measures X-operators -> Detects Z Errors)
    # (Although we are in Z-basis, we still run this to simulate full circuit noise)
    ancilla_offset_x = 144 + 72
    for batch in gross.x_schedule:
        targets_init = [a + ancilla_offset_x for a in batch]
        circuit.append("R", targets_init)
        circuit.append("DEPOLARIZE1", targets_init, p)
        circuit.append("H", targets_init)
        circuit.append("DEPOLARIZE1", targets_init, p)
        
        for check_idx in batch:
            row = gross.hx[check_idx]
            data_qubits = row.nonzero()[1]
            ancilla = check_idx + ancilla_offset_x
            for dq in data_qubits:
                circuit.append("CNOT", [ancilla, dq])
                circuit.append("DEPOLARIZE2", [ancilla, dq], p)
        
        circuit.append("H", targets_init)
        circuit.append("DEPOLARIZE1", targets_init, p)
        circuit.append("X_ERROR", targets_init, p) 
        circuit.append("M", targets_init)

    # 3. Logical Ground Truth Check (ONLY Z)
    # Logical X measurement removed to avoid random collapse of |0> state
    
    # Logical Z (Lz) - This is deterministic for |0> state
    for i in range(gross.css.K):
        cols = gross.lz[i].nonzero()[1]
        targets = []
        for c in cols:
            targets.append(stim.target_z(c))
            targets.append(stim.target_combiner())
        if targets: targets.pop()
        circuit.append("MPP", targets)
        
    return circuit

def run_gross_worker(args):
    p, shots = args
    p = float(p)
    
    gross = GrossCode144()
    
    # [Fix] Use Z-Memory Circuit
    circuit = build_noisy_gross_circuit_z_memory(gross, p)
    sampler = circuit.compile_sampler()
    samples = sampler.sample(shots)
    
    # Mapping reconstruction
    z_measure_order = []
    for batch in gross.z_schedule:
        z_measure_order.extend(batch)
    
    # X measurement results are present but not used for X-correction
    # (Because Z-errors don't flip Logical Z)
    num_z = 72
    num_x = 72
    
    # Samples layout: [Syndrome_Z (72) | Syndrome_X (72) | Logical_Z (12)]
    raw_z = samples[:, :num_z]
    # raw_x = samples[:, num_z : num_z + num_x] # Not needed for Z-memory X-correction
    actual_flips_lz = samples[:, num_z + num_x:]
    
    # Sort Z syndromes
    sorted_z = np.zeros_like(raw_z)
    for meas_idx, check_idx in enumerate(z_measure_order):
        sorted_z[:, check_idx] = raw_z[:, meas_idx]
        
    # Decoder for X-errors (Uses Hz syndromes)
    # We only care about X-errors because they flip Logical Z.
    bpd_x = bposd_decoder(
        gross.css.hz,
        error_rate=p,
        max_iter=50,
        bp_method="ms",
        osd_method="osd_cs",
        osd_order=10
    )
    
    logical_errors = 0
    
    for i in range(shots):
        # 1. Decode X-errors using Hz
        corr_x = bpd_x.decode(sorted_z[i]) 
        
        # 2. Check if Correction flips Logical Z
        # (Original Z-noise doesn't matter for Z-basis memory)
        pred_lz = (gross.lz @ corr_x) % 2
        
        # 3. Compare with Ground Truth
        if not np.array_equal(pred_lz, actual_flips_lz[i]):
            logical_errors += 1
            
    return logical_errors, shots

# ==============================================================================
# Main
# ==============================================================================
def main():
    physical_error_rates = np.geomspace(1e-4, 1e-2, 10)
    target_shots = 1_000_00
    num_workers = max(1, multiprocessing.cpu_count() - 2)

    print(f"===========================================================")
    print(f" Circuit-Level Comparison: Gross Code vs Surface Code")
    print(f" Experiment: Z-Basis Memory (Robustness against X-errors)")
    print(f" Shots: {target_shots}, Workers: {num_workers}")
    print(f"===========================================================")

    # 1. Surface Code (Sinter)
    print("\n>>> [1/2] Running Rotated Surface Code (Circuit Level)...")
    surface_distances = [3, 5, 7, 9]
    surface_results = {}
    
    tasks = []
    for d in surface_distances:
        for p in physical_error_rates:
            p_float = float(p)
            tasks.append(
                sinter.Task(
                    circuit=stim.Circuit.generated(
                        "surface_code:rotated_memory_z",
                        rounds=d, distance=d,
                        after_clifford_depolarization=p_float,
                        after_reset_flip_probability=p_float,
                        before_measure_flip_probability=p_float,
                        before_round_data_depolarization=p_float
                    ),
                    json_metadata={'d': d, 'p': p_float}
                )
            )
            
    collected_stats = sinter.collect(
        num_workers=num_workers,
        tasks=tasks,
        max_shots=target_shots,
        decoders=['pymatching'],
        print_progress=False
    )
    print("    Surface Code simulation complete.")
    
    for d in surface_distances:
        stats_d = [s for s in collected_stats if s.json_metadata['d'] == d]
        stats_d.sort(key=lambda s: s.json_metadata['p'])
        surface_results[d] = (
            [s.json_metadata['p'] for s in stats_d],
            [s.errors / s.shots if s.shots > 0 else 0 for s in stats_d]
        )

    # 2. Gross Code (Circuit Level)
    print("\n>>> [2/2] Running Gross Code [[144,12,12]] (Circuit Level)...")
    gross_ler = []
    
    chunk_size = target_shots // num_workers
    chunks = [chunk_size] * num_workers
    if target_shots % num_workers: chunks[-1] += (target_shots % num_workers)
    
    with multiprocessing.Pool(num_workers) as pool:
        for p in physical_error_rates:
            p_float = float(p)
            start_t = time.time()
            jobs = [(p_float, c) for c in chunks]
            
            results = pool.map(run_gross_worker, jobs)
            
            errs = sum(r[0] for r in results)
            runs = sum(r[1] for r in results)
            ler = errs / runs
            gross_ler.append(ler)
            print(f"    p={p_float:.5f} | LER={ler:.6f} | Time={time.time()-start_t:.1f}s")

    # 3. Plot
    print("\n>>> Generating Plot...")
    plt.figure(figsize=(10, 8))
    
    plt.loglog(physical_error_rates, gross_ler, 'D-', color='black', linewidth=2.5, markersize=8, label='[[144,12,12]] Gross (Circuit Noise)')
    
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
    for i, d in enumerate(surface_distances):
        x_vals = surface_results[d][0]
        y_vals = surface_results[d][1]
        plt.loglog(x_vals, y_vals, 'o--', color=colors[i], label=f'Surface d={d} (Circuit Noise)')
        
    plt.loglog(physical_error_rates, physical_error_rates, 'k:', alpha=0.3, label='Break-even')
    
    plt.grid(True, which="both", linestyle='--', alpha=0.4)
    plt.xlabel('Physical Error Rate (p)', fontsize=12)
    plt.ylabel('Logical Error Rate ($P_L$)', fontsize=12)
    plt.title('Circuit-Level Threshold: Gross Code vs Surface Code', fontsize=14)
    plt.legend()
    
    plt.savefig("circuit_level_comparison_z_basis.png")
    print(">>> Saved to 'circuit_level_comparison_z_basis.png'")
    plt.show()

if __name__ == "__main__":
    main()