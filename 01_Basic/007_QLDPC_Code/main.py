import numpy as np
from scipy.sparse import csr_matrix, eye, hstack, kron
from bposd.css import css_code
from ldpc import bposd_decoder
import stim
import warnings

warnings.filterwarnings("ignore")

class GrossCode144:
    def __init__(self):
        self.L_dim = 12
        self.M_dim = 6
        self.N = 2 * self.L_dim * self.M_dim # 144
        self.hx, self.hz = self._construct_matrices()
        self.css = css_code(self.hx, self.hz)

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

def build_stim_circuit(qcode, p):
    circuit = stim.Circuit()
    circuit.append("DEPOLARIZE1", range(qcode.N), p)
    
    # Hx -> X-check -> Measure X-basis -> Detects Z-error
    cx = qcode.hx.tocsr()
    for i in range(cx.shape[0]):
        targets = [stim.target_x(c) for c in cx[i].nonzero()[1]]
        for t in range(len(targets) - 1): # Insert combiners manually
            targets.insert(2*t + 1, stim.target_combiner())
        circuit.append("MPP", targets)

    # Hz -> Z-check -> Measure Z-basis -> Detects X-error
    cz = qcode.hz.tocsr()
    for i in range(cz.shape[0]):
        targets = [stim.target_z(c) for c in cz[i].nonzero()[1]]
        for t in range(len(targets) - 1):
            targets.insert(2*t + 1, stim.target_combiner())
        circuit.append("MPP", targets)
        
    # Logical Operators (Ground Truth)
    # Logical X (Lx)
    lx = qcode.lx
    for i in range(qcode.K):
        # Sparse matrix slicing produces (1, N) matrix, need [1] for cols
        cols = lx[i].nonzero()[1]
        targets = [stim.target_x(c) for c in cols]
        circuit.append("OBSERVABLE_INCLUDE", targets, i) 

    # Logical Z (Lz)
    lz = qcode.lz
    for i in range(qcode.K):
        cols = lz[i].nonzero()[1]
        targets = [stim.target_z(c) for c in cols]
        circuit.append("OBSERVABLE_INCLUDE", targets, i + qcode.K) 
        
    return circuit

def main():
    print(">>> Initializing Gross Code...")
    gross_code = GrossCode144()
    qcode = gross_code.css

    # Decoder Setup
    bpd_z = bposd_decoder(qcode.hx, error_rate=0.01, max_iter=50, bp_method="ms", osd_order=10)
    bpd_x = bposd_decoder(qcode.hz, error_rate=0.01, max_iter=50, bp_method="ms", osd_order=10)

    # ----------------------------------------------------------------
    # DEBUG SECTION: Check why LER is 1.0
    # ----------------------------------------------------------------
    print("\n>>> DEBUG START: Running 1 Shot with p=0.0001")
    p = 0.0001
    circuit = build_stim_circuit(qcode, p)
    sampler = circuit.compile_sampler()
    samples = sampler.sample(1) # Just 1 shot

    n_z = qcode.hx.shape[0]
    n_x = qcode.hz.shape[0]
    
    syndromes_z = samples[0, :n_z]
    syndromes_x = samples[0, n_z : n_z + n_x]
    actual_flips = samples[0, n_z + n_x :]

    # Decode
    corr_z = bpd_z.decode(syndromes_z)
    corr_x = bpd_x.decode(syndromes_x)

    # Calculate Predict
    # Note: lx @ corr returns float/int array, we need % 2 and casting
    pred_lx = (qcode.lx @ corr_z) % 2
    pred_lz = (qcode.lz @ corr_x) % 2
    pred_flips = np.concatenate([pred_lx, pred_lz]).astype(int) # Force int type

    print(f"1. Shapes Check:")
    print(f"   - Actual Flips Shape: {actual_flips.shape}")
    print(f"   - Pred Flips Shape:   {pred_flips.shape}")
    print(f"2. Values Check (First 10 bits):")
    print(f"   - Actual: {actual_flips[:10]}")
    print(f"   - Pred:   {pred_flips[:10]}")
    print(f"3. Type Check:")
    print(f"   - Actual Type: {actual_flips.dtype}")
    print(f"   - Pred Type:   {pred_flips.dtype}")
    
    is_equal = np.array_equal(actual_flips, pred_flips)
    print(f"4. Result: Match? {is_equal}")
    
    if not is_equal:
        print("   !!! MISMATCH DETECTED !!!")
        print("   If Actual is all 0s and Pred is all 0s, check Types/Shapes.")
        return # Stop if debug fails
    else:
        print("   >>> SUCCESS: Logic is consistent.")
    
    # ----------------------------------------------------------------
    # MAIN SWEEP
    # ----------------------------------------------------------------
    prob_list = [0.0001, 0.001, 0.01]
    shots = 5000
    
    print(f"\n>>> Starting Main Sweep (Shots: {shots})")
    print(f"{'Physical p':<15} | {'Log Errors':<10} | {'LER':<10}")
    print("-" * 45)

    for p in prob_list:
        circuit = build_stim_circuit(qcode, p)
        sampler = circuit.compile_sampler()
        samples = sampler.sample(shots)
        
        logical_errors = 0
        
        for i in range(shots):
            syn_z = samples[i, :n_z]
            syn_x = samples[i, n_z : n_z + n_x]
            truth = samples[i, n_z + n_x :]
            
            c_z = bpd_z.decode(syn_z)
            c_x = bpd_x.decode(syn_x)
            
            p_lx = (qcode.lx @ c_z) % 2
            p_lz = (qcode.lz @ c_x) % 2
            guess = np.concatenate([p_lx, p_lz]).astype(int) # Ensure int
            
            if not np.array_equal(truth, guess):
                logical_errors += 1
                
        print(f"{p:<15.5f} | {logical_errors:<10} | {logical_errors/shots:<10.5f}")

if __name__ == "__main__":
    main()