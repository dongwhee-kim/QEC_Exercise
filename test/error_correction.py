import networkx as nx
import numpy as np
import itertools 
import pymatching  # 1. PyMatching 라이브러리 임포트

def get_stabilizer_and_decoding_maps():
    """
    Defines the stabilizer connectivity and the mapping for the decoding graph.
    This corresponds to a specific surface code layout (e.g., rotated surface code 13-qubit).
    (이 함수는 변경되지 않았습니다.)
    """
    z_stabilizers = {
        'c_z[0]': ('d[0]', 'd[1]', 'd[3]'),
        'c_z[1]': ('d[1]', 'd[2]', 'd[4]'),
        'c_z[2]': ('d[3]', 'd[5]', 'd[6]', 'd[8]'),
        'c_z[3]': ('d[4]', 'd[6]', 'd[7]', 'd[9]'),
        'c_z[4]': ('d[8]', 'd[10]', 'd[11]'),
        'c_z[5]': ('d[9]', 'd[11]', 'd[12]')
    }
    x_stabilizers = {
        'c_x[0]': ('d[0]', 'd[3]', 'd[5]'),
        'c_x[1]': ('d[1]', 'd[3]', 'd[4]', 'd[6]'),
        'c_x[2]': ('d[2]', 'd[4]', 'd[7]'),
        'c_x[3]': ('d[5]', 'd[8]', 'd[10]'),
        'c_x[4]': ('d[6]', 'd[8]', 'd[9]', 'd[11]'),
        'c_x[5]': ('d[7]', 'd[9]', 'd[12]')
    }
    
    # Maps spatial edges (ancilla pairs) to the corresponding data qubit index for Z-graph (X-errors)
    z_spatial_map = {
        (0, 1): 1, (0, 2): 3, (1, 3): 4, (2, 3): 6, 
        (2, 4): 8, (3, 5): 9, (4, 5): 11
    }
    # Maps boundary ancilla indices to their corresponding data qubit index for Z-graph
    z_boundary_map = {0: 0, 1: 2, 2: 5, 3: 7, 4: 10, 5: 12}
    
    # Maps spatial edges (ancilla pairs) to the corresponding data qubit index for X-graph (Z-errors)
    x_spatial_map = {
        (0, 1): 3, (0, 3): 5, (1, 2): 4, (1, 4): 6, 
        (2, 5): 7, (3, 4): 8, (4, 5): 9
    }
    # Maps boundary ancilla indices to their corresponding data qubit index for X-graph
    x_boundary_map = {0: 0, 1: 1, 2: 2, 3: 10, 4: 11, 5: 12}

    return (
        z_stabilizers, x_stabilizers, 
        z_spatial_map, z_boundary_map, 
        x_spatial_map, x_boundary_map
    )

# --- 2. PyMatching을 위한 디코딩 그래프 생성 함수 (수정됨) ---
def build_matching_graph(num_rounds, num_ancillas, spatial_edges, spatial_map, boundary_map, w_spatial, w_temporal, w_boundary_edge):
    """
    Creates the space-time decoding graph as a networkx.Graph
    formatted for PyMatching.
    
    PyMatching의 핵심:
    - 'fault_id' 속성: 매칭 경로에 이 간선이 포함될 경우, 
      어떤 물리적 오류(여기서는 데이터 큐비트 인덱스)가 발생했는지를 나타냅니다.
    """
    G = nx.Graph()
    
    num_nodes_per_round = num_ancillas
    
    # 1. Spatial edges (공간적 간선)
    # 각 시간(라운드) 슬라이스 내의 간선
    for r in range(num_rounds):
        offset = r * num_nodes_per_round
        for u_raw, v_raw in spatial_edges:
            u, v = min(u_raw, v_raw), max(u_raw, v_raw)
            # 'fault_id'는 이 간선이 나타내는 데이터 큐비트의 인덱스입니다.
            qubit_id = spatial_map.get((u, v))
            G.add_edge(
                u + offset, 
                v + offset, 
                weight=w_spatial, 
                fault_id=qubit_id
            )
            
    # 2. Temporal edges (시간적 간선)
    # 서로 다른 시간 슬라이스 간의 동일한 큐비트를 연결 (측정 오류)
    for r in range(num_rounds - 1):
        offset1 = r * num_nodes_per_round
        offset2 = (r + 1) * num_nodes_per_round
        for a in range(num_ancillas):
            # 측정 오류는 데이터 큐비트 플립에 직접 해당하지 않으므로 'fault_id'가 없습니다.
            G.add_edge(
                a + offset1, 
                a + offset2, 
                weight=w_temporal
            ) 

    # 3. Boundary edges (경계 간선)
    # 마지막 라운드의 노드들을 단일 경계 노드에 연결
    final_round_offset = (num_rounds - 1) * num_nodes_per_round
    boundary_node = num_rounds * num_nodes_per_round # 단일 경계 노드 인덱스
    G.add_node(boundary_node) 
    
    for a_idx in range(num_ancillas):
        if a_idx in boundary_map: 
            node_in_final_round = a_idx + final_round_offset
            # 'fault_id'는 이 경계 간선이 나타내는 데이터 큐비트의 인덱스입니다.
            qubit_id = boundary_map.get(a_idx)
            G.add_edge(
                node_in_final_round, 
                boundary_node, 
                weight=w_boundary_edge, 
                fault_id=qubit_id
            )
        
    return G

