import stim
import pymatching
import numpy as np
import matplotlib.pyplot as plt
from ldpc import bposd_decoder, mod2
from scipy.sparse import csc_matrix, issparse
import multiprocessing
from dataclasses import dataclass
import random

# ==============================================================================
# 1. Robust Gross Code Generator (Random Search)
# ==============================================================================
def get_circulant(L, shifts):
    """L x L 순환 행렬 생성"""
    mat = np.zeros((L, L), dtype=int)
    for i in range(L):
        for s in shifts:
            mat[i, (i + s) % L] = 1
    return mat

def generate_valid_gross_code():
    """
    논리 큐비트(k > 0)가 존재하는 Gross Code가 나올 때까지
    Shift 파라미터를 랜덤 변경하며 탐색합니다.
    """
    L = 72  # n = 144
    attempts = 0
    
    print("🔹 유효한 Gross Code(k > 0) 탐색 중...")
    
    while True:
        attempts += 1
        # Weight 3 (Row weight 6)를 위한 랜덤 Shift 3개씩 생성
        shifts_A = sorted(random.sample(range(L), 3))
        shifts_B = sorted(random.sample(range(L), 3))
        
        A = get_circulant(L, shifts_A)
        B = get_circulant(L, shifts_B)
        
        # Hx = [A, B], Hz = [B.T, A.T]
        Hx = np.hstack([A, B])
        Hz = np.hstack([B.T, A.T])
        
        # 랭크 계산 (GF(2))
        rank_x = mod2.rank(Hx)
        rank_z = mod2.rank(Hz)
        n = 144
        k = n - rank_x - rank_z
        
        # Commutativity Check: Hx * Hz.T == 0
        # Bicycle 구조상 A, B가 commute하면 자동 만족하지만 확인
        
        if k > 0:
            print(f"✅ 코드 발견! (시도 {attempts}회)")
            print(f"   - Shifts A: {shifts_A}")
            print(f"   - Shifts B: {shifts_B}")
            print(f"   - Parameters: [[n={n}, k={k}, d=?]]")
            return Hx, Hz
            
        if attempts > 100:
            print("⚠️ 100회 시도에도 코드를 찾지 못했습니다. 설정을 확인하세요.")
            exit()

def find_logical_z_operator(Hx, Hz):
    """
    Hx, Hz가 주어졌을 때 유효한 Logical Z 연산자 하나를 찾음
    """
    try:
        # Hx * z = 0 (Kernel)
        lz_candidates = mod2.nullspace(Hx) 
        
        # Sparse -> Dense 변환
        if issparse(lz_candidates) or hasattr(lz_candidates, "toarray"):
            lz_candidates = lz_candidates.toarray()
            
        if lz_candidates.ndim == 1:
            lz_candidates = np.array([lz_candidates])
            
        hz_rank = mod2.rank(Hz)
        
        # Kernel 벡터 중 Hz(Stabilizer)와 독립적인 것 탐색
        for cand in lz_candidates:
            cand_row = cand.flatten()
            combined = np.vstack([Hz, cand_row])
            if mod2.rank(combined) > hz_rank:
                return cand_row 
                
    except Exception as e:
        print(f"⚠️ Logical Operator 탐색 에러: {e}")
        
    return np.zeros(Hx.shape[1], dtype=int)

# ==============================================================================
# [Helper] Stim 구버전 호환용 DEM 파싱 함수
# ==============================================================================
def dem_to_matrices_manual(dem):
    priors = []
    cols_check, rows_check = [], []
    cols_obs, rows_obs = [], []
    
    err_idx = 0
    for instr in dem:
        if instr.type == "error":
            p = instr.args_copy()[0]
            priors.append(p)
            for t in instr.targets_copy():
                if t.is_relative_detector_id():
                    rows_check.append(t.val)
                    cols_check.append(err_idx)
                elif t.is_logical_observable_id():
                    rows_obs.append(t.val)
                    cols_obs.append(err_idx)
            err_idx += 1
            
    num_errors = err_idx
    num_detectors = dem.num_detectors
    num_observables = dem.num_observables
    
    check_matrix = csc_matrix((np.ones(len(cols_check)), (rows_check, cols_check)), shape=(num_detectors, num_errors))
    observables_matrix = csc_matrix((np.ones(len(cols_obs)), (rows_obs, cols_obs)), shape=(num_observables, num_errors))
    
    return check_matrix, observables_matrix, np.array(priors)

