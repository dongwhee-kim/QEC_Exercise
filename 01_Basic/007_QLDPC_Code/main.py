import numpy as np
from scipy.sparse import csr_matrix, eye, hstack, kron
from bposd.css import css_code
from ldpc import bposd_decoder
import time
import warnings
import matplotlib.pyplot as plt

# 경고 무시
warnings.filterwarnings("ignore")

class GrossCode144:
    """
    Bravyi et al. (Nature 2024) [[144, 12, 12]] Code
    """
    def __init__(self):
        self.L_dim = 12
        self.M_dim = 6
        self.N = 2 * self.L_dim * self.M_dim # 144
        self.hx, self.hz = self._construct_matrices()
        self.css = css_code(self.hx, self.hz)
        print(f"Code Constructed: [[{self.css.N}, {self.css.K}, {self.css.D}]]")

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

def generate_errors(N, p, num_shots):
    """
    Generate independent X/Z errors (Code Capacity Model)
    """
    error_x = np.random.choice([0, 1], size=(num_shots, N), p=[1-p, p])
    error_z = np.random.choice([0, 1], size=(num_shots, N), p=[1-p, p])
    return error_x, error_z

def main():
    print(">>> Initializing Gross Code [[144, 12, 12]]...")
    gross_code = GrossCode144()
    qcode = gross_code.css

    # Decoder Setup
    # X-error decoder (uses Hz)
    bpd_x = bposd_decoder(
        qcode.hz, error_rate=0.01, max_iter=50, bp_method="ms",
        osd_method="osd_cs", osd_order=10
    )
    # Z-error decoder (uses Hx)
    bpd_z = bposd_decoder(
        qcode.hx, error_rate=0.01, max_iter=50, bp_method="ms",
        osd_method="osd_cs", osd_order=10
    )

    # ---------------------------------------------------------
    # Sweep Parameters (Updated)
    # ---------------------------------------------------------
    # 1e-4 부터 1e-2 까지 10개 지점 (Log scale spacing)
    physical_error_rates = np.geomspace(1e-4, 1e-2, 10)
    shots = 1_000_000
    
    print(f"\n>>> Starting Fine-Grained Sweep (Shots: {shots})")
    print(f"{'Physical p':<15} | {'Log Errors':<10} | {'LER':<10} | {'Time (s)':<10}")
    print("-" * 55)

    ler_results = []

    for p in physical_error_rates:
        start_t = time.time()
        
        # 1. Generate Errors
        ex, ez = generate_errors(qcode.N, p, shots)
        
        # 2. Calculate Syndromes (Matrix Mul)
        syn_x = (qcode.hz @ ex.T).T % 2
        syn_z = (qcode.hx @ ez.T).T % 2
        
        logical_errors = 0
        
        # 3. Decode Loop
        for i in range(shots):
            # X Correction
            corr_x = bpd_x.decode(syn_x[i])
            res_x = (ex[i] + corr_x) % 2
            
            # Z Correction
            corr_z = bpd_z.decode(syn_z[i])
            res_z = (ez[i] + corr_z) % 2
            
            # Logical Error Check
            # Lz checks X-error (anticommute), Lx checks Z-error (anticommute)
            lz_flip = (qcode.lz @ res_x) % 2
            lx_flip = (qcode.lx @ res_z) % 2
            
            if np.any(lz_flip) or np.any(lx_flip):
                logical_errors += 1

        end_t = time.time()
        ler = logical_errors / shots
        ler_results.append(ler)
        print(f"{p:<15.5f} | {logical_errors:<10} | {ler:<10.5f} | {end_t - start_t:<10.2f}")

    # ---------------------------------------------------------
    # Plotting
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 7))
    
    # Main Data
    plt.loglog(physical_error_rates, ler_results, 'o-', linewidth=2, markersize=8, label='[[144,12,12]] BB Code')
    
    # Reference Line (Break-even y=x)
    plt.loglog(physical_error_rates, physical_error_rates, 'k--', alpha=0.3, label='Physical Error Rate (Break-even)')
    
    plt.grid(True, which="both", linestyle='--', alpha=0.5)
    plt.xlabel('Physical Error Rate ($p$)', fontsize=12)
    plt.ylabel('Logical Error Rate ($P_L$)', fontsize=12)
    plt.title('Code Capacity Performance: Gross Code [[144,12,12]]', fontsize=14)
    plt.legend(fontsize=12)
    
    # 저장 및 출력
    save_filename = 'gross_code_fine_sweep.png'
    plt.savefig(save_filename)
    print(f"\n>>> Graph saved to '{save_filename}'")
    plt.show()

if __name__ == "__main__":
    main()