# --- Calculate Syndrome from Final Result Bits ---
def calculate_syndrome_from_res(res_bits, stabilizers_map, num_ancillas):
    """
    Calculates the final syndrome by measuring stabilizers on the final data qubit state (res_bits).
    (이 함수는 변경되지 않았습니다.)
    """
    final_syndrome = np.zeros(num_ancillas, dtype=int)
    
    for a_idx, (a_name, data_qubits) in enumerate(stabilizers_map.items()):
        parity = 0
        for dq_str in data_qubits: 
            dq_idx = int(dq_str[2:-1]) # e.g., 'd[0]' -> 0
            parity ^= res_bits[dq_idx]
        final_syndrome[a_idx] = parity
        
    return final_syndrome

# --- Main Reporting Function ---
def run_error_correction_and_reporting(
    measured_string, num_rounds, num_data_qubits, num_x_ancillas, num_z_ancillas,
    spatial_edges_z, spatial_edges_x, prob_data_x, prob_data_z, prob_meas_z, prob_meas_x,
    injected_error_group, injected_data_flip_index, injected_ancilla_flip_index,
    enable_debug_printing=False): 
    
    (z_stabilizers, x_stabilizers, 
     z_spatial_map, z_boundary_map, 
     x_spatial_map, x_boundary_map) = get_stabilizer_and_decoding_maps()
    
    # --- 1. Parsing --- (변경 없음)
    num_sx = num_rounds * num_x_ancillas
    num_sz = num_rounds * num_z_ancillas
    cleaned_string = measured_string.replace(" ", "")
    
    sx_bits = [int(bit) for bit in cleaned_string[0:num_sx]][::-1]
    sz_bits = [int(bit) for bit in cleaned_string[num_sx : num_sx + num_sz]][::-1]
    res_bits = [int(bit) for bit in cleaned_string[num_sx + num_sz:]][::-1]

    # --- 2. 2D Transformation --- (변경 없음)
    sz_syndromes = np.array(sz_bits).reshape((num_rounds, num_z_ancillas))
    sx_syndromes = np.array(sx_bits).reshape((num_rounds, num_x_ancillas))
    
    # --- 3. Defect Calculation (Bulk) --- (변경 없음)
    z_defects = np.zeros((num_rounds, num_z_ancillas), dtype=int)
    z_defects[0, :] = sz_syndromes[0, :] 
    for r in range(1, num_rounds):
        z_defects[r, :] = np.bitwise_xor(sz_syndromes[r, :], sz_syndromes[r-1, :])
        
    x_defects = np.zeros((num_rounds, num_x_ancillas), dtype=int)
    x_defects[0, :] = sx_syndromes[0, :]
    for r in range(1, num_rounds):
        x_defects[r, :] = np.bitwise_xor(sx_syndromes[r, :], sx_syndromes[r-1, :])

    # --- 4. Boundary Defect Calculation --- (변경 없음)
    final_z_syndrome = calculate_syndrome_from_res(res_bits, z_stabilizers, num_z_ancillas)
    final_x_syndrome = np.zeros(num_x_ancillas, dtype=int) 
    
    final_z_defects = np.bitwise_xor(sz_syndromes[num_rounds-1, :], final_z_syndrome)
    final_x_defects = np.bitwise_xor(sx_syndromes[num_rounds-1, :], final_x_syndrome)

    # --- 5. MWPM Graph Creation & Matching (PyMatching으로 수정됨) ---
    
    # 가중치 계산
    w_data_x = -np.log(prob_data_x) if prob_data_x > 0 else float('inf')
    w_meas_z = -np.log(prob_meas_z) if prob_meas_z > 0 else float('inf')
    w_data_z = -np.log(prob_data_z) if prob_data_z > 0 else float('inf')
    w_meas_x = -np.log(prob_meas_x) if prob_meas_x > 0 else float('inf')

    # Z-Graph (for correcting X-errors)
    # 5-1. PyMatching용 networkx 그래프 생성
    z_graph_nx = build_matching_graph(
        num_rounds, num_z_ancillas, spatial_edges_z,
        z_spatial_map, z_boundary_map,
        w_data_x, w_meas_z, w_data_x # w_boundary_edge는 w_spatial과 동일
    )
    # 5-2. PyMatching 객체 생성
    z_matcher = pymatching.Matching(z_graph_nx)

    # 5-3. PyMatching에 입력할 결함 벡터(defect vector) 생성
    z_defect_vec = np.zeros(num_rounds * num_z_ancillas + 1, dtype=int)
    z_boundary_node_idx = num_rounds * num_z_ancillas
    
    # 벌크 결함 채우기
    z_defect_vec[0 : num_rounds * num_z_ancillas] = z_defects.flatten()
    
    # 경계 결함 (마지막 라운드 결함에 XOR)
    last_round_start_idx = (num_rounds - 1) * num_z_ancillas
    last_round_end_idx = num_rounds * num_z_ancillas
    z_defect_vec[last_round_start_idx : last_round_end_idx] ^= final_z_defects
    
    # 총 결함 수가 홀수이면 경계 노드와 매칭
    if np.sum(z_defect_vec) % 2 == 1:
        z_defect_vec[z_boundary_node_idx] = 1

    # 5-4. 디코딩 수행
    z_correction_fault_ids = z_matcher.decode(z_defect_vec)


    # X-Graph (for correcting Z-errors)
    # 5-1. PyMatching용 networkx 그래프 생성
    x_graph_nx = build_matching_graph(
        num_rounds, num_x_ancillas, spatial_edges_x,
        x_spatial_map, x_boundary_map,
        w_data_z, w_meas_x, w_data_z
    )
    # 5-2. PyMatching 객체 생성
    x_matcher = pymatching.Matching(x_graph_nx)

    # 5-3. 결함 벡터 생성
    x_defect_vec = np.zeros(num_rounds * num_x_ancillas + 1, dtype=int)
    x_boundary_node_idx = num_rounds * num_x_ancillas
    
    x_defect_vec[0 : num_rounds * num_x_ancillas] = x_defects.flatten()
    
    last_round_start_idx_x = (num_rounds - 1) * num_x_ancillas
    last_round_end_idx_x = num_rounds * num_x_ancillas
    x_defect_vec[last_round_start_idx_x : last_round_end_idx_x] ^= final_x_defects

    if np.sum(x_defect_vec) % 2 == 1:
        x_defect_vec[x_boundary_node_idx] = 1

    # 5-4. 디코딩 수행
    x_correction_fault_ids = x_matcher.decode(x_defect_vec)


    # --- 6. Apply Correction (PyMatching 결과로 수정됨) ---
    
    corrected_res_bits = np.array(res_bits)
    
    # Z-Graph (X-Error) Correction -> Flips res_bits
    # z_matcher.decode()가 반환한 fault_id(큐비트 인덱스) 세트를 순회합니다.
    for qubit_to_flip in z_correction_fault_ids:
        if qubit_to_flip is not None:
            corrected_res_bits[qubit_to_flip] = 1 - corrected_res_bits[qubit_to_flip]

    # X-Graph (Z-Error) Correction -> Flips the final_x_syndrome
    # 이전 로직과 동일하게, 최종 결함 상태에서 시작합니다.
    corrected_final_x_syndrome = np.array(final_x_defects) 
    
    # x_matcher.decode()가 반환한 fault_id(큐비트 인덱스) 세트를 순회합니다.
    for qubit_to_flip in x_correction_fault_ids:
        if qubit_to_flip is not None: 
            # 이 큐비트를 측정하는 모든 X-stabilizer를 찾습니다.
            for a_idx, data_qubits in enumerate(x_stabilizers.values()):
                if f'd[{qubit_to_flip}]' in data_qubits:
                    # 해당 신드롬 비트를 뒤집습니다.
                    corrected_final_x_syndrome[a_idx] = 1 - corrected_final_x_syndrome[a_idx]

    # --- 7. Error Reporting (변경 없음) ---
    
    no_error_injected = (injected_error_group == 'Data' and injected_data_flip_index is None) or \
                          (injected_error_group == 'Measurement' and injected_ancilla_flip_index is None)

    # 1. Recalculate Z-stabilizers with the *corrected* res_bits
    corrected_final_z_syndrome = calculate_syndrome_from_res(corrected_res_bits, z_stabilizers, num_z_ancillas)
    
    # 2. Check for Logical-X error
    logical_x_error_parity = corrected_res_bits[2] ^ corrected_res_bits[7] ^ corrected_res_bits[12]
    
    # 3. Detect Logical-X error
    logical_x_error_detected = any(corrected_final_z_syndrome) or (logical_x_error_parity == 1)
    
    # 4. Detect Logical-Z error
    logical_z_error_detected = any(corrected_final_x_syndrome)
    
    logical_error_detected = logical_x_error_detected or logical_z_error_detected
    
    # --- Debug Printing (PyMatching 변수를 사용하도록 수정됨) ---
    if enable_debug_printing and logical_error_detected:
        print("--- 🐞 DECODER INTERNAL DUMP (UE) 🐞 ---")
        
        injected_error_details = "None"
        if injected_error_group == 'Data' and injected_data_flip_index is not None:
            injected_error_details = f"Data d[{injected_data_flip_index}]"
        elif injected_error_group == 'Measurement' and injected_ancilla_flip_index is not None:
            injected_error_details = f"Meas (R0) Anc[{injected_ancilla_flip_index}]"
        print(f"DEBUG: Injected Error: {injected_error_details}")

        print(f"Parsed sx_bits (R0...R{num_rounds-1}): {sx_bits}")
        print(f"Parsed sz_bits (R0...R{num_rounds-1}): {sz_bits}")
        print(f"Parsed res_bits: {res_bits}")
        
        # PyMatching용 변수 출력
        print(f"X-Defect Vector (flat): {x_defect_vec}")
        print(f"Z-Defect Vector (flat): {z_defect_vec}")
        
        print(f"X-Correction (fault_ids): {x_correction_fault_ids}")
        print(f"Z-Correction (fault_ids): {z_correction_fault_ids}")
        
        print(f"Original res_bits: {np.array(res_bits)}")
        print(f"Corrected res_bits: {corrected_res_bits}")
        print(f"Corrected X-Syndrome: {corrected_final_x_syndrome} (Any={any(corrected_final_x_syndrome)})")
        print(f"Corrected Z-Syndrome: {corrected_final_z_syndrome} (Any={any(corrected_final_z_syndrome)})")
        print(f"Logical X Parity (Z_L): {logical_x_error_parity}")
        print(f"-> Result: logical_x_error: {logical_x_error_detected}, logical_z_error: {logical_z_error_detected}")
        print("---------------------------------------")
    # --- [END DEBUG] ---

    
    if no_error_injected and not logical_error_detected:
        return 'NE' # No Error
    elif not no_error_injected and not logical_error_detected:
        return 'CE' # Correctable Error
    elif logical_error_detected:
        return 'UE' # Uncorrectable Error
    else:
        return 'UE' 