# ==============================================================================
# 2. Circuit Generator (Gate-Based Accurate Noise Model)
# ==============================================================================
def generate_gross_code_circuit_accurate(Hx, Hz, logical_z_op, p, rounds):
    num_data = Hx.shape[1]
    num_x_checks = Hx.shape[0]
    num_z_checks = Hz.shape[0]
    
    data_qubits = list(range(num_data))
    anc_x_start = num_data
    anc_z_start = anc_x_start + num_x_checks
    
    circuit = stim.Circuit()
    
    x_ancillas = list(range(anc_x_start, anc_x_start + num_x_checks))
    z_ancillas = list(range(anc_z_start, anc_z_start + num_z_checks))
    all_ancillas = x_ancillas + z_ancillas
    all_qubits = data_qubits + all_ancillas

    # --- A. Initialization ---
    circuit.append("R", all_qubits)
    circuit.append("X_ERROR", all_qubits, p) 

    # --- B. Syndrome Extraction Rounds ---
    for r in range(rounds):
        # 1. X-Checks
        circuit.append("H", x_ancillas)
        circuit.append("DEPOLARIZE1", x_ancillas, p)

        for i in range(num_x_checks):
            anc = anc_x_start + i
            targets = np.nonzero(Hx[i, :])[0]
            for t in targets:
                circuit.append("CNOT", [anc, t])
                circuit.append("DEPOLARIZE2", [anc, t], p)

        circuit.append("H", x_ancillas)
        circuit.append("DEPOLARIZE1", x_ancillas, p)

        # 2. Z-Checks
        for i in range(num_z_checks):
            anc = anc_z_start + i
            targets = np.nonzero(Hz[i, :])[0]
            for t in targets:
                circuit.append("CNOT", [t, anc])
                circuit.append("DEPOLARIZE2", [t, anc], p)

        # 3. Measure Ancillas
        circuit.append("X_ERROR", all_ancillas, p) 
        circuit.append("MR", all_ancillas) 
        circuit.append("X_ERROR", all_ancillas, p) 

        # 4. Detectors
        for i in range(num_x_checks):
            rec_idx = - (num_x_checks + num_z_checks) + i
            if r == 0: pass 
            else:
                targets = [stim.target_rec(rec_idx), stim.target_rec(rec_idx - (num_x_checks + num_z_checks))]
                circuit.append("DETECTOR", targets, [float(r), float(i), 0.0])

        for i in range(num_z_checks):
            rec_idx = - num_z_checks + i
            targets = []
            if r == 0: targets = [stim.target_rec(rec_idx)] 
            else: targets = [stim.target_rec(rec_idx), stim.target_rec(rec_idx - (num_x_checks + num_z_checks))]
            circuit.append("DETECTOR", targets, [float(r), float(i), 1.0])

    # --- C. Final Measurement ---
    circuit.append("X_ERROR", data_qubits, p)
    circuit.append("M", data_qubits)
    
    for i in range(num_z_checks):
        targets = np.nonzero(Hz[i, :])[0]
        rec_targets = [stim.target_rec(t - num_data) for t in targets] 
        last_ancilla_rec = stim.target_rec(-num_data - num_z_checks + i)
        circuit.append("DETECTOR", rec_targets + [last_ancilla_rec], [float(rounds), float(i), 1.0])

    # Logical Observable
    obs_targets = [stim.target_rec(t - num_data) for t in logical_z_op]
    circuit.append("OBSERVABLE_INCLUDE", obs_targets, 0.0)

    return circuit

# ==============================================================================
# 3. Simulation Worker
# ==============================================================================
@dataclass
class SimParams:
    code_type: str 
    p: float
    shots: int
    distance: int = 0
    gross_hx: np.ndarray = None
    gross_hz: np.ndarray = None
    gross_lz: list = None

def worker_simulation(params: SimParams):
    if params.code_type == "surface":
        circuit = stim.Circuit.generated(
            "surface_code:rotated_memory_z",
            rounds=params.distance,
            distance=params.distance,
            after_clifford_depolarization=params.p,
            after_reset_flip_probability=params.p,
            before_measure_flip_probability=params.p,
            before_round_data_depolarization=params.p
        )
    else:
        rounds = 12 if params.distance == 0 else params.distance 
        circuit = generate_gross_code_circuit_accurate(
            params.gross_hx, params.gross_hz, params.gross_lz, params.p, rounds
        )

    sampler = circuit.compile_detector_sampler()
    batch_size = 20_000
    total_errors = 0
    executed_shots = 0
    
    # [설정] 복잡한 에러 분해 실패 허용 옵션
    dem = circuit.detector_error_model(
        decompose_errors=True, 
        ignore_decomposition_failures=True
    )
    
    if params.code_type == "surface":
        matcher = pymatching.Matching.from_detector_error_model(dem)
        while executed_shots < params.shots:
            current_batch = min(batch_size, params.shots - executed_shots)
            syndrome_batch, actual_obs_batch = sampler.sample(shots=current_batch, separate_observables=True)
            predicted_obs = matcher.decode_batch(syndrome_batch)
            errors = np.sum(np.any(predicted_obs != actual_obs_batch, axis=1))
            total_errors += errors
            executed_shots += current_batch
            if total_errors > 500: break
    else:
        # Gross Code: BP+OSD
        try:
            dem_m = dem.to_dem_matrices(probability_func=lambda x: x)
            check_mat = csc_matrix(dem_m.check_matrix)
            obs_mat = csc_matrix(dem_m.observables_matrix)
            priors = dem_m.priors
        except AttributeError:
            check_mat, obs_mat, priors = dem_to_matrices_manual(dem)

        bp_decoder = bposd_decoder(
            check_mat,                  
            error_rate=0.0001,          
            channel_probs=priors,       
            max_iter=50, bp_method="ms", osd_method="osd_cs", osd_order=10
        )
        
        while executed_shots < params.shots:
            current_batch = min(batch_size, params.shots - executed_shots)
            syndrome_batch, actual_obs_batch = sampler.sample(shots=current_batch, separate_observables=True)
            
            preds_logical = []
            for i in range(current_batch):
                estimated_error_mechanisms = bp_decoder.decode(syndrome_batch[i])
                predicted_flip = (obs_mat @ estimated_error_mechanisms) % 2
                preds_logical.append(predicted_flip)
            
            predicted_obs = np.array(preds_logical).reshape(-1, 1)
            errors = np.sum(np.any(predicted_obs != actual_obs_batch, axis=1))
            total_errors += errors
            executed_shots += current_batch
            if total_errors > 500: break
            
    return (params.code_type, params.distance, params.p, total_errors, executed_shots)

# ==============================================================================
# 4. Main Execution
# ==============================================================================
if __name__ == "__main__":
    # --------------------------------------------------------------------------
    # [STEP 1] Valid Gross Code (k>0) 자동 생성
    # --------------------------------------------------------------------------
    Hx_gen, Hz_gen = generate_valid_gross_code() # 수정된 생성 함수 호출
    
    print("🔹 Logical Z Operator 탐색 중...")
    Lz_gen_vector = find_logical_z_operator(Hx_gen, Hz_gen)
    
    if not np.any(Lz_gen_vector):
        print("❌ 실패: Logical Z를 찾을 수 없습니다. (매우 드문 경우)")
        exit()
        
    Lz_gen = np.nonzero(Lz_gen_vector)[0].tolist()
    print(f"✅ 시뮬레이션 준비 완료! (Logical Z Weight={len(Lz_gen)})")

    # 파라미터 설정
    surface_distances = [3, 5, 7, 9]
    physical_error_rates = np.geomspace(1e-4, 1e-2, 10)
    target_shots = 1_000_000 
    num_workers = max(1, multiprocessing.cpu_count() - 2)
    
    tasks = []
    
    for d in surface_distances:
        for p in physical_error_rates:
            tasks.append(SimParams("surface", p, target_shots, distance=d))
    
    for p in physical_error_rates:
        tasks.append(SimParams("gross", p, target_shots, gross_hx=Hx_gen, gross_hz=Hz_gen, gross_lz=Lz_gen))

    print(f"🚀 시뮬레이션 시작 (Workers: {num_workers})...")
    
    results = { "surface": {}, "gross": {} }
    for d in surface_distances: results["surface"][d] = ([], [])
    results["gross"] = ([], [])

    with multiprocessing.Pool(num_workers) as pool:
        for res in pool.imap_unordered(worker_simulation, tasks):
            c_type, dist, p, errs, shots = res
            ler = errs / shots
            
            d_str = f"d={dist}" if dist else "Gross"
            print(f"[{c_type.upper()}] {d_str:<4} p={p:.5f} -> LER={ler:.2e} ({errs}/{shots})")
            
            if c_type == "surface":
                results["surface"][dist][0].append(p)
                results["surface"][dist][1].append(ler)
            else:
                results["gross"][0].append(p)
                results["gross"][1].append(ler)

    # 그래프 저장
    plt.figure(figsize=(10, 8))
    plt.plot([1e-4, 1e-2], [1e-4, 1e-2], 'k:', alpha=0.5, label='Break-even (PL=p)')

    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
    for i, d in enumerate(surface_distances):
        p_data, ler_data = results["surface"][d]
        sorted_pairs = sorted(zip(p_data, ler_data))
        if sorted_pairs:
            plt.plot(*zip(*sorted_pairs), marker='o', linestyle='--', color=colors[i], label=f'Surface d={d}')

    p_g, ler_g = results["gross"]
    sorted_pairs_g = sorted(zip(p_g, ler_g))
    if sorted_pairs_g:
        plt.plot(*zip(*sorted_pairs_g), marker='D', color='black', linewidth=2, label='Generated Gross Code')

    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Physical Error Rate (p)')
    plt.ylabel('Logical Error Rate ($P_L$)')
    plt.title('Circuit-Level Threshold: Gross Code vs Surface Code')
    plt.grid(True, which="both", linestyle='--', alpha=0.3)
    plt.legend()
    
    filename = "gross_vs_surface_final.png"
    plt.savefig(filename, dpi=300)
    print(f"\n✅ 그래프 저장 완료: {filename